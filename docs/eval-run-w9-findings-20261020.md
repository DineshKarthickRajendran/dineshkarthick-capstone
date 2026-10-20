# W9 Evaluation Findings — 2026-10-20

## Status: blocked during W9 retrieval

Ran `scripts/run_eval.py` against the active `src.api.main` application with
`data/golden_set_w9.jsonl`, the `/ask_w9` endpoint, and label
`eval-run-w9-findings-activeapi-20261020`.

The first `/ask_w9` request failed during query embedding. The configured key
was rejected by the default OpenAI API endpoint with HTTP 401
(`invalid_api_key`), returned by the API as HTTP 500. No candidate answer was
returned, and no evaluation rows or scored findings report were produced.

| Measure | Result |
|---|---|
| Golden questions | 20 |
| Candidate answers returned | 0 |
| Questions fully evaluated | 0 |
| Accuracy / groundedness / format | Not measured |
| Retrieval metrics | Not measured |
| Judge cost | Not measured |

The active API was served from `src.api.main` on port 8001. The attempt used
the temporary database `/tmp/eval-run-w9-findings-20261020.db`; it contains no
evaluation rows for this label. This report is a run-status record, not a
scored W9 findings report.

The configured credential was rejected by the OpenAI API endpoint. Configure a
valid authorized key, or the course provider's supported API base URL and model.
Start the active API module and rerun:

```bash
uvicorn src.api.main:app --reload --port 8000
```

```bash
python scripts/run_eval.py \
  --golden-set data/golden_set_w9.jsonl \
  --endpoint /ask_w9 \
  --label eval-run-w9-findings-20261020-retry
```

Do not put credentials in source code, logs, or reports. A previous diagnostic
print of the configured credential was removed from the pipeline; rotate the
credential if it was exposed outside your trusted environment.
