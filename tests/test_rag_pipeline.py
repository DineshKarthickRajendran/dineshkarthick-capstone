from types import SimpleNamespace

import pytest

from src.rag import pipeline
from src.rag.naive_rag import load_corpus


def test_tombstone_source_creates_required_indexes_before_filtering():
    calls = []
    client = SimpleNamespace(
        get_collection=lambda _collection: SimpleNamespace(payload_schema={}),
        create_payload_index=lambda **kwargs: calls.append(("create_index", kwargs)),
        count=lambda **kwargs: (
            calls.append(("count", kwargs)) or SimpleNamespace(count=2)
        ),
        set_payload=lambda **kwargs: calls.append(("set_payload", kwargs)),
    )
    store = SimpleNamespace(client=client, collection="policies")

    assert pipeline.tombstone_source(store, "leave.md") == 2
    assert [name for name, _ in calls] == [
        "create_index",
        "create_index",
        "count",
        "set_payload",
    ]
    assert calls[:2] == [
        (
            "create_index",
            {
                "collection_name": "policies",
                "field_name": "source",
                "field_schema": pipeline.PayloadSchemaType.KEYWORD,
                "wait": True,
            },
        ),
        (
            "create_index",
            {
                "collection_name": "policies",
                "field_name": "deleted_at",
                "field_schema": pipeline.PayloadSchemaType.FLOAT,
                "wait": True,
            },
        ),
    ]


@pytest.mark.parametrize(
    ("field_name", "field_schema"),
    [
        ("source", pipeline.PayloadSchemaType.TEXT),
        ("deleted_at", pipeline.PayloadSchemaType.KEYWORD),
    ],
)
def test_tombstone_source_rejects_incompatible_indexes(field_name, field_schema):
    payload_schema = {
        "source": SimpleNamespace(data_type=pipeline.PayloadSchemaType.KEYWORD),
        "deleted_at": SimpleNamespace(data_type=pipeline.PayloadSchemaType.FLOAT),
    }
    payload_schema[field_name] = SimpleNamespace(data_type=field_schema)
    client = SimpleNamespace(
        get_collection=lambda _collection: SimpleNamespace(
            payload_schema=payload_schema
        )
    )
    store = SimpleNamespace(client=client, collection="policies")

    expected_schema = (
        pipeline.PayloadSchemaType.KEYWORD
        if field_name == "source"
        else pipeline.PayloadSchemaType.FLOAT
    )
    with pytest.raises(
        ValueError,
        match=f"payload index for '{field_name}' must be {expected_schema}",
    ):
        pipeline.tombstone_source(store, "leave.md")


def test_ingestion_matches_load_corpus_chunks_and_ids(monkeypatch, tmp_path):
    body = "0123456789" * 120
    (tmp_path / "leave.md").write_text(body, encoding="utf-8")
    expected_chunks = load_corpus(tmp_path)
    captured = {}
    store = SimpleNamespace(
        client=SimpleNamespace(upsert=lambda **kwargs: captured.update(kwargs)),
        collection="policies",
    )

    monkeypatch.setattr(pipeline, "tombstone_source", lambda store, source: 0)
    monkeypatch.setattr(
        pipeline,
        "embed_texts",
        lambda texts: [[float(index)] for index, _ in enumerate(texts)],
    )
    monkeypatch.setattr(pipeline.cache, "clear", lambda: 1)

    result = pipeline.ingest_or_update_source(
        store, source="policies/leave.md", body=body
    )

    payloads = [point.payload for point in captured["points"]]
    assert [
        {key: payload[key] for key in ("chunk_id", "source_id", "text")}
        for payload in payloads
    ] == expected_chunks
    assert all(payload["source_id"] == "leave" for payload in payloads)
    assert result == {
        "tombstoned": 0,
        "ingested": len(expected_chunks),
        "cache_cleared": 1,
    }


def test_embed_texts_uses_lazy_openai_client(monkeypatch):
    batches = []
    client = SimpleNamespace(
        embeddings=SimpleNamespace(
            create=lambda **kwargs: (
                batches.append(kwargs)
                or SimpleNamespace(
                    data=[
                        SimpleNamespace(index=1, embedding=[0.2]),
                        SimpleNamespace(index=0, embedding=[0.1]),
                    ]
                )
            )
        )
    )
    monkeypatch.setattr(pipeline, "_openai", lambda: client)

    assert pipeline.embed_texts(["first", "second"]) == [[0.1], [0.2]]
    assert batches == [
        {
            "model": pipeline.EMBEDDING_MODEL,
            "input": ["first", "second"],
        }
    ]
