"""Hybrid retrieval + cross-encoder reranking for the capstone.

Replaces W8's pure-dense retrieval with:
  1. Hybrid retrieval (BM25 + Dense via RRF) - top-10
  2. Cross-encoder reranking - top-3

Public API:
  hybrid_retrieve(query, k=10) -> list[dict]
  rerank(query, candidates, top_k=3) -> list[dict]
  retrieve(query, k=3) -> list[dict]   # full stack, use this from qdrant_rag.py
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

from openai import OpenAI
from rank_bm25 import BM25Okapi

from src.rag.qdrant_store import W9_COLLECTION_NAME, _get_client

# W10
from qdrant_client.models import Filter, IsEmptyCondition, PayloadField

# Cross-encoder lazy-init (heavy)
_reranker = None


def _get_reranker():
    global _reranker
    if _reranker is None:
        from sentence_transformers import CrossEncoder

        _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _reranker


_openai = None


def _get_openai():
    global _openai
    if _openai is None:
        _openai = OpenAI()
    return _openai


def simple_tokenize(text: str) -> list[str]:
    """Match W9 Day 1 tokenization: keeps hyphens/slashes in tokens.

    'AC-1042' stays as one token so BM25 can catch exact IDs.
    """
    return re.findall(r"[a-z0-9][a-z0-9\-/_]*", text.lower())


def _normalize_payload(payload: dict | None, point_id: str | int) -> dict:
    """Normalize W9 and legacy payload metadata for downstream RAG consumers."""
    if not payload:
        raise ValueError(f"Qdrant point {point_id!r} has no payload")
    doc = dict(payload)
    chunk_id = doc.get("chunk_id")
    source_id = (
        doc.get("source_id")
        or doc.get("section_path")
        or (Path(doc["source"]).stem if doc.get("source") else None)
    )
    if not chunk_id:
        raise ValueError(f"Qdrant point {point_id!r} is missing chunk_id metadata")
    if not source_id:
        raise ValueError(f"Qdrant point {point_id!r} is missing source metadata")
    if not isinstance(doc.get("text"), str):
        raise ValueError(f"Qdrant point {point_id!r} is missing text metadata")
    doc["chunk_id"] = str(chunk_id)
    doc["source_id"] = str(source_id)
    doc["point_id"] = point_id
    return doc


@lru_cache(maxsize=1)
def _load_bm25(collection_name: str):
    """Load ALL chunks from Qdrant, build BM25 index over their text.

    Cached — pays the cost once per process. For very large corpora
    (>10K chunks), persist this to disk instead. That's a W10 topic.
    """
    client = _get_client()
    all_points = []
    offset = None
    while True:
        batch, next_offset = client.scroll(
            collection_name=collection_name,
            limit=200,
            offset=offset,
            with_payload=True,
        )
        all_points.extend(batch)
        if next_offset is None:
            break
        offset = next_offset

    # Preserve order — index positions map to point ids
    corpus_meta = [_normalize_payload(p.payload, p.id) for p in all_points]
    corpus_texts = [doc["text"] for doc in corpus_meta]
    tokenized = [simple_tokenize(t) for t in corpus_texts]
    return BM25Okapi(tokenized), corpus_meta


def bm25_search(
    query: str, k: int = 10, *, collection_name: str = W9_COLLECTION_NAME
) -> list[dict]:
    """BM25 retrieval — top-K by score. Returns list of dicts with 'point_id'."""
    bm25, meta = _load_bm25(collection_name)
    scores = bm25.get_scores(simple_tokenize(query))
    ranked = sorted(zip(scores, meta), key=lambda p: p[0], reverse=True)
    return [
        {"id": str(m["point_id"]), "score": float(s), "doc": m} for s, m in ranked[:k]
    ]


def dense_search_w9(
    query: str,
    k: int = 10,
    *,
    usage: dict[str, int] | None = None,
    collection_name: str = W9_COLLECTION_NAME,
) -> list[dict]:
    """Dense retrieval — Qdrant cosine top-K."""
    openai = _get_openai()
    client = _get_client()
    response = openai.embeddings.create(model="text-embedding-3-small", input=[query])
    q_vec = response.data[0].embedding
    if usage is not None:
        if response.usage is None:
            raise RuntimeError("Embedding response did not include token usage")
        usage["embedding_tokens"] = response.usage.prompt_tokens
    hits = client.query_points(
        collection_name=collection_name, query=q_vec, limit=k
    ).points
    return [
        {
            "id": str(h.id),
            "score": h.score,
            "doc": _normalize_payload(h.payload, h.id),
        }
        for h in hits
    ]


def rrf_fuse(
    ranked_lists: list[list[dict]], k: int = 60, top_n: int = 10
) -> list[dict]:
    """Reciprocal Rank Fusion — same as W9 Day 1."""
    scores = {}
    docs = {}
    for ranked in ranked_lists:
        for rank, hit in enumerate(ranked, start=1):
            doc_id = hit["id"]
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
            if doc_id not in docs:
                docs[doc_id] = hit
    fused = sorted(scores.items(), key=lambda p: p[1], reverse=True)[:top_n]
    return [{**docs[doc_id], "rrf_score": s} for doc_id, s in fused]


def hybrid_retrieve(
    query: str,
    k_per_retriever: int = 10,
    k_final: int = 10,
    *,
    usage: dict[str, int] | None = None,
    collection_name: str = W9_COLLECTION_NAME,
) -> list[dict]:
    """BM25 + Dense + RRF combined."""
    bm25_hits = bm25_search(query, k=k_per_retriever, collection_name=collection_name)
    dense_hits = dense_search(
        query,
        k=k_per_retriever,
        usage=usage,
        collection_name=collection_name,
    )
    return rrf_fuse([bm25_hits, dense_hits], k=60, top_n=k_final)


def rerank(query: str, candidates: list[dict], top_k: int = 3) -> list[dict]:
    """Cross-encoder reranking — score (query, candidate.text) pairs."""
    reranker = _get_reranker()
    pairs = [(query, c["doc"].get("text", "")) for c in candidates]
    scores = reranker.predict(pairs)
    scored = [{**c, "rerank_score": float(s)} for c, s in zip(candidates, scores)]
    scored.sort(key=lambda h: h["rerank_score"], reverse=True)
    return scored[:top_k]


def retrieve(
    query: str,
    k: int = 3,
    *,
    usage: dict[str, int] | None = None,
    collection_name: str = W9_COLLECTION_NAME,
) -> list[dict]:
    """Full W9 stack: hybrid → rerank → top-k. Use this from qdrant_rag.py."""
    candidates = hybrid_retrieve(
        query,
        k_per_retriever=10,
        k_final=10,
        usage=usage,
        collection_name=collection_name,
    )
    return rerank(query, candidates, top_k=k)


def _live_filter():
    """Filter matching only not-yet-tombstoned chunks."""
    return Filter(must=[IsEmptyCondition(is_empty=PayloadField(key="deleted_at"))])


def dense_search(
    query: str,
    k: int = 10,
    include_deleted: bool = False,
    *,
    usage: dict[str, int] | None = None,
    collection_name: str = W9_COLLECTION_NAME,
) -> list[dict]:
    """Dense retrieval with tombstone filter by default.

    include_deleted=True is the audit escape hatch — use only when
    re-running historical evaluations against past KB state.
    """
    openai = _get_openai()
    client = _get_client()
    response = openai.embeddings.create(
        model="text-embedding-3-small", input=[query]
    )
    q_vec = response.data[0].embedding
    if usage is not None:
        if response.usage is None:
            raise RuntimeError("Embedding response did not include token usage")
        usage["embedding_tokens"] = response.usage.prompt_tokens

    query_filter = None if include_deleted else _live_filter()
    hits = client.query_points(
        collection_name=collection_name,
        query=q_vec,
        limit=k,
        query_filter=query_filter,
    ).points
    return [
        {
            "id": str(h.id),
            "score": h.score,
            "doc": _normalize_payload(h.payload, str(h.id)),
        }
        for h in hits
    ]
