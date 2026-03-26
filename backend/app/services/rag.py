"""RAG service — manages the EU AI Act vector store and retrieval."""

import os

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import settings

_client: chromadb.ClientAPI | None = None
_collection: chromadb.Collection | None = None

COLLECTION_NAME = "eu_ai_act"


def get_chroma_client() -> chromadb.ClientAPI:
    """Get or create the ChromaDB client."""
    global _client
    if _client is None:
        persist_dir = os.path.abspath(settings.chroma_persist_dir)
        os.makedirs(persist_dir, exist_ok=True)
        _client = chromadb.PersistentClient(
            path=persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _client


def get_collection() -> chromadb.Collection:
    """Get or create the EU AI Act collection."""
    global _collection
    if _collection is None:
        client = get_chroma_client()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "EU AI Act full regulatory text"},
        )
    return _collection


async def query_ai_act(query: str, n_results: int = 5) -> str:
    """Query the EU AI Act vector store for relevant regulatory text.

    Args:
        query: The search query.
        n_results: Number of results to return.

    Returns:
        Concatenated relevant regulatory text passages.
    """
    collection = get_collection()

    if collection.count() == 0:
        return (
            "EU AI Act vector store is empty. Please run the ingestion script "
            "to load the regulatory text. For now, use your training knowledge "
            "of the EU AI Act (Regulation (EU) 2024/1689)."
        )

    results = collection.query(query_texts=[query], n_results=n_results)

    if not results["documents"] or not results["documents"][0]:
        return "No relevant regulatory text found for this query."

    passages = []
    for doc, metadata in zip(
        results["documents"][0], results["metadatas"][0]
    ):
        source = metadata.get("source", "Unknown")
        passages.append(f"[{source}]\n{doc}")

    return "\n\n---\n\n".join(passages)


async def ingest_document(
    text: str, metadata: dict, doc_id: str
) -> None:
    """Ingest a document chunk into the vector store.

    Args:
        text: The text content to ingest.
        metadata: Metadata about the text (source, article number, etc).
        doc_id: Unique identifier for this chunk.
    """
    collection = get_collection()
    collection.add(documents=[text], metadatas=[metadata], ids=[doc_id])
