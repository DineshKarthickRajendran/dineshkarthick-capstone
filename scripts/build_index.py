"""Build the RAG index. Run once, or whenever the corpus changes."""

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.rag.naive_rag import load_corpus, build_index, save_index

CORPUS_DIR = ROOT_DIR / "data/corpus"
INDEX_PATH = ROOT_DIR / "data/embeddings.json"

print(f"Loading corpus from {CORPUS_DIR}...")
chunks = load_corpus(CORPUS_DIR)
print(f"  {len(chunks)} chunks loaded.")

print(f"Building embeddings (this may take a minute)...")
build_index(chunks)

print(f"Saving to {INDEX_PATH}...")
save_index(chunks, INDEX_PATH)
print(f"Done. Index has {len(chunks)} chunks.")
