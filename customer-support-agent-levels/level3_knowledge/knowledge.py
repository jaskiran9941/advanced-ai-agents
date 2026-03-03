"""
knowledge.py — Level 3
======================
Loads the 5 Acme Shop policy docs into ChromaDB and exposes a search function.

First run: ChromaDB downloads the all-MiniLM-L6-v2 embedding model (~90MB).
Subsequent runs: instant — the collection is persisted to chroma_db/ on disk.

How it works:
  1. Each policy doc is turned into a vector (list of ~384 numbers) by the model.
  2. When search_policies("can I return after 45 days") is called:
     - The query is also turned into a vector.
     - ChromaDB finds the doc vectors closest to the query vector.
     - Returns the most relevant policy text.
  This is why it beats keyword search: "return after 45 days" matches
  "30-day return window" even though none of those exact words overlap.
"""

import os
import sys
import chromadb

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from shared.data import POLICIES

# Persist the DB next to this file so it survives restarts
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")

_collection = None  # module-level cache — only build once per session


def _get_collection():
    """Lazy-load: build the ChromaDB collection on first call, reuse after."""
    global _collection
    if _collection is not None:
        return _collection

    # PersistentClient saves to disk — embeddings survive app restarts
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # get_or_create: safe to call on every startup
    collection = client.get_or_create_collection(
        name="acme_policies",
        # No embedding_function specified → uses ChromaDB's default
        # (sentence-transformers all-MiniLM-L6-v2, downloaded on first use)
    )

    # Only add docs if the collection is empty (first run)
    if collection.count() == 0:
        collection.add(
            ids=[doc["id"] for doc in POLICIES],
            documents=[doc["content"] for doc in POLICIES],
            metadatas=[{"title": doc["title"]} for doc in POLICIES],
        )

    _collection = collection
    return _collection


def search_policies(query: str, n_results: int = 2) -> list[dict]:
    """
    Search policy docs by semantic similarity to the query.
    Returns a list of {title, content, relevance_score} dicts.
    """
    collection = _get_collection()

    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append({
            "title": meta["title"],
            "content": doc,
            # Distance → similarity score (lower distance = more relevant)
            "relevance_score": round(1 - dist, 3),
        })

    return hits
