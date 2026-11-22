import asyncio
import sys
from types import ModuleType, SimpleNamespace

from src.eval.ragas_metrics import _ragas_score


def test_ragas_score_passes_langchain_compatible_embeddings(monkeypatch):
    observed = {}

    class FakeDataset:
        @staticmethod
        def from_dict(data):
            return data

    class FakeEmbeddings:
        def __init__(self, *, model):
            self.model = model

    class FakeSeries:
        def __init__(self, values):
            self.values = values

        @property
        def iloc(self):
            return self

        def __getitem__(self, index):
            return self.values[index]

        def mean(self):
            return sum(self.values) / len(self.values)

    class FakeFrame:
        def __getitem__(self, _column):
            return FakeSeries([0.75])

    async def fake_aevaluate(dataset, *, metrics, embeddings, raise_exceptions):
        assert asyncio.current_task() is not None
        async with asyncio.timeout(1):
            await asyncio.sleep(0)
        observed.update(
            dataset=dataset,
            metrics=metrics,
            embeddings=embeddings,
            raise_exceptions=raise_exceptions,
        )
        return SimpleNamespace(to_pandas=lambda: FakeFrame())

    datasets = ModuleType("datasets")
    datasets.Dataset = FakeDataset
    ragas = ModuleType("ragas")
    ragas.aevaluate = fake_aevaluate
    langchain_openai = ModuleType("langchain_openai")
    langchain_openai.OpenAIEmbeddings = FakeEmbeddings
    monkeypatch.setitem(sys.modules, "datasets", datasets)
    monkeypatch.setitem(sys.modules, "ragas", ragas)
    monkeypatch.setitem(sys.modules, "langchain_openai", langchain_openai)

    result = _ragas_score(
        "answer_relevance",
        [
            {
                "id": "g001",
                "question": "Question?",
                "answer": "Answer.",
                "contexts": ["Context."],
                "ground_truth": "Ground truth.",
            }
        ],
        metric=object(),
        column="answer_relevancy",
    )

    assert observed["embeddings"].model == "text-embedding-3-small"
    assert observed["raise_exceptions"] is True
    assert result.aggregate == 0.75
    assert result.per_row == {"g001": 0.75}
