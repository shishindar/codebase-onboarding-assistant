
import json
from pathlib import Path

import chromadb


PROJECT_ROOT = Path(__file__).resolve().parents[3]

CHROMA_PATH = PROJECT_ROOT / "data" / "chroma_db"

COLLECTION_NAME = "codebase_chunks"


def get_collection():
    """Create or retrieve the persistent ChromaDB collection."""

    CHROMA_PATH.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(
        path=str(CHROMA_PATH)
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    return collection


def store_chunks(chunks, embeddings):
    """Store code chunks, embeddings and metadata in ChromaDB."""

    if len(chunks) != len(embeddings):
        raise ValueError("Chunks and embeddings count must match.")

    if not chunks:
        return 0

    collection = get_collection()

    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:

        ids.append(chunk["chunk_id"])

        documents.append(chunk["code"])

        metadatas.append({
            "repository": chunk["repository"],
            "name": chunk["name"],
            "type": chunk["type"],
            "file_path": chunk["file_path"],
            "language": chunk["language"],
            "parent_class": chunk.get("parent_class") or "",
            "start_line": chunk["start_line"],
            "end_line": chunk["end_line"],
            "imports": json.dumps(chunk.get("imports", []))
        })

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )

    return len(ids)


def get_collection_stats():
    """Return the number of stored code chunks."""

    collection = get_collection()

    return {
        "collection": COLLECTION_NAME,
        "total_chunks": collection.count()
    }
