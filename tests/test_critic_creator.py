from src.eval import critic_creator


def test_loop_forwards_models_and_threshold(monkeypatch):
    observed = {}

    def fake_critic(question, answer, must_mention, *, model, threshold):
        observed.update(judge_model=model, threshold=threshold)
        return {"issues": ["revise"], "is_good_enough": False}

    def fake_creator(question, answer, critique, *, model):
        observed["creator_model"] = model
        return "Revised answer"

    monkeypatch.setattr(critic_creator, "critic", fake_critic)
    monkeypatch.setattr(critic_creator, "creator", fake_creator)

    result = critic_creator.critic_creator(
        "Question",
        "Draft",
        ["required fact"],
        max_rounds=2,
        creator_model="creator-test",
        judge_model="judge-test",
        threshold=4.25,
    )

    assert observed == {
        "judge_model": "judge-test",
        "threshold": 4.25,
        "creator_model": "creator-test",
    }
    assert result["final"] == "Revised answer"
    assert result["rounds"] == 2
