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
