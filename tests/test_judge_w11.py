import asyncio
import json
import sys
from types import ModuleType, SimpleNamespace

from src.eval import judge_W11


def test_judge_one_closes_async_openai_client(monkeypatch):
    lifecycle = []
    response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    tool_calls=[
                        SimpleNamespace(
                            function=SimpleNamespace(
                                arguments=json.dumps(
                                    {
                                        "accuracy": 4,
                                        "groundedness": 4,
                                        "format": 3,
                                        "reasoning": "The response is accurate and grounded.",
                                    }
                                )
                            )
                        )
                    ]
                )
            )
        ]
    )

    class FakeClient:
        chat = SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **_kwargs: completed_response()
            )
        )

        async def __aenter__(self):
            lifecycle.append("enter")
            return self

        async def __aexit__(self, _exc_type, _exc_value, _traceback):
            lifecycle.append("exit")

    async def completed_response():
        return response

    monkeypatch.setattr(judge_W11, "_async_openai", lambda _api_key: FakeClient())

    score = asyncio.run(judge_W11.judge_one("Question", "Answer", "Ideal"))

    assert score.task_success
    assert lifecycle == ["enter", "exit"]


def test_judge_one_sync_uses_and_closes_sync_client(monkeypatch):
    lifecycle = []
    response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    tool_calls=[
                        SimpleNamespace(
                            function=SimpleNamespace(
                                arguments=json.dumps(
                                    {
                                        "accuracy": 4,
                                        "groundedness": 4,
                                        "format": 3,
                                        "reasoning": "The response is accurate and grounded.",
                                    }
                                )
                            )
                        )
                    ]
                )
            )
        ]
    )

    class FakeOpenAI:
        def __init__(self, *, api_key):
            assert api_key == "test-key"
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(
                    create=lambda **_kwargs: response
                )
            )

        def __enter__(self):
            lifecycle.append("enter")
            return self

        def __exit__(self, _exc_type, _exc_value, _traceback):
            lifecycle.append("exit")

    openai = ModuleType("openai")
    openai.OpenAI = FakeOpenAI
    monkeypatch.setitem(sys.modules, "openai", openai)

    score = judge_W11.judge_one_sync(
        "Question", "Answer", "Ideal", api_key="test-key"
    )

    assert score.task_success
    assert lifecycle == ["enter", "exit"]
