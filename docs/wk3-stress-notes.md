Finding 1 — Malformed JSON. Response codes for each of the four bad inputs; whether
any reached your application code.
• Finding 2 — 5000-character question. Total wall time observed; whether the API hit a
token limit; whether streaming worked.
• Finding 3 — Disconnect mid-stream. What the server logged on --max-time 1;
whether /health still responded after.
• Finding 4 — 50 parallel requests. Successes out of 50; p50 / p95 latency; effective req/s;
whether SQLite captured all entries.