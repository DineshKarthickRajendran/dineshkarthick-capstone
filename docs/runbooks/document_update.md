# Document Update Runbook

**When to run:** a source doc has changed and needs to be reflected in
retrieval + generation.

## Steps

1. **Pull the updated file** into `data/`
2. **Run** `python -m scripts.update_document <path/to/file>`
   - Tombstones old chunks (marks deleted_at)
   - Inserts new chunks
   - Clears semantic cache
3. **Verify** with a query that would touch the updated doc:

## Verified outcome

Command: `python -m scripts.update_document data/corpus/05_dress_code.md`

First run:

```text
Update complete for 05_dress_code.md:
  Tombstoned: 40 old chunks
  Ingested:   14 new chunks
  Cache cleared: 1 entries
```
    
Second run:

```text
Update complete for 05_dress_code.md:
  Tombstoned: 14 old chunks
  Ingested:   14 new chunks
  Cache cleared: 0 entries
```

The first run also replaced 40 pre-existing chunks from older ingestion with
14 chunks using the current chunking logic. On the second run, those 14 chunks
were tombstoned and replaced by 14 chunks. The cache was cleared after the
first update; it had no entries to clear after the second.