"""Qdrant-backed RAG for the capstone — W7 upgrade of W6's naive_rag.

Same public interface as W6's ask_rag: (question, store, k) → dict.
Storage layer swapped from JSON+numpy to Qdrant.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from openai import OpenAI

from src.pipeline.cost import compute_cost_usd
from src.pipeline.settings import Settings
from src.rag.qdrant_store import QdrantStore, W9_COLLECTION_NAME, _get_client

from src.rag.retrieval import retrieve as retrieve_v9  # Week9
from src.rag import cache  # NEW W10


def load_store():
    """Load a store pointing at the v2 collection."""
    return QdrantStore(client=_get_client(), collection=W9_COLLECTION_NAME)


CHAT_MODEL = "gpt-4o-mini"
EMBED_MODEL = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_COST_PER_MILLION = {
    "text-embedding-3-small": 0.02,
    "text-embedding-3-large": 0.13,
}

_client = None


def _openai() -> OpenAI:
    """Lazy-init the OpenAI client (unit tests can import without a key)."""
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def _embed_query_with_usage(text: str) -> tuple[list[float], int]:
    resp = _openai().embeddings.create(model=EMBED_MODEL, input=[text])
    return resp.data[0].embedding, resp.usage.prompt_tokens


def embed_query(text: str) -> list[float]:
    """Single-string embedding. Used at query time."""
    return _embed_query_with_usage(text)[0]


def retrieve(
    store: QdrantStore,
    query: str,
    k: int = 3,
    *,
    usage: dict[str, int] | None = None,
) -> list[dict[str, Any]]:
    """Embed the query, ask Qdrant for top-K, return list of hits."""
    q_vec, embedding_tokens = _embed_query_with_usage(query)
    if usage is not None:
        usage["embedding_tokens"] = embedding_tokens
    results = store.client.query_points(
        collection_name=store.collection,
        query=q_vec,
        limit=k,
    ).points
    hits = []
    for hit in results:
        payload = hit.payload or {}
        source_id = (
            payload.get("source_id")
            or payload.get("section_path")
            or Path(payload["source"]).stem
        )
        hits.append(
            {
                "chunk_id": payload["chunk_id"],
                "source_id": source_id,
                "text": payload["text"],
                "score": hit.score,
            }
        )
    return hits


SYSTEM = (
    "You are a helpful assistant. Answer the user's question using ONLY the "
    "provided context. If the context does not contain the answer, say so "
    "plainly. Cite the source_id in square brackets after any fact you use."
)


def ask_rag(
    question: str,
    store: QdrantStore | None = None,
    settings: Settings | None = None,
    k: int = 3,
    cache_threshold: float = 0.95,
) -> dict[str, Any]:
    """Full pipeline: embed → retrieve → prompt → generate. Returns dict."""

    # W10
    """Full RAG with 3-layer caching.

    Layer 1 (semantic cache) checked first — return early on hit.
    Layer 2 (OpenAI prompt cache) fires automatically on the LLM call.
    Layer 3 (embedding cache) transparent from W7.
    """
    if store is None:
        store = load_store()

    usage: dict[str, int] = {}
    # retrieved = retrieve(store, question, k=k, usage=usage) # OLD (W8)

    client = _openai()

    # ── Layer 1: semantic cache ──
    q_vec = (
        client.embeddings.create(model="text-embedding-3-small", input=[question])
        .data[0]
        .embedding
    )

    hit = cache.lookup(q_vec, threshold=cache_threshold)
    if hit:
        return {
            "answer": hit["answer"],
            "cache_hit": True,
            "similarity": hit["similarity"],
            "matched": hit["matched_question"],
        }

    # ── Miss: full RAG pipeline ──
    retrieved = retrieve_v9(
        question,
        k=k,
        usage=usage,
        collection_name=store.collection,
    )

    # Commented as part of W10 cache changes
    # retrieved_docs = [hit["doc"] for hit in retrieved]

    # context = "\n\n".join(
    #     f"[{doc['chunk_id']}] (source: {doc['source_id']})\n{doc['text']}"
    #     for doc in retrieved_docs
    # )

    # resp = _openai().chat.completions.create(
    #     model=CHAT_MODEL,
    #     temperature=0.0,
    #     messages=[
    #         {"role": "system", "content": SYSTEM},
    #         {
    #             "role": "user",
    #             "content": f"Context:\n{context}\n\n---\n\nQuestion: {question}",
    #         },
    #     ],
    # )

    prompt = _build_prompt(question, retrieved)

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.1,
        messages=[{"role": "user", "content": prompt}],
    )
    answer = resp.choices[0].message.content

    # Store in cache for next time
    cache.put(question, q_vec, answer)

    return {
        "answer": answer,
        "cache_hit": False,
        "n_input_tokens": resp.usage.prompt_tokens,
        "n_output_tokens": resp.usage.completion_tokens,
        "n_cached_input_tokens": getattr(resp.usage, "prompt_tokens_details", None)
        and resp.usage.prompt_tokens_details.cached_tokens
        or 0,
        "retrieved": retrieved,
    }


def _build_prompt(question: str, retrieved: list[dict]) -> str:
    """Stable prefix FIRST (cacheable), question + context LAST."""
    system = (
        "You are a helpful assistant. Answer using ONLY the context. "
        "If the context does not contain the answer, say 'I don't know'."
    )
    ctx = "\n\n".join(
        f"[{i+1}] {h['doc'].get('text', '')}" for i, h in enumerate(retrieved)
    )
    return f"{system}\n\n=== Context ===\n{ctx}\n\n=== Question ===\n{question}\n\n=== Answer ==="


def ask_rag_w9(
    question: str,
    store: QdrantStore | None = None,
    settings: Settings | None = None,
    k: int = 3,
) -> dict[str, Any]:
    """Full pipeline: embed → retrieve → prompt → generate. Returns dict."""
    if store is None:
        store = load_store()

    usage: dict[str, int] = {}
    # retrieved = retrieve(store, question, k=k, usage=usage) # OLD (W8)

    retrieved = retrieve_v9(
        question,
        k=k,
        usage=usage,
        collection_name=store.collection,
    )
    retrieved_docs = [hit["doc"] for hit in retrieved]

    context = "\n\n".join(
        f"[{doc['chunk_id']}] (source: {doc['source_id']})\n{doc['text']}"
        for doc in retrieved_docs
    )

    resp = _openai().chat.completions.create(
        model=CHAT_MODEL,
        temperature=0.0,
        messages=[
            {"role": "system", "content": SYSTEM},
            {
                "role": "user",
                "content": f"Context:\n{context}\n\n---\n\nQuestion: {question}",
            },
        ],
    )

    prompt_tokens = resp.usage.prompt_tokens
    completion_tokens = resp.usage.completion_tokens
    embedding_tokens = usage["embedding_tokens"]
    cost_usd = (
        compute_cost_usd(CHAT_MODEL, prompt_tokens, completion_tokens)
        + embedding_tokens
        * EMBEDDING_COST_PER_MILLION.get(EMBED_MODEL, 0.0)
        / 1_000_000
    )

    return {
        "answer": resp.choices[0].message.content,
        "sources": [doc["source_id"] for doc in retrieved_docs],
        "chunk_ids": [doc["chunk_id"] for doc in retrieved_docs],
        "candidate_model": CHAT_MODEL,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "embedding_tokens": embedding_tokens,
        "cost_usd": cost_usd,
    }
