from src.eval.golden import GoldenEntry
from scripts import run_pairwise


def test_main_writes_summary_to_output_path(tmp_path, monkeypatch):
    output_path = tmp_path / "reports" / "pairwise-summary.md"
    entry = GoldenEntry(
        id="g001",
        question="What is the policy?",
        ideal_answer="Use the approved policy.",
        must_mention=["approved"],
    )
    monkeypatch.setattr(run_pairwise, "load_golden", lambda _path: [entry])
    monkeypatch.setattr(run_pairwise, "get_candidate", lambda _question: "Answer")
    monkeypatch.setattr(
        run_pairwise,
        "pairwise_consistent",
        lambda *_args: "APP",
    )

    run_pairwise.main(["--golden-set", "questions.jsonl", "--output", str(output_path)])

    summary = output_path.read_text(encoding="utf-8")
    assert "Pairwise comparison summary (1 golden questions)" in summary
    assert "| APP | 1 |" in summary
    assert "| g001 | APP |" in summary
