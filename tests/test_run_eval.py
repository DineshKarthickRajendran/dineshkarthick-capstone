import sqlite3
from types import SimpleNamespace

from scripts import run_eval
from src.eval.golden import GoldenEntry


def test_cli_arguments_reach_evaluation_and_storage(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "docs").mkdir()
    golden_path = "fixtures/questions.jsonl"
    db_path = tmp_path / "answers.db"
    entry = GoldenEntry(
        id="g001",
        question="What is the policy?",
        ideal_answer="Use the approved policy.",
        must_mention=["approved"],
        expected_sources=["policy"],
    )
    observed = {}

    monkeypatch.setattr(
        run_eval,
        "load_golden",
        lambda path: observed.update(golden_path=path) or [entry],
    )

    def fake_get_candidate(question, api_url):
        observed.update(question=question, api_url=api_url)
        return {
            "content": "Use the approved policy.",
            "sources": ["policy#chunk-0"],
            "model": "gpt-4o-mini",
            "cost_usd": 0.00001,
            "latency_ms": 125.0,
            "prompt_tokens": 20,
            "completion_tokens": 5,
            "embedding_tokens": 4,
        }

    def fake_judge(question, ideal, candidate, must_mention, *, model):
        observed["judge_model"] = model
        return (
            {
                "accuracy": 4,
                "groundedness": 4,
                "format": 4,
                "reasoning": "Matches the policy.",
            },
            {
                "model": model,
                "cost_usd": 0.00002,
                "prompt_tokens": 40,
                "completion_tokens": 10,
            },
        )

    monkeypatch.setattr(run_eval, "get_candidate", fake_get_candidate)
    monkeypatch.setattr(run_eval, "judge_with_telemetry", fake_judge)

    run_eval.main(
        [
            "--golden-set",
            golden_path,
            "--db",
            str(db_path),
            "--api-url",
            "http://localhost:8000",
            "--judge-model",
            "gpt-4o-mini",
            "--label",
            "smoke-test",
        ]
    )

    assert observed == {
        "golden_path": golden_path,
        "question": entry.question,
        "api_url": "http://localhost:8000",
        "judge_model": "gpt-4o-mini",
    }
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT judge_model, eval_run_label, candidate_answer FROM eval_runs"
        ).fetchone()
        telemetry = conn.execute(
            """SELECT candidate_model, candidate_cost_usd, candidate_latency_ms,
                      candidate_embedding_tokens, judge_model, judge_cost_usd,
                      judge_latency_ms, judge_prompt_tokens
               FROM eval_call_telemetry"""
        ).fetchone()
    assert row == ("gpt-4o-mini", "smoke-test", "Use the approved policy.")
    assert telemetry[:4] == ("gpt-4o-mini", 0.00001, 125.0, 4)
    assert telemetry[4] == "gpt-4o-mini"
    assert telemetry[5] == 0.00002
    assert telemetry[6] >= 0
    assert telemetry[7] == 40
    report = (tmp_path / "docs" / "smoke-test.md").read_text(encoding="utf-8")
    assert "Candidate cost total / average" in report
    assert "candidate ms" in report
    assert "retrieval hit@3:  **1/1 (100.0%)**" in report
    assert "| g001 | yes |" in report


def test_get_candidate_adds_endpoint_to_api_base(monkeypatch):
    observed = {}

    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "content": "answer",
                "sources": ["policy.md"],
                "cost_usd": 0.00001,
                "candidate_model": "gpt-4o-mini",
                "prompt_tokens": 20,
                "completion_tokens": 5,
                "embedding_tokens": 4,
            }

    def fake_post(url, *, json, timeout):
        observed.update(url=url, payload=json, timeout=timeout)
        return Response()

    monkeypatch.setattr(run_eval.httpx, "post", fake_post)

    answer = run_eval.get_candidate("Question?", "http://localhost:8000/")

    assert answer["content"] == "answer"
    assert answer["sources"] == ["policy.md"]
    assert answer["cost_usd"] == 0.00001
    assert answer["model"] == "gpt-4o-mini"
    assert answer["prompt_tokens"] == 20
    assert answer["completion_tokens"] == 5
    assert answer["embedding_tokens"] == 4
    assert answer["latency_ms"] >= 0
    assert observed["url"] == "http://localhost:8000/ask_batched"
    assert observed["payload"] == {"question": "Question?"}
