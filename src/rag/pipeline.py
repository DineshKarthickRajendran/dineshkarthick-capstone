import time
import uuid
from pathlib import Path

from openai import OpenAI
from qdrant_client.models import (
    FieldCondition,
    Filter,
    IsEmptyCondition,  # NOT IsNullCondition
    MatchValue,
    PayloadField,
    PayloadSchemaType,
    PointStruct,
)
from src.rag import cache

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536
EMBEDDING_BATCH_SIZE = 100
KB_VERSION = "v1"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


_client = None


def _openai() -> OpenAI:
    """Lazy-init the OpenAI client (unit tests can import without a key)."""
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def _ensure_payload_index(
    store, field_name: str, field_schema: PayloadSchemaType
) -> None:
    payload_schema = store.client.get_collection(store.collection).payload_schema or {}
    index = payload_schema.get(field_name)
    if index is None:
        store.client.create_payload_index(
            collection_name=store.collection,
            field_name=field_name,
            field_schema=field_schema,
            wait=True,
        )
    elif index.data_type != field_schema:
        raise ValueError(
            f"Qdrant payload index for {field_name!r} must be {field_schema}, "
            f"not {index.data_type!r}"
        )


def tombstone_source(store, source: str) -> int:
    """Mark all live chunks whose payload.source == source as tombstoned.

    Uses IsEmptyCondition — matches whether deleted_at is absent, null, or
    empty. IsNullCondition would only match explicit-null values and misses
    absent fields (silent bug). See W10 Day 2 Cell 4 for the diagnosis.

    Returns count of chunks tombstoned.
    """
    _ensure_payload_index(store, "source", PayloadSchemaType.KEYWORD)
    _ensure_payload_index(store, "deleted_at", PayloadSchemaType.FLOAT)

    flt = Filter(
        must=[
            FieldCondition(key="source", match=MatchValue(value=source)),
            IsEmptyCondition(is_empty=PayloadField(key="deleted_at")),
        ]
    )
    pre_count = store.client.count(
        collection_name=store.collection,
        count_filter=flt,
        exact=True,
    ).count
    store.client.set_payload(
        collection_name=store.collection,
        payload={"deleted_at": time.time()},
        points=flt,
        wait=True,
    )
    return pre_count


def ingest_or_update_source(
    store,
    source: str,
    body: str,
    doc_type: str = "general",
    clear_cache_after: bool = True,
) -> dict:
    """Re-ingest a document. Tombstone old chunks, insert new ones, clear cache.

    Returns {tombstoned, ingested, cache_cleared}.

    The clear_cache_after flag defaults True — critical to prevent stale
    answers from the semantic cache after a doc update. Turn off only if
    you're doing bulk updates and will call cache.clear() once at the end.
    """
    n_tombstoned = tombstone_source(store, source)

    source_id = Path(source).stem
    chunks = [
        {
            "chunk_id": f"{source_id}#{idx}",
            "source_id": source_id,
            "text": chunk,
        }
        for idx, chunk in enumerate(chunk_text(body))
    ]
    vectors = embed_texts([c["text"] for c in chunks])

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vec,
            payload={
                **chunk,
                "source": source,
                "doc_type": doc_type,
                "kb_version": KB_VERSION,
                "ingested_at": time.time(),
                # NOTE: deliberately no deleted_at field. IsEmptyCondition
                # will match this — no explicit None needed.
            },
        )
        for chunk, vec in zip(chunks, vectors)
    ]
    store.client.upsert(collection_name=store.collection, points=points, wait=True)

    n_cleared = 0
    if clear_cache_after:
        n_cleared = cache.clear()

    return {
        "tombstoned": n_tombstoned,
        "ingested": len(points),
        "cache_cleared": n_cleared,
    }


def chunk_text(
    text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP
) -> list[str]:
    """Split text using the same sliding-window pattern as naive_rag.chunk_text."""
    if len(text) <= size:
        return [text]
    chunks = []
    i = 0
    while i < len(text):
        end = min(i + size, len(text))
        chunks.append(text[i:end])
        if end == len(text):
            break
        i = end - overlap
    return chunks


# ─── Step 3: Embed text ─────────────────────────────────────────────────


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Batch-embed a list of texts using OpenAI's embedding model.

    Returns a list of 1536-dim float vectors (same order as inputs).

    """
    embeddings: list[list[float]] = []
    for start in range(0, len(texts), EMBEDDING_BATCH_SIZE):
        batch = texts[start : start + EMBEDDING_BATCH_SIZE]
        response = _openai().embeddings.create(model=EMBEDDING_MODEL, input=batch)
        embeddings.extend(
            item.embedding
            for item in sorted(response.data, key=lambda item: item.index)
        )
    return embeddings
