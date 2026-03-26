"""Ingestion script — loads EU AI Act text into ChromaDB vector store.

Supports two modes:
1. Full corpus: Load from eu_ai_act_chunks.json (fetched from EUR-Lex)
2. Fallback: Load minimal hand-written summaries if JSON not available

Run: python -m app.services.ingest_ai_act
     python -m app.services.ingest_ai_act --reset  (clear and re-ingest)
"""

import asyncio
import json
import os
import sys

from app.services.rag import ingest_document, get_collection

CHUNKS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "eu_ai_act_chunks.json"
)


async def ingest_from_json(reset: bool = False) -> int:
    """Ingest EU AI Act chunks from the JSON file produced by fetch_eu_ai_act.py.

    Args:
        reset: If True, clear existing collection before ingesting.

    Returns:
        Number of documents ingested.
    """
    collection = get_collection()

    if reset and collection.count() > 0:
        print(f"Clearing existing {collection.count()} documents...")
        all_ids = collection.get()["ids"]
        if all_ids:
            # Delete in batches of 500
            for i in range(0, len(all_ids), 500):
                batch = all_ids[i : i + 500]
                collection.delete(ids=batch)
        print("Collection cleared.")

    if collection.count() > 0 and not reset:
        print(
            f"Collection already contains {collection.count()} documents. "
            f"Use --reset to clear and re-ingest."
        )
        return collection.count()

    if not os.path.exists(CHUNKS_PATH):
        print(f"Chunks file not found at {CHUNKS_PATH}")
        print("Run 'python -m app.services.fetch_eu_ai_act' first to fetch the full text.")
        return 0

    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    # Deduplicate by ID — keep first occurrence
    seen_ids: set[str] = set()
    unique_chunks = []
    for chunk in chunks:
        if chunk["id"] not in seen_ids:
            seen_ids.add(chunk["id"])
            unique_chunks.append(chunk)
    chunks = unique_chunks

    print(f"Ingesting {len(chunks)} unique chunks into ChromaDB...")

    count = 0
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]

        ids = [chunk["id"] for chunk in batch]
        documents = [chunk["text"] for chunk in batch]
        metadatas = [
            {"source": chunk["source"], "chapter": chunk["chapter"]}
            for chunk in batch
        ]

        collection.add(documents=documents, metadatas=metadatas, ids=ids)
        count += len(batch)

        if count % 500 == 0 or count == len(chunks):
            print(f"  Ingested {count}/{len(chunks)} chunks...")

    print(f"\nTotal documents ingested: {count}")
    print(f"Collection now contains: {collection.count()} documents")
    return count


async def ingest_eu_ai_act() -> int:
    """Main ingestion entrypoint."""
    reset = "--reset" in sys.argv
    return await ingest_from_json(reset=reset)


if __name__ == "__main__":
    asyncio.run(ingest_eu_ai_act())
