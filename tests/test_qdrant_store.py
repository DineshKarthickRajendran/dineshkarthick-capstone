from types import SimpleNamespace

import pytest

from src.rag.qdrant_store import QdrantStore, upsert_chunks


@pytest.mark.parametrize(
    ("chunk", "expected_source"),
    [
        (
            {"chunk_id": "leave#0", "source_id": "leave", "text": "policy"},
            "leave",
        ),
        (
            {
                "chunk_id": "leave#0",
                "source": "leave.md",
                "section_path": "leave",
                "text": "policy",
            },
            "leave",
        ),
    ],
)
def test_upsert_supports_legacy_and_ingestion_chunk_metadata(chunk, expected_source):
    captured = {}
    client = SimpleNamespace(upsert=lambda **kwargs: captured.update(kwargs))
    store = QdrantStore(client=client, collection="policies")

    upsert_chunks(store, [chunk], [[0.1, 0.2]])

    assert captured["collection_name"] == "policies"
    assert captured["points"][0].payload["source_id"] == expected_source
    assert captured["points"][0].payload["text"] == "policy"


def test_upsert_reports_missing_source_metadata():
    store = QdrantStore(client=SimpleNamespace(), collection="policies")

    with pytest.raises(ValueError, match="missing source_id and section_path"):
        upsert_chunks(
            store,
            [{"chunk_id": "unknown#0", "text": "policy"}],
            [[0.1, 0.2]],
        )
