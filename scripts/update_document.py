"""Update a single document in the capstone KB.

Usage:
    python -m scripts.update_document data/policies/leave.md
"""

import sys
from pathlib import Path

from src.rag.pipeline import ingest_or_update_source
from src.rag.qdrant_store import QdrantStore, W9_COLLECTION_NAME, _get_client


def main(doc_path: str):
    path = Path(doc_path)
    assert path.exists(), f"Not found: {path}"
    body = path.read_text()
    source = path.name

    store = QdrantStore(client=_get_client(), collection=W9_COLLECTION_NAME)
    result = ingest_or_update_source(store, source, body)

    print(f"Update complete for {source}:")
    print(f"  Tombstoned: {result['tombstoned']} old chunks")
    print(f"  Ingested:   {result['ingested']} new chunks")
    print(f"  Cache cleared: {result['cache_cleared']} entries")


if __name__ == "__main__":
    main(sys.argv[1])
