from src.eval.golden import load_golden


def test_challenge_set_has_twenty_multidocument_questions():
    entries = load_golden("data/golden_set_challenge.jsonl")

    assert len(entries) == 20
    assert len({entry.id for entry in entries}) == 20
    assert all(len(entry.expected_sources) >= 2 for entry in entries)
    assert all(entry.must_mention for entry in entries)
