"""MP2 · Mini-RAG — Starter Template
====================================

You'll build a complete RAG pipeline over the Sherlock Holmes corpus in this
file. Fill in every TODO. The reference solution is ~250 lines, but yours can
be shorter or longer — what matters is that it works end-to-end.

Pipeline you're building:
    corpus/*.txt  →  chunks  →  embeddings  →  Qdrant
                                                  ↓
                              question  →  retrieve  →  answer + citations

Run sequence (once you've filled in the TODOs):
    pip install -r requirements.txt
    source .env                 # exports your OpenAI + Qdrant credentials
    python mp2_rag.py ingest    # builds the collection (run once)
    python mp2_rag.py ask       # interactive Q&A loop
    python mp2_rag.py validate  # runs against data/predefined_questions.jsonl

Tip: get the CORE pipeline working FIRST (Steps 1-7 below), THEN come back to
polish and add your 3 questions. Don't try to perfect each step before moving
on — you'll learn more from a rough end-to-end loop than a polished half.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

# ─── Configuration ──────────────────────────────────────────────────────

CORPUS_DIR        = Path(__file__).parent / "corpus"
DATA_DIR          = Path(__file__).parent / "data"
COLLECTION_NAME   = "mp2_sherlock"
EMBEDDING_MODEL   = "text-embedding-3-small"
EMBEDDING_DIM     = 1536
EMBEDDING_BATCH_SIZE = 100
CHAT_MODEL        = "gpt-4o-mini"
TARGET_CHUNK_SIZE = 500   # characters
CHUNK_OVERLAP     = 80    # characters

openai = OpenAI()
qdrant = QdrantClient(
    url=os.environ["QDRANT_URL"],
    api_key=os.environ.get("QDRANT_API_KEY"),
)


# ─── Step 1: Load the corpus ────────────────────────────────────────────

def load_corpus(corpus_dir: Path) -> list[dict[str, Any]]:
    """Read every .txt file in the corpus directory.

    Returns a list of dicts, each with: source (filename), title (first line),
    and text (full content).

    TODO:
      - Iterate over every *.txt file in corpus_dir (use Path.glob)
      - For each file, read its text and extract the first non-empty line as title
      - Return the list of doc dicts
    """
    docs = []
    for path in sorted(corpus_dir.glob("*.txt")):
        text = path.read_text(encoding="utf-8")
        title = next((line.strip() for line in text.splitlines() if line.strip()), "")
        docs.append({"source": path.name, "title": title, "text": text})
    return docs


# ─── Step 2: Chunk each document ────────────────────────────────────────

def chunk_document(doc: dict[str, Any]) -> list[dict[str, Any]]:
    """Split a document into smaller chunks.

    Each chunk should be a dict with: source, title, section, text.

    Paragraphs are packed up to TARGET_CHUNK_SIZE characters. Short lines
    without terminal punctuation mark section boundaries; oversized
    paragraphs are split on sentence boundaries where possible, with overlap.
    """
    chunks: list[dict[str, Any]] = []
    title = str(doc.get("title", ""))
    section = title
    paragraphs: list[str] = []
    paragraph_length = 0

    def flush() -> None:
        nonlocal paragraph_length
        if paragraphs:
            chunks.append({
                "source": doc["source"],
                "title": title,
                "section": section,
                "text": "\n\n".join(paragraphs),
            })
            paragraphs.clear()
            paragraph_length = 0

    def add_chunk(text: str) -> None:
        chunks.append({
            "source": doc["source"],
            "title": title,
            "section": section,
            "text": text,
        })

    for raw_paragraph in re.split(r"\n\s*\n", str(doc.get("text", ""))):
        paragraph = raw_paragraph.strip()
        if not paragraph:
            continue

        if paragraph == title and not chunks and not paragraphs:
            continue

        if len(paragraph) <= 80 and not re.search(r"[.!?][\"')\]]?$", paragraph):
            flush()
            section = paragraph
            continue

        if len(paragraph) > TARGET_CHUNK_SIZE:
            flush()
            start = 0
            while start < len(paragraph):
                end = min(start + TARGET_CHUNK_SIZE, len(paragraph))
                if end < len(paragraph):
                    window = paragraph[start:end]
                    sentence_boundaries = [
                        match.end()
                        for match in re.finditer(
                            r"""[.!?](?:["')\]]*)?(?=\s)""", window
                        )
                    ]
                    sentence_boundary = (
                        sentence_boundaries[-1] if sentence_boundaries else 0
                    )
                    if sentence_boundary >= TARGET_CHUNK_SIZE // 2:
                        end = start + sentence_boundary
                    else:
                        word_boundary = paragraph.rfind(" ", start, end)
                        if word_boundary > start:
                            end = word_boundary
                add_chunk(paragraph[start:end].strip())
                if end == len(paragraph):
                    break
                start = max(start + 1, end - CHUNK_OVERLAP)
                if start < end:
                    next_word = paragraph.find(" ", start, end)
                    if next_word >= 0:
                        start = next_word + 1
                while start < len(paragraph) and paragraph[start].isspace():
                    start += 1
            continue

        added_length = len(paragraph) + (2 if paragraphs else 0)
        if paragraph_length + added_length > TARGET_CHUNK_SIZE:
            flush()
            added_length = len(paragraph)
        paragraphs.append(paragraph)
        paragraph_length += added_length

    flush()
    return chunks


# ─── Step 3: Embed text ─────────────────────────────────────────────────

def embed_texts(texts: list[str]) -> list[list[float]]:
    """Batch-embed a list of texts using OpenAI's embedding model.

    Returns a list of 1536-dim float vectors (same order as inputs).

    TODO:
      - Call openai.embeddings.create with EMBEDDING_MODEL and the texts
      - Extract the embedding vectors from the response
    """
    embeddings: list[list[float]] = []
    for start in range(0, len(texts), EMBEDDING_BATCH_SIZE):
        batch = texts[start : start + EMBEDDING_BATCH_SIZE]
        response = openai.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        embeddings.extend(
            item.embedding for item in sorted(response.data, key=lambda item: item.index)
        )
    return embeddings


# ─── Step 4: Set up the Qdrant collection ───────────────────────────────

def setup_collection() -> None:
    """Create (or recreate) the Qdrant collection.

    Recreating clears existing points before creating the collection.
    """
    if qdrant.collection_exists(COLLECTION_NAME):
        deleted = qdrant.delete_collection(collection_name=COLLECTION_NAME)
        if not deleted:
            raise RuntimeError(
                f"Failed to delete existing Qdrant collection {COLLECTION_NAME!r}"
            )

    created = qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=EMBEDDING_DIM,
            distance=Distance.COSINE,
        ),
    )
    if not created:
        raise RuntimeError(f"Failed to create Qdrant collection {COLLECTION_NAME!r}")


# ─── Step 5: Ingest chunks into Qdrant ──────────────────────────────────

def ingest_chunks(chunks: list[dict[str, Any]]) -> None:
    """Embed every chunk and upsert into Qdrant.

    TODO:
      - Call embed_texts on the chunk texts
      - Build PointStruct objects (id=uuid, vector, payload=chunk dict)
      - qdrant.upsert
    """
    if not chunks:
        return

    texts: list[str] = []
    for index, chunk in enumerate(chunks):
        text = chunk.get("text")
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"Chunk at index {index} must contain non-empty text")
        texts.append(text)

    vectors = embed_texts(texts)
    if len(vectors) != len(chunks):
        raise ValueError(
            f"Expected {len(chunks)} embeddings, received {len(vectors)}"
        )

    points = []
    for index, (chunk, vector) in enumerate(zip(chunks, vectors)):
        if len(vector) != EMBEDDING_DIM:
            raise ValueError(
                f"Embedding at index {index} has dimension {len(vector)}; "
                f"expected {EMBEDDING_DIM}"
            )
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload=chunk,
            )
        )

    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)


# ─── Step 6: Retrieve ───────────────────────────────────────────────────

def retrieve(query: str, k: int = 3) -> list[dict[str, Any]]:
    """Retrieve top-k chunks for a query.

    Returns the stored chunk payloads with a relevance score for citations.
    """
    if not query.strip():
        raise ValueError("Query must not be empty")
    if k < 1:
        raise ValueError("k must be at least 1")

    query_vectors = embed_texts([query])
    if len(query_vectors) != 1:
        raise ValueError(
            f"Expected 1 query embedding, received {len(query_vectors)}"
        )
    query_vector = query_vectors[0]
    if len(query_vector) != EMBEDDING_DIM:
        raise ValueError(
            f"Query embedding has dimension {len(query_vector)}; "
            f"expected {EMBEDDING_DIM}"
        )

    response = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=k,
        with_payload=True,
    )

    results: list[dict[str, Any]] = []
    for hit in response.points:
        if hit.payload is None:
            raise ValueError(f"Qdrant point {hit.id!r} is missing its payload")
        results.append({**hit.payload, "score": hit.score})
    return results


# ─── Step 7: Generate the answer ────────────────────────────────────────

SYSTEM_PROMPT = """You are a helpful assistant answering questions about a small
collection of Sherlock Holmes stories. You will be given the user's question and
several relevant excerpts. Use ONLY the provided excerpts to answer. If the
excerpts don't contain the answer, say so plainly. Cite the source (story title
+ section) in your answer."""


def answer(question: str, k: int = 3) -> dict[str, Any]:
    """End-to-end: retrieve, format context, call LLM, return result.

    Returns the generated answer, retrieved citations, and elapsed time in ms.
    """
    started_at = time.perf_counter()
    retrieved = retrieve(question, k=k)

    context_parts: list[str] = []
    citations: list[dict[str, Any]] = []
    for index, chunk in enumerate(retrieved):
        title = chunk.get("title")
        section = chunk.get("section")
        source = chunk.get("source")
        text = chunk.get("text")
        if not all(isinstance(value, str) and value.strip() for value in (
            title,
            section,
            source,
            text,
        )):
            raise ValueError(
                f"Retrieved chunk at index {index} is missing source, title, "
                "section, or text metadata"
            )

        context_parts.append(
            f"[Source: {title} — {section}]\n{text}"
        )
        citation = {
            "source": source,
            "title": title,
            "section": section,
        }
        if "score" in chunk:
            citation["score"] = chunk["score"]
        citations.append(citation)

    context = "\n\n".join(context_parts) or "(No relevant excerpts were retrieved.)"
    response = openai.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Question: {question}\n\nExcerpts:\n{context}",
            },
        ],
    )
    if not response.choices:
        raise RuntimeError("Chat completion returned no choices")
    answer_text = response.choices[0].message.content
    if answer_text is None:
        raise RuntimeError("Chat completion returned no answer text")

    return {
        "question": question,
        "answer": answer_text,
        "citations": citations,
        "latency_ms": round((time.perf_counter() - started_at) * 1000),
    }


# ─── Validation harness (provided — do not modify) ──────────────────────

def validate_against(jsonl_path: Path) -> None:
    questions = [json.loads(line) for line in jsonl_path.read_text().splitlines() if line.strip()]
    print(f"\n  Validating {len(questions)} questions from {jsonl_path.name}…\n")

    hits = 0
    for q in questions:
        result = answer(q["question"], k=3)
        cited_sources = {cit["source"] for cit in result["citations"]}
        source_hit = q["expected_source"] in cited_sources

        ans_lower = result["answer"].lower()
        facts_hit = sum(1 for fact in q.get("expected_facts", []) if fact.lower() in ans_lower)
        facts_total = len(q.get("expected_facts", []))

        verdict = "✓" if source_hit else "✗"
        print(f"  {verdict} {q['id']}")
        print(f"      Q: {q['question']}")
        print(f"      Cited: {', '.join(cited_sources)}")
        print(f"      Expected: {q['expected_source']}")
        print(f"      Facts matched: {facts_hit}/{facts_total}")
        print(f"      Latency: {result.get('latency_ms', '?')}ms")
        print()
        if source_hit:
            hits += 1

    print(f"  Source-match: {hits}/{len(questions)}")


# ─── CLI (provided — do not modify) ─────────────────────────────────────

def cmd_ingest() -> None:
    print("→ Loading corpus…")
    docs = load_corpus(CORPUS_DIR)
    print(f"  {len(docs)} documents loaded")

    print("→ Chunking…")
    all_chunks: list[dict[str, Any]] = []
    for doc in docs:
        chunks = chunk_document(doc)
        all_chunks.extend(chunks)
        print(f"  {doc['source']}: {len(chunks)} chunks")

    print(f"→ Total chunks: {len(all_chunks)}")
    print("→ Setting up Qdrant collection…")
    setup_collection()

    print("→ Ingesting…")
    ingest_chunks(all_chunks)
    print("\n✓ Done. Try: python mp2_rag.py ask")


def cmd_ask() -> None:
    print("Mini-RAG over the Sherlock Holmes corpus.")
    print("Type your question. Empty line or Ctrl-C to exit.\n")
    while True:
        try:
            q = input("? ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not q:
            return
        result = answer(q, k=3)
        print(f"\n{result['answer']}\n")
        print("  Sources:")
        for c in result["citations"]:
            print(f"    - {c['title']} — {c['section']}")
        print(f"  Latency: {result.get('latency_ms', '?')}ms\n")


def cmd_validate() -> None:
    validate_against(DATA_DIR / "predefined_questions.jsonl")
    learner_path = DATA_DIR / "learner_questions.jsonl"
    if learner_path.exists():
        first = json.loads(learner_path.read_text().splitlines()[0])
        if not first["question"].startswith("Replace this"):
            validate_against(learner_path)


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    cmd = sys.argv[1]
    if cmd == "ingest":   cmd_ingest()
    elif cmd == "ask":    cmd_ask()
    elif cmd == "validate": cmd_validate()
    else:
        print(f"Unknown command: {cmd}\n")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
