
from backend.app.embeddings.embedding_service import get_embedding_model
from backend.app.retrieval.vector_store import get_collection


def search_code(query: str, repository: str | None = None, top_k: int = 5):
    """Find relevant code using semantic vector search."""

    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    if not 1 <= top_k <= 20:
        raise ValueError("top_k must be between 1 and 20.")

    collection = get_collection()

    if collection.count() == 0:
        return []

    model = get_embedding_model()

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True
    ).tolist()

    where = {"repository": repository} if repository else None

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(top_k, collection.count()),
        where=where,
        include=["documents", "metadatas", "distances"]
    )

    matches = []

    for i in range(len(results["ids"][0])):

        metadata = results["metadatas"][0][i]
        distance = results["distances"][0][i]

        matches.append({
            "chunk_id": results["ids"][0][i],
            "code": results["documents"][0][i],
            "name": metadata["name"],
            "type": metadata["type"],
            "repository": metadata["repository"],
            "file_path": metadata["file_path"],
            "language": metadata["language"],
            "parent_class": metadata["parent_class"] or None,
            "start_line": metadata["start_line"],
            "end_line": metadata["end_line"],
            "imports": metadata["imports"],
            "distance": distance,
            "similarity": 1 - distance
        })

    return matches
