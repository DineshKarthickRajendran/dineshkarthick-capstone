from types import SimpleNamespace

from src.pipeline.cost import compute_cost_usd
from src.rag import qdrant_rag
from src.rag.qdrant_store import (
    DEFAULT_EMBEDDING_MODEL,
    EMBEDDING_MODEL,
    QdrantStore,
)


def test_qdrant_embedding_defaults_to_small():
    assert DEFAULT_EMBEDDING_MODEL == "text-embedding-3-small"
    assert EMBEDDING_MODEL == qdrant_rag.EMBED_MODEL


def test_ask_rag_reports_chat_and_embedding_cost(monkeypatch):
    chat_request = {}
    client = SimpleNamespace(
        embeddings=SimpleNamespace(
            create=lambda **_kwargs: SimpleNamespace(
                data=[SimpleNamespace(embedding=[0.1, 0.2])],
                usage=SimpleNamespace(prompt_tokens=4),
            )
        ),
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **kwargs: (
                    chat_request.update(kwargs)
                    or SimpleNamespace(
                        choices=[
                            SimpleNamespace(
                                message=SimpleNamespace(content="Grounded answer")
                            )
                        ],
                        usage=SimpleNamespace(
                            prompt_tokens=10, completion_tokens=2
                        ),
                    )
                )
            )
        ),
    )
    store_client = SimpleNamespace(
        query_points=lambda **_kwargs: SimpleNamespace(
            points=[
                SimpleNamespace(
                    payload={
                        "chunk_id": "leave#0",
                        "source_id": "leave",
                        "text": "Leave policy text",
                    },
                    score=0.9,
                )
            ]
        )
    )
    monkeypatch.setattr(qdrant_rag, "_client", client)

    def fake_retrieve_v9(_question, *, k, usage, collection_name):
        assert collection_name == "policies"
        usage["embedding_tokens"] = 4
        return [
            {
                "doc": {
                    "chunk_id": "leave#0",
                    "source_id": "leave",
                    "text": "Leave policy text",
                }
            }
        ]

    monkeypatch.setattr(qdrant_rag, "retrieve_v9", fake_retrieve_v9)

    result = qdrant_rag.ask_rag(
        "How much leave?", store=QdrantStore(store_client, "policies")
    )

    expected_cost = compute_cost_usd("gpt-4o-mini", 10, 2) + 4 * 0.02 / 1_000_000
    assert result["cost_usd"] == expected_cost
    assert result["candidate_model"] == "gpt-4o-mini"
    assert result["prompt_tokens"] == 10
    assert result["completion_tokens"] == 2
    assert result["embedding_tokens"] == 4
    assert result["sources"] == ["leave"]
    assert result["chunk_ids"] == ["leave#0"]
    assert "[leave#0] (source: leave)\nLeave policy text" in chat_request[
        "messages"
    ][1]["content"]


def test_ask_rag_can_bypass_semantic_cache(monkeypatch):
    def unexpected_cache_call(*_args, **_kwargs):
        raise AssertionError("cache should not be read or written during evaluation")

    client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **_kwargs: SimpleNamespace(
                    choices=[
                        SimpleNamespace(
                            message=SimpleNamespace(content="Fresh answer")
                        )
                    ],
                    usage=SimpleNamespace(prompt_tokens=10, completion_tokens=2),
                )
            )
        )
    )
    monkeypatch.setattr(qdrant_rag, "_client", client)
    monkeypatch.setattr(qdrant_rag.cache, "lookup", unexpected_cache_call)
    monkeypatch.setattr(qdrant_rag.cache, "put", unexpected_cache_call)
    monkeypatch.setattr(
        qdrant_rag,
        "retrieve_v9",
        lambda _question, *, k, usage, collection_name: [
            {"doc": {"text": "Policy context"}}
        ],
    )

    result = qdrant_rag.ask_rag(
        "How much leave?",
        store=QdrantStore(SimpleNamespace(), "policies"),
        use_cache=False,
    )

    assert result["answer"] == "Fresh answer"
    assert result["cache_hit"] is False


def test_ask_rag_refreshes_cache_without_reading_it(monkeypatch):
    cache_writes = []
    client = SimpleNamespace(
        embeddings=SimpleNamespace(
            create=lambda **_kwargs: SimpleNamespace(
                data=[SimpleNamespace(embedding=[0.1, 0.2])]
            )
        ),
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **_kwargs: SimpleNamespace(
                    choices=[
                        SimpleNamespace(
                            message=SimpleNamespace(content="Fresh answer")
                        )
                    ],
                    usage=SimpleNamespace(prompt_tokens=10, completion_tokens=2),
                )
            )
        ),
    )

    def unexpected_lookup(*_args, **_kwargs):
        raise AssertionError("refresh should not read the old cache entry")

    monkeypatch.setattr(qdrant_rag, "_client", client)
    monkeypatch.setattr(qdrant_rag.cache, "lookup", unexpected_lookup)
    monkeypatch.setattr(
        qdrant_rag.cache,
        "put",
        lambda question, embedding, answer: cache_writes.append(
            (question, embedding, answer)
        ),
    )
    monkeypatch.setattr(
        qdrant_rag,
        "retrieve_v9",
        lambda _question, *, k, usage, collection_name: [
            {"doc": {"text": "Policy context"}}
        ],
    )

    result = qdrant_rag.ask_rag(
        "How much leave?",
        store=QdrantStore(SimpleNamespace(), "policies"),
        refresh_cache=True,
    )

    assert result["answer"] == "Fresh answer"
    assert result["cache_hit"] is False
    assert cache_writes == [("How much leave?", [0.1, 0.2], "Fresh answer")]


def test_retrieve_accepts_w8_ingestion_payload(monkeypatch):
    monkeypatch.setattr(
        qdrant_rag,
        "_embed_query_with_usage",
        lambda _query: ([0.1, 0.2], 3),
    )
    client = SimpleNamespace(
        query_points=lambda **_kwargs: SimpleNamespace(
            points=[
                SimpleNamespace(
                    payload={
                        "chunk_id": "01_leave_policy#0",
                        "source": "01_leave_policy.md",
                        "section_path": "01_leave_policy",
                        "text": "Leave policy text",
                        "pii_flags_count": 0,
                    },
                    score=0.8,
                )
            ]
        )
    )
    usage = {}

    hits = qdrant_rag.retrieve(
        QdrantStore(client, "capstone_chunks_v2"), "leave?", usage=usage
    )

    assert hits == [
        {
            "chunk_id": "01_leave_policy#0",
            "source_id": "01_leave_policy",
            "text": "Leave policy text",
            "score": 0.8,
        }
    ]
    assert usage["embedding_tokens"] == 3


def test_w9_dense_search_reports_embedding_usage(monkeypatch):
    from src.rag import retrieval

    observed = {}
    monkeypatch.setattr(
        retrieval,
        "_get_openai",
        lambda: SimpleNamespace(
            embeddings=SimpleNamespace(
                create=lambda **_kwargs: SimpleNamespace(
                    data=[SimpleNamespace(embedding=[0.1, 0.2])],
                    usage=SimpleNamespace(prompt_tokens=7),
                )
            )
        ),
    )
    monkeypatch.setattr(
        retrieval,
        "_get_client",
        lambda: SimpleNamespace(
            query_points=lambda **kwargs: (
                observed.update(kwargs)
                or SimpleNamespace(
                    points=[
                        SimpleNamespace(
                            id=1,
                            score=0.9,
                            payload={
                                "chunk_id": "leave#0",
                                "section_path": "leave",
                                "text": "Leave policy text",
                            },
                        )
                    ]
                )
            )
        ),
    )
    usage = {}

    hits = retrieval.dense_search("leave?", k=1, usage=usage)

    assert hits[0]["doc"]["chunk_id"] == "leave#0"
    assert hits[0]["doc"]["source_id"] == "leave"
    assert usage["embedding_tokens"] == 7
    assert observed["collection_name"] == retrieval.W9_COLLECTION_NAME


def test_bm25_search_uses_requested_collection(monkeypatch):
    from src.rag import retrieval

    observed = {}

    class FakeBM25:
        def get_scores(self, _query):
            return [1.0]

    monkeypatch.setattr(
        retrieval,
        "_load_bm25",
        lambda collection_name: (
            observed.update(collection_name=collection_name) or FakeBM25(),
            [{"point_id": 7, "chunk_id": "leave#0", "text": "leave policy"}],
        ),
    )

    hits = retrieval.bm25_search("leave", collection_name="policies-v9")

    assert hits[0]["doc"]["chunk_id"] == "leave#0"
    assert observed["collection_name"] == "policies-v9"


def test_hybrid_retrieve_keeps_query_first_api(monkeypatch):
    from src.rag import retrieval

    calls = []
    hit = {"id": "leave#0", "score": 1.0, "doc": {"text": "leave policy"}}
    monkeypatch.setattr(
        retrieval,
        "bm25_search",
        lambda query, **kwargs: calls.append(("bm25", query, kwargs)) or [hit],
    )
    monkeypatch.setattr(
        retrieval,
        "dense_search",
        lambda query, **kwargs: calls.append(("dense", query, kwargs)) or [hit],
    )

    results = retrieval.hybrid_retrieve(
        "leave", k_per_retriever=2, k_final=1, collection_name="policies"
    )

    assert [call[0] for call in calls] == ["bm25", "dense"]
    assert all(call[1] == "leave" for call in calls)
    assert all(call[2]["k"] == 2 for call in calls)
    assert all(call[2]["collection_name"] == "policies" for call in calls)
    assert results[0]["id"] == "leave#0"


def test_chunk_backed_hybrid_retrieval_loads_live_chunks_and_builds_bm25(monkeypatch):
    from src.rag import retrieval

    points = [
        SimpleNamespace(
            id=1,
            payload={
                "chunk_id": "leave#0",
                "source_id": "leave",
                "text": "Employees receive paid leave each year.",
            },
        ),
        SimpleNamespace(
            id=2,
            payload={
                "chunk_id": "remote#0",
                "source_id": "remote",
                "text": "Remote work requires manager approval.",
            },
        ),
    ]
    scroll_calls = []
    query_calls = []

    class FakeClient:
        def scroll(self, **kwargs):
            scroll_calls.append(kwargs)
            if kwargs["offset"] is None:
                return [points[0]], 1
            return [points[1]], None

        def query_points(self, **kwargs):
            query_calls.append(kwargs)
            return SimpleNamespace(
                points=[SimpleNamespace(id=1, score=0.9, payload=points[0].payload)]
            )

    store = QdrantStore(FakeClient(), "policies")
    chunks = retrieval.load_chunks_from_qdrant(store)
    bm25 = retrieval.build_bm25_index(chunks)
    monkeypatch.setattr(
        retrieval,
        "_get_openai",
        lambda: SimpleNamespace(
            embeddings=SimpleNamespace(
                create=lambda **_kwargs: SimpleNamespace(
                    data=[SimpleNamespace(embedding=[0.1, 0.2])],
                    usage=SimpleNamespace(prompt_tokens=3),
                )
            )
        ),
    )
    usage = {}

    hits = retrieval.hybrid_retrieve_preloaded(
        store, bm25, chunks, "paid leave", top_k=1, usage=usage
    )

    assert [chunk["chunk_id"] for chunk in chunks] == ["leave#0", "remote#0"]
    assert chunks[0]["point_id"] == "1"
    assert len(scroll_calls) == 2
    assert all(call["scroll_filter"] is not None for call in scroll_calls)
    assert hits[0]["chunk_id"] == "leave#0"
    assert query_calls[0]["collection_name"] == "policies"
    assert query_calls[0]["query_filter"] is not None
    assert usage["embedding_tokens"] == 3
