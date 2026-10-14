"""Qdrant-backed RAG for the capstone — W7 upgrade of W6's naive_rag.

Same public interface as W6's ask_rag: (question, store, k) → dict.
Storage layer swapped from JSON+numpy to Qdrant.
"""

from __future__ import annotations

from typing import Any

from openai import OpenAI

from src.pipeline.cost import compute_cost_usd
from src.pipeline.settings import Settings
from src.rag.qdrant_store import EMBEDDING_MODEL, QdrantStore, load_store

CHAT_MODEL = "gpt-4o-mini"
EMBED_MODEL = EMBEDDING_MODEL
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
    return [
        {
            "chunk_id": h.payload["chunk_id"],
            "source_id": h.payload["source_id"],
            "text": h.payload["text"],
            "score": h.score,
        }
        for h in results
    ]


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
) -> dict[str, Any]:
    """Full pipeline: embed → retrieve → prompt → generate. Returns dict."""
    if store is None:
        store = load_store()

    usage: dict[str, int] = {}
    retrieved = retrieve(store, question, k=k, usage=usage)

    context = "\n\n".join(
        f"[{hit['chunk_id']}] (source: {hit['source_id']})\n{hit['text']}"
        for hit in retrieved
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
        "sources": [h["source_id"] for h in retrieved],
        "chunk_ids": [h["chunk_id"] for h in retrieved],
        "candidate_model": CHAT_MODEL,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "embedding_tokens": embedding_tokens,
        "cost_usd": cost_usd,
    }
