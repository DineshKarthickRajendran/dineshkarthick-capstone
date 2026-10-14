import json
import sys
from types import SimpleNamespace

from src.eval import judge as judge_module
from src.pipeline.cost import compute_cost_usd


def test_judge_with_telemetry_returns_usage_and_cost(monkeypatch):
    response = SimpleNamespace(
        usage=SimpleNamespace(prompt_tokens=100, completion_tokens=50),
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    tool_calls=[
                        SimpleNamespace(
                            function=SimpleNamespace(
                                arguments=json.dumps(
                                    {
                                        "accuracy": 4,
                                        "groundedness": 3,
                                        "format": 4,
                                        "reasoning": "Supported answer.",
                                    }
                                )
                            )
                        )
                    ]
                )
            )
        ],
    )

    class FakeOpenAI:
        def __init__(self, *, api_key):
            assert api_key == "test-key"
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(create=lambda **_kwargs: response)
            )

    monkeypatch.setattr(judge_module, "USE_FAKE", False)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=FakeOpenAI))

    scores, telemetry = judge_module.judge_with_telemetry(
        "Question", "Ideal", "Candidate", [], model="gpt-4o"
    )

    assert scores["accuracy"] == 4
    assert telemetry == {
        "model": "gpt-4o",
        "prompt_tokens": 100,
        "completion_tokens": 50,
        "cost_usd": compute_cost_usd("gpt-4o", 100, 50),
    }
