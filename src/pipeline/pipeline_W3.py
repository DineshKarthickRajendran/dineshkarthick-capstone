from __future__ import annotations

import asyncio
import csv
import json
import time
from pathlib import Path

from .logging_config import get_logger
from .settings import RunSummary, Settings

log = get_logger()

# ─────────────────────────────────────────────────────────────────────────────
# LLM client setup — branches on Settings.use_fake at module-load time
# ─────────────────────────────────────────────────────────────────────────────

_settings_for_import = Settings(use_fake=True)

if _settings_for_import.use_fake:
    from .fake_llm import Question, Answer, FakeLLMError, fake_ask_llm
else:
    from dotenv import load_dotenv
    from pydantic import BaseModel
    from openai import AsyncOpenAI

    load_dotenv()  # load .env for OPENAI_API_KEY
    _client = AsyncOpenAI()  # reads OPENAI_API_KEY from env automatically

    class Question(BaseModel):
        text: str

    class Answer(BaseModel):
        question: str
        text: str
        cost_usd: float
        retries: int = 0


# ─────────────────────────────────────────────────────────────────────────────
# CSV loader
# ─────────────────────────────────────────────────────────────────────────────


def load_questions(path: str | Path = ("data/questions.csv")) -> list[Question]:
    """Read questions from a CSV with a `text` column."""

    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [Question(text=row["text"]) for row in rows if row.get("text")]


# ─────────────────────────────────────────────────────────────────────────────
# Core LLM calls
# ─────────────────────────────────────────────────────────────────────────────


async def ask_llm(q: Question, fail_rate: float = 0.0) -> Answer:
    """One LLM call. Branches on Settings.use_fake."""
    if _settings_for_import.use_fake:
        ans = await fake_ask_llm(q, fail_rate=fail_rate)
    else:
        resp = await _client.chat.completions.create(
            model=_settings_for_import.model,
            messages=[{"role": "user", "content": q.text}],
        )
        ans = Answer(
            question=q.text,
            text=resp.choices[0].message.content,
            cost_usd=0.0001,  # real cost-from-usage lands in W25
        )
    log.info(f"asked: {q.text[:40]}")
    return ans


async def ask_llm_with_retry(
    q: Question, tries: int = 3, fail_rate: float = 0.0
) -> Answer:
    """Retry up to `tries` times. Wait 1 s, 2 s, 4 s between attempts.

    Re-raises the last exception if all attempts fail (no silent failures).
    """
    for attempt in range(tries):
        try:
            ans = await ask_llm(q, fail_rate=fail_rate)
            ans.retries = attempt
            return ans
        except Exception as exc:
            if attempt == tries - 1:
                raise
            log.warning(f"retry {attempt + 1} for: {q.text[:40]} ({exc})")
            await asyncio.sleep(2**attempt)  # 1, 2, 4 seconds
    raise RuntimeError("unreachable")


# ─────────────────────────────────────────────────────────────────────────────
# Batch runners
# ─────────────────────────────────────────────────────────────────────────────


async def run_batch(qs: list[Question], fail_rate: float = 0.0) -> list[Answer]:
    """Fire every question in parallel via one big asyncio.gather (no batching)."""
    tasks = [ask_llm_with_retry(q, fail_rate=fail_rate) for q in qs]
    return await asyncio.gather(*tasks)


async def run_in_batches(
    qs: list[Question], batch_size: int = 5, fail_rate: float = 0.0
) -> list[Answer]:
    """Fire questions in chunks of `batch_size`, with a 100 ms pause between batches."""
    out: list[Answer] = []
    for i in range(0, len(qs), batch_size):
        chunk = qs[i : i + batch_size]
        log.info(f"batch {i // batch_size + 1}: {len(chunk)} questions")
        batch_answers = await run_batch(chunk, fail_rate=fail_rate)
        out.extend(batch_answers)
        await asyncio.sleep(0.1)  # 100 ms pause between batches
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Run summariser
# ─────────────────────────────────────────────────────────────────────────────
def summarize_run(
    answers: list[Answer],
    *,
    started_at: float,
    elapsed: float,
    fail_rate: float,
    use_fake: bool,
) -> RunSummary:
    """Roll a list of Answers + wall-clock data into a RunSummary."""
    return RunSummary(
        started_at=started_at,
        elapsed_seconds=elapsed,
        n_questions=len(answers),
        n_succeeded=len(answers),
        n_retries_total=sum(a.retries for a in answers),
        total_cost_usd=sum(a.cost_usd for a in answers),
        fail_rate=fail_rate,
        use_fake=use_fake,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Entrypoint
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    settings = Settings()
    log.info(f"config: {settings.model_dump(mode='json')} ")

    questions = load_questions(settings.questions_csv)
    log.info(f"loaded {len(questions)} questions ")

    started = time.time()
    answers = asyncio.run(
        run_in_batches(
            questions, batch_size=settings.batch_size, fail_rate=settings.fail_rate
        )
    )
    elapsed = time.time() - started

    summary = summarize_run(
        answers,
        started_at=started,
        elapsed=elapsed,
        fail_rate=settings.fail_rate,
        use_fake=settings.use_fake,
    )
    log.info(f"run summary: {summary.model_dump_json()} ")

    # Write the structured artefact
    settings.results_json.write_text(
        json.dumps(
            {
                "summary": summary.model_dump(mode="json"),
                "answers": [a.model_dump() for a in answers],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"wrote {len(answers)} answers to {settings.results_json} in {elapsed:.2f}s")

    # # SQLite persistence
    # # Deferred import: store.py imports Answer from this module; top-level import
    # # would cause a circular import.
    from .store import connect, write_answers, write_run

    with connect(settings.results_db) as con:
        run_id = write_run(con, summary)
        n = write_answers(con, run_id, answers)
    log.info(f"persisted run {run_id} with {n} answers to {settings.results_db}")
