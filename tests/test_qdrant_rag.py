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
    client = SimpleNamespace(
        embeddings=SimpleNamespace(
            create=lambda **_kwargs: SimpleNamespace(
                data=[SimpleNamespace(embedding=[0.1, 0.2])],
                usage=SimpleNamespace(prompt_tokens=4),
            )
        ),
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **_kwargs: SimpleNamespace(
                    choices=[
                        SimpleNamespace(
                            message=SimpleNamespace(content="Grounded answer")
                        )
                    ],
                    usage=SimpleNamespace(prompt_tokens=10, completion_tokens=2),
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

    result = qdrant_rag.ask_rag(
        "How much leave?", store=QdrantStore(store_client, "policies")
    )

    expected_cost = compute_cost_usd("gpt-4o-mini", 10, 2) + 4 * 0.02 / 1_000_000
    assert result["cost_usd"] == expected_cost
    assert result["candidate_model"] == "gpt-4o-mini"
    assert result["prompt_tokens"] == 10
    assert result["completion_tokens"] == 2
    assert result["embedding_tokens"] == 4


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
