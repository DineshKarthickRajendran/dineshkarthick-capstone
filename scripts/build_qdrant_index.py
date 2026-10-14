"""Build a fresh Qdrant collection using a selected OpenAI embedding model."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from openai import OpenAI
from qdrant_client.models import Distance, VectorParams

from src.rag.naive_rag import load_corpus
from src.rag.qdrant_store import (
    DEFAULT_EMBEDDING_MODEL,
    EMBEDDING_DIMS,
    load_store,
    upsert_chunks,
)

EMBEDDING_COST_PER_MILLION = {
    "text-embedding-3-small": 0.02,
    "text-embedding-3-large": 0.13,
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--embedding-model",
        choices=EMBEDDING_DIMS,
        default=DEFAULT_EMBEDDING_MODEL,
    )
    parser.add_argument("--collection", required=True)
    parser.add_argument("--batch-size", type=int, default=64)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    store = load_store(collection_name=args.collection)
    existing = {item.name for item in store.client.get_collections().collections}
    dimensions = EMBEDDING_DIMS[args.embedding_model]
    if args.collection in existing:
        info = store.client.get_collection(args.collection)
        vector_config = info.config.params.vectors
        if info.points_count != 0 or vector_config.size != dimensions:
            raise SystemExit(
                f"Collection {args.collection!r} exists with points or incompatible "
                "dimensions; refusing to overwrite it."
            )
        print(f"Resuming empty collection {args.collection!r}")
    else:
        store.client.create_collection(
            collection_name=args.collection,
            vectors_config=VectorParams(size=dimensions, distance=Distance.COSINE),
        )

    chunks = load_corpus(PROJECT_ROOT / "data" / "corpus")
    client = OpenAI()
    vectors: list[list[float]] = []
    total_tokens = 0
    texts = [chunk["text"] for chunk in chunks]
    for offset in range(0, len(texts), args.batch_size):
        response = client.embeddings.create(
            model=args.embedding_model,
            input=texts[offset : offset + args.batch_size],
        )
        vectors.extend(item.embedding for item in response.data)
        total_tokens += response.usage.prompt_tokens
        print(f"Embedded {len(vectors)}/{len(chunks)} chunks")

    upsert_chunks(store, chunks, vectors)
    info = store.client.get_collection(args.collection)
    embedding_cost = (
        total_tokens * EMBEDDING_COST_PER_MILLION[args.embedding_model] / 1_000_000
    )
    print(
        f"Built {args.collection}: points={info.points_count}, dims={dimensions}, "
        f"model={args.embedding_model}, embedding_tokens={total_tokens}, "
        f"embedding_cost=${embedding_cost:.8f}"
    )


if __name__ == "__main__":
    main()
