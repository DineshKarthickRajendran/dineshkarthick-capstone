"""Qdrant vector store for the capstone.

Replaces W6's naive_rag.py in-memory list + JSON cache with a real
vector database. Same public interface — different engine underneath.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    HnswConfigDiff,
)

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMS = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
}
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
COLLECTION_NAME = os.environ.get("QDRANT_COLLECTION", "capstone_chunks")
EMBEDDING_DIM = EMBEDDING_DIMS.get(EMBEDDING_MODEL, 1536)


@dataclass
class QdrantStore:
    """Wraps a Qdrant client + a collection name.

    Convention: one QdrantStore instance per running app.
    Instantiate via load_store() below.
    """

    client: QdrantClient
    collection: str


def _get_client() -> QdrantClient:
    """Build a QdrantClient using QDRANT_URL + QDRANT_API_KEY env vars.

    Resolution order (matches the W7 lesson plan):
      1. QDRANT_URL + QDRANT_API_KEY → Qdrant Cloud
      2. QDRANT_URL only → local Docker
      3. Default → http://localhost:6333
    """
    url = os.environ.get("QDRANT_URL", "http://localhost:6333")
    api_key = os.environ.get("QDRANT_API_KEY") or None
    print(f"Qdrant config url={url} api_key={'<redacted>' if api_key else '<not set>'}")
    if api_key:
        return QdrantClient(url=url, api_key=api_key)
    return QdrantClient(url=url)


def load_store(collection_name: str | None = None) -> QdrantStore:
    """Return a QdrantStore pointing at the capstone_chunks collection."""
    return QdrantStore(
        client=_get_client(), collection=collection_name or COLLECTION_NAME
    )


def ensure_collection(store: QdrantStore) -> None:
    """Create the capstone_chunks collection if it doesn't exist.

    Idempotent — safe to call on every app start.
    """
    existing = [c.name for c in store.client.get_collections().collections]
    if store.collection in existing:
        return
    store.client.create_collection(
        collection_name=store.collection,
        vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
    )


def upsert_chunks(
    store: QdrantStore, chunks: list[dict], vectors: list[list[float]]
) -> None:
    """Push (chunk, vector) pairs into the store.

    Each chunk is a dict with 'chunk_id', 'source_id', and 'text' keys
    (matches the shape produced by W6's naive_rag.load_corpus).
    """

    points = [
        PointStruct(
            id=idx,
            vector=vec,
            # payload={
            #     "chunk_id": chunk["chunk_id"],
            #     "source_id": chunk["source_id"],
            #     "text": chunk["text"],
            # },
            payload={
                k: v for k, v in chunk.items() if k != "vector"
            },  # Added in W8 richer payload
        )
        for idx, (chunk, vec) in enumerate(zip(chunks, vectors))
    ]
    store.client.upsert(collection_name=store.collection, points=points)


# def upsert_chunks(
#     store: QdrantStore, chunks: list[dict], vectors: list[list[float]]
# ) -> None:
#     """Push (chunk, vector) pairs into the store.

#     Accept both W6's {chunk_id, source_id, text} shape and the ingestion
#     pipeline's enriched metadata shape, where section_path identifies source.
#     """
#     points = []
#     for idx, (chunk, vec) in enumerate(zip(chunks, vectors)):
#         source_id = chunk.get("source_id") or chunk.get("section_path")
#         if not source_id:
#             raise ValueError(
#                 f"Chunk {chunk.get('chunk_id', idx)!r} is missing source_id "
#                 "and section_path metadata"
#             )
#         points.append(
#             PointStruct(
#                 id=idx,
#                 vector=vec,
#                 payload={
#                     "chunk_id": chunk["chunk_id"],
#                     "source_id": source_id,
#                     "text": chunk["text"],
#                 },
#             )
#         )
#     store.client.upsert(collection_name=store.collection, points=points)


def collection_size(store: QdrantStore) -> int:
    """Return the number of points in the collection. Used for smoke tests."""
    info = store.client.get_collection(store.collection)
    return info.points_count


"""You already have qdrant_store.py from W7. It handles capstone_chunks. 
For W8, you need it to also handle capstone_chunks_v2 with the enriched payload."""


def upsert_chunks_v2(
    store: QdrantStore, chunks: list[dict], vectors: list[list[float]]
) -> None:
    """Upsert with the full 9-field metadata payload from W8's pipeline.

    chunks[i] is a dict with keys: chunk_id, source, doc_type, section_path,
    page, date, language, version, ingested_at, text, pii_flags_count.
    """
    from qdrant_client.models import PointStruct

    points = [
        PointStruct(id=idx, vector=vec, payload=chunk)
        for idx, (chunk, vec) in enumerate(zip(chunks, vectors))
    ]
    store.client.upsert(collection_name=store.collection, points=points)
