"""Week 5 - run the golden set through the app and judge every answer.

Flow:  load golden set -> POST each question to /ask_batched -> judge the answer
against the ideal -> persist to eval_runs -> write docs/eval-run-001.md.

Prereqs:
  * the API running:   uvicorn api.main:app --port 8000
  * OPENAI_API_KEY set (real judge = gpt-4o), OR run offline: USE_FAKE=1 python scripts/run_eval.py

Usage:  python scripts/run_eval.py
"""

from __future__ import annotations
import argparse
import sqlite3
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx

from src.eval.golden import load_golden
from src.eval.judge import judge_with_telemetry
from src.pipeline import store

DEFAULT_API_URL = "http://localhost:8000"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate the app against a golden set"
    )
    parser.add_argument("--golden-set", default="data/golden_set.jsonl")
    parser.add_argument("--db", default="data/answers.db")
    parser.add_argument("--api-url", default=DEFAULT_API_URL)
    parser.add_argument("--judge-model", default="gpt-4o")
    parser.add_argument("--label", default="eval-run-004")
    return parser.parse_args(argv)


def get_candidate(question: str, api_url: str) -> dict:
    """Ask the running app for an answer."""
    endpoint = api_url.rstrip("/")
    if not endpoint.endswith("/ask_batched"):
        endpoint += "/ask_batched"
    started = time.perf_counter()
    response = httpx.post(endpoint, json={"question": question}, timeout=60.0)
    response.raise_for_status()
    data = response.json()
    return {
        "content": data["content"],
        "sources": data.get("sources", []),
        "model": data.get("candidate_model"),
        "cost_usd": data.get("cost_usd"),
        "latency_ms": (time.perf_counter() - started) * 1000,
        "prompt_tokens": data.get("prompt_tokens"),
        "completion_tokens": data.get("completion_tokens"),
        "embedding_tokens": data.get("embedding_tokens"),
    }


def source_document_id(source: str) -> str:
    """Normalize either a source ID or chunk ID to its document ID."""
    return source.partition("#")[0]


def retrieval_source_metrics(
    expected_sources: set[str], retrieved_sources: set[str]
) -> tuple[bool | None, bool | None, float | None]:
    """Return any-source hit, complete-source hit, and expected-source coverage."""
    if not expected_sources:
        return None, None, None
    found = expected_sources & retrieved_sources
    return bool(found), found == expected_sources, len(found) / len(expected_sources)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    golden = load_golden(args.golden_set)
    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    run_id = int(time.time())
    report_path = Path("docs") / f"{args.label}.md"
    if report_path.exists():
        raise SystemExit(
            f"Report already exists: {report_path}; choose a unique --label"
        )
    with sqlite3.connect(db_path) as check_conn:
        has_eval_runs = check_conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'eval_runs'"
        ).fetchone()
        if (
            has_eval_runs
            and check_conn.execute(
                "SELECT 1 FROM eval_runs WHERE eval_run_label = ? LIMIT 1",
                (args.label,),
            ).fetchone()
        ):
            raise SystemExit(
                f"Run label already exists in {db_path}: {args.label!r}; "
                "choose a unique --label"
            )

    rows, accs, grds, fmts = [], [], [], []
    candidate_costs, candidate_latencies = [], []
    judge_costs, judge_latencies = [], []
    retrieval_hits, complete_source_hits, source_coverages = [], [], []
    with store.connect(db_path) as con:
        for g in golden:
            candidate_metrics = get_candidate(g.question, args.api_url)
            candidate = candidate_metrics["content"]
            expected_sources = set(g.expected_sources)
            retrieved_sources = {
                source_document_id(source) for source in candidate_metrics["sources"]
            }
            candidate_metrics["expected_sources"] = sorted(expected_sources)
            (
                candidate_metrics["retrieval_hit"],
                candidate_metrics["complete_source_hit"],
                candidate_metrics["source_coverage"],
            ) = retrieval_source_metrics(
                expected_sources,
                retrieved_sources,
            )
            judge_started = time.perf_counter()
            s, judge_metrics = judge_with_telemetry(
                g.question,
                g.ideal_answer,
                candidate,
                g.must_mention,
                model=args.judge_model,
            )
            judge_metrics["latency_ms"] = (time.perf_counter() - judge_started) * 1000
            eval_run_id = store.write_eval_run(
                con,
                golden_id=g.id,
                question=g.question,
                candidate_answer=candidate,
                ideal_answer=g.ideal_answer,
                judge_model=args.judge_model,
                scores=s,
                label=args.label,
            )
            store.write_eval_telemetry(
                con,
                eval_run_id=eval_run_id,
                candidate=candidate_metrics,
                judge=judge_metrics,
            )
            rows.append((g.id, candidate, s, candidate_metrics, judge_metrics))
            accs.append(s["accuracy"])
            grds.append(s["groundedness"])
            fmts.append(s["format"])
            if candidate_metrics["cost_usd"] is not None:
                candidate_costs.append(candidate_metrics["cost_usd"])
            candidate_latencies.append(candidate_metrics["latency_ms"])
            if judge_metrics["cost_usd"] is not None:
                judge_costs.append(judge_metrics["cost_usd"])
            judge_latencies.append(judge_metrics["latency_ms"])
            if candidate_metrics["retrieval_hit"] is not None:
                retrieval_hits.append(candidate_metrics["retrieval_hit"])
                complete_source_hits.append(candidate_metrics["complete_source_hit"])
                source_coverages.append(candidate_metrics["source_coverage"])
            print(
                f"{g.id}: acc={s['accuracy']} grnd={s['groundedness']} fmt={s['format']}  "
                f"hit@3={candidate_metrics['retrieval_hit']} "
                f"all_sources={candidate_metrics['complete_source_hit']} "
                f"cand_cost={candidate_metrics['cost_usd']} "
                f"cand_ms={candidate_metrics['latency_ms']:.1f} "
                f"judge_cost={judge_metrics['cost_usd']} "
                f"judge_ms={judge_metrics['latency_ms']:.1f} | {candidate[:60]}"
            )

    n = len(rows)
    avg = lambda xs: round(statistics.mean(xs), 2) if xs else 0.0
    avg_cost = lambda xs: statistics.mean(xs) if xs else None
    median_ms = lambda xs: statistics.median(xs) if xs else None
    retrieval_rate = (
        f"{sum(retrieval_hits)}/{len(retrieval_hits)} "
        f"({statistics.mean(retrieval_hits) * 100:.1f}%)"
        if retrieval_hits
        else "not measured"
    )
    complete_source_rate = (
        f"{sum(complete_source_hits)}/{len(complete_source_hits)} "
        f"({statistics.mean(complete_source_hits) * 100:.1f}%)"
        if complete_source_hits
        else "not measured"
    )
    mean_source_coverage = (
        f"{statistics.mean(source_coverages) * 100:.1f}%"
        if source_coverages
        else "not measured"
    )
    fmt_cost = lambda value: f"${value:.8f}" if value is not None else "not measured"
    fmt_ms = lambda value: f"{value:.1f} ms" if value is not None else "not measured"
    lines = [
        f"# {args.label} ({n} golden questions)",
        "",
        f"- run_id: `{run_id}`",
        f"- avg accuracy:     **{avg(accs)}** / 4",
        f"- avg groundedness: **{avg(grds)}** / 4",
        f"- avg format:       **{avg(fmts)}** / 4",
        f"- retrieval hit@3:  **{retrieval_rate}**",
        f"- complete-source hit@3: **{complete_source_rate}**",
        f"- expected-source coverage@3: **{mean_source_coverage}**",
        "",
        "## Cost and latency",
        "",
        "Candidate latency is end-to-end API request time; judge latency is the local time around the judge call.",
        "",
        f"- Candidate cost total / average: {fmt_cost(sum(candidate_costs) if candidate_costs else None)} / {fmt_cost(avg_cost(candidate_costs))} ({len(candidate_costs)}/{n} measured)",
        f"- Candidate latency median (p50): {fmt_ms(median_ms(candidate_latencies))}",
        f"- Judge cost total / average: {fmt_cost(sum(judge_costs) if judge_costs else None)} / {fmt_cost(avg_cost(judge_costs))} ({len(judge_costs)}/{n} measured)",
        f"- Judge latency median (p50): {fmt_ms(median_ms(judge_latencies))}",
        "",
        "| id | any hit | all sources | coverage | acc | grnd | fmt | retrieved sources | candidate cost | candidate ms | judge cost | judge ms | candidate |",
        "|----|:-------:|:-----------:|:--------:|-----|------|-----|-------------------|---------------:|-------------:|-----------:|---------:|-----------|",
    ]
    for gid, cand, s, candidate_metrics, judge_metrics in rows:
        c = cand.replace("|", "/")[:70]
        hit_label = (
            "yes"
            if candidate_metrics["retrieval_hit"] is True
            else "no" if candidate_metrics["retrieval_hit"] is False else "n/a"
        )
        complete_hit_label = (
            "yes"
            if candidate_metrics["complete_source_hit"] is True
            else "no" if candidate_metrics["complete_source_hit"] is False else "n/a"
        )
        source_coverage_label = (
            f"{candidate_metrics['source_coverage'] * 100:.0f}%"
            if candidate_metrics["source_coverage"] is not None
            else "n/a"
        )
        lines.append(
            f"| {gid} | {hit_label} | {complete_hit_label} | {source_coverage_label} | "
            f"{s['accuracy']} | {s['groundedness']} | {s['format']} | "
            f"{', '.join(candidate_metrics['sources'])} | "
            f"{fmt_cost(candidate_metrics['cost_usd'])} | "
            f"{fmt_ms(candidate_metrics['latency_ms'])} | "
            f"{fmt_cost(judge_metrics['cost_usd'])} | "
            f"{fmt_ms(judge_metrics['latency_ms'])} | {c} |"
        )
    with report_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(
        f"\nWrote {report_path}  (avg accuracy {avg(accs)}/4 over {n} questions; "
        f"candidate avg cost {fmt_cost(avg_cost(candidate_costs))}, "
        f"candidate p50 {fmt_ms(median_ms(candidate_latencies))})"
    )


if __name__ == "__main__":
    main()
