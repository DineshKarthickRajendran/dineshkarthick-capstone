"""tests/test_api.py — REFERENCE for Week 3 Lab Step 2 sub-step 2b (API tests).

Uses FastAPI's TestClient. No mocking needed for these — they test the
validation surface, not the LLM. The underlying W2 pipeline runs in
`use_fake=True` mode (the default) so any actual /ask call would use canned
fake answers — but these tests never reach an LLM call.

Run with:
    pytest tests/test_api.py -v
"""

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_ask_rejects_missing_question():
    """POST /ask with empty body -> 422 Unprocessable Entity."""
    response = client.post("/ask", json={})
    assert response.status_code == 422
    body = response.json()
    detail_text = str(body.get("detail", ""))
    assert "question" in detail_text.lower()


def test_health_returns_ok():
    """GET /health -> 200 OK with the expected body."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ask_w9_returns_rag_sources_and_usage(monkeypatch):
    from src.rag import qdrant_rag

    monkeypatch.setattr(
        qdrant_rag,
        "ask_rag",
        lambda question, *, settings: {
            "answer": "Employees accrue 18 days [01_leave_policy].",
            "sources": ["01_leave_policy"],
            "candidate_model": "gpt-4o-mini",
            "prompt_tokens": 100,
            "completion_tokens": 12,
            "embedding_tokens": 8,
            "cost_usd": 0.0001,
        },
    )

    response = client.post(
        "/ask_w9", json={"question": "How many annual leave days?"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "content": "Employees accrue 18 days [01_leave_policy].",
        "cost_usd": 0.0001,
        "retries": 0,
        "sources": ["01_leave_policy"],
        "candidate_model": "gpt-4o-mini",
        "prompt_tokens": 100,
        "completion_tokens": 12,
        "embedding_tokens": 8,
        "confidence": 1.0,
        "schema_version": "v1",
    }
