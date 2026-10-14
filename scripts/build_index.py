"""Build the RAG index. Run once, or whenever the corpus changes."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.rag.naive_rag import load_corpus, build_index, save_index

CORPUS_DIR = PROJECT_ROOT / "data" / "corpus"
INDEX_PATH = PROJECT_ROOT / "data" / "embeddings.json"

print(f"Loading corpus from {CORPUS_DIR}...")
chunks = load_corpus(CORPUS_DIR)
print(f"  {len(chunks)} chunks loaded.")

print(f"Building embeddings (this may take a minute)...")
build_index(chunks)

print(f"Saving to {INDEX_PATH}...")
save_index(chunks, INDEX_PATH)
print(f"Done. Index has {len(chunks)} chunks.")
