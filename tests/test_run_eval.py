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
    )
    observed = {}

    monkeypatch.setattr(
        run_eval,
        "load_golden",
        lambda path: observed.update(golden_path=path) or [entry],
    )

    def fake_get_candidate(question, api_url):
        observed.update(question=question, api_url=api_url)
        return "Use the approved policy.", []

    def fake_judge(question, ideal, candidate, must_mention, *, model):
        observed["judge_model"] = model
        return {
            "accuracy": 4,
            "groundedness": 4,
            "format": 4,
            "reasoning": "Matches the policy.",
        }

    monkeypatch.setattr(run_eval, "get_candidate", fake_get_candidate)
    monkeypatch.setattr(run_eval, "judge", fake_judge)

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
    assert row == ("gpt-4o-mini", "smoke-test", "Use the approved policy.")


def test_get_candidate_adds_endpoint_to_api_base(monkeypatch):
    observed = {}

    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"content": "answer", "sources": ["policy.md"]}

    def fake_post(url, *, json, timeout):
        observed.update(url=url, payload=json, timeout=timeout)
        return Response()

    monkeypatch.setattr(run_eval.httpx, "post", fake_post)

    answer = run_eval.get_candidate("Question?", "http://localhost:8000/")

    assert answer == ("answer", ["policy.md"])
    assert observed["url"] == "http://localhost:8000/ask_batched"
    assert observed["payload"] == {"question": "Question?"}
