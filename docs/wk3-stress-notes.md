Finding 1 — Malformed JSON. Response codes for each of the four bad inputs; 

curl -i -X POST http://localhost:8000/ask \
-H "Content-Type: application/json" \
-d '{"question": "What is the leave policy?"'
HTTP/1.1 422 Unprocessable Content
date: Tue, 01 Sep 2026 12:46:10 GMT
server: uvicorn
content-length: 133
content-type: application/json

{"detail":[{"type":"json_invalid","loc":["body",40],"msg":"JSON decode error","input":{},"ctx":{"error":"Expecting ',' delimiter"}}]}%    


• Finding 2 — 5000-character question. Total wall time observed; 
curl -N -X POST http://localhost:8000/ask -H "Content-Type: application/json"  0.02s user 0.05s system 0% cpu 42.228 total

• Finding 3 — Disconnect mid-stream. What the server logged on --max-time 1;
whether /health still responded after.
curl --max-time 1 -N -X POST http://localhost:8000/ask \
-H "Content-Type: application/json" \
-d '{"question": "Please give me a long answer about something
complicated"}'
{"detail":[{"type":"json_invalid","loc":["body",58],"msg":"JSON decode error","input":{},"ctx":{"error":"Invalid control character at"}}]}% 


• Finding 4 — 50 parallel requests. Successes out of 50; p50 / p95 latency; effective req/s;
python scripts/stress_test.py --requests 50 --concurrent 10
Stress test: 50 requests, up to 10 concurrent
────────────────────────────────────────────────────────────
Total wall time:   8.92s
Successes:         50 / 50
Effective req/s:   5.60

Latency (successful requests):
  min:   1.00s
  p50:   1.51s
  p95:   2.14s
  max:   2.17s