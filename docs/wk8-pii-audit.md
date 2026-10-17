# W8 PII Audit — capstone_chunks_v2

**Date:** 2026-10-17
**Corpus:** `data/corpus/` (20 documents)
**Collection:** `capstone_chunks_v2`
**Total chunks ingested:** 800
**PII detector flags:** 74 across 59 chunks (7.4% of chunks flagged; 9.3 flags per 100 chunks)

## Sample audit — 10 returned chunks

Fetched via:
```python
from src.rag.qdrant_store import _get_client
client = _get_client()
sample = client.scroll(collection_name="capstone_chunks_v2", limit=10, with_payload=True)[0]
```

The supplied scroll returns the first page of points, not a random sample. These
ten records are all from `01_leave_policy.md`, so they are not representative of
all 20 source documents. The audit inspected metadata only and did not print or
review chunk text.

| Chunk ID | Source | Stored PII flag count | Payload metadata present |
|---|---|---:|---|
| `01_leave_policy#0` | `01_leave_policy.md` | 0 | yes |
| `01_leave_policy#1` | `01_leave_policy.md` | 1 | yes |
| `01_leave_policy#2` | `01_leave_policy.md` | 0 | yes |
| `01_leave_policy#3` | `01_leave_policy.md` | 1 | yes |
| `01_leave_policy#4` | `01_leave_policy.md` | 0 | yes |
| `01_leave_policy#5` | `01_leave_policy.md` | 5 | yes |
| `01_leave_policy#6` | `01_leave_policy.md` | 0 | yes |
| `01_leave_policy#7` | `01_leave_policy.md` | 2 | yes |
| `01_leave_policy#8` | `01_leave_policy.md` | 0 | yes |
| `01_leave_policy#9` | `01_leave_policy.md` | 1 | yes |

Sample total: 10 flags across 6 of 10 chunks. The stored count reflects the
ingestion detector's matches; flags are indicators for review, not confirmation
that the content is personal data. The full collection contains 74 detector
flags across 59 of 800 chunks.
