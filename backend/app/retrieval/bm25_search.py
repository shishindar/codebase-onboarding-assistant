
import re
from rank_bm25 import BM25Okapi
from backend.app.retrieval.vector_store import get_collection


def tokenize(text: str):
    """Split code into searchable words and identifiers."""
    return re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*|[0-9]+", text.lower())


def search_bm25(
    query: str,
    repository: str | None = None,
    top_k: int = 5
):
    """Search indexed code using BM25 keyword matching."""

    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    if not 1 <= top_k <= 20:
        raise ValueError("top_k must be between 1 and 20.")

    collection = get_collection()

    where = {"repository": repository} if repository else None

    stored_data = collection.get(
        where=where,
        include=["documents", "metadatas"]
    )

    documents = stored_data["documents"]
    metadatas = stored_data["metadatas"]
    ids = stored_data["ids"]

    if not documents:
        return []

    tokenized_documents = []

    for document, metadata in zip(documents, metadatas):
        searchable_text = (
            f"{metadata.get('name', '')} "
            f"{metadata.get('file_path', '')} "
            f"{document}"
        )
        tokenized_documents.append(tokenize(searchable_text))

    bm25 = BM25Okapi(tokenized_documents)
    query_tokens = tokenize(query)

    scores = bm25.get_scores(query_tokens)

    ranked_indices = sorted(
        range(len(scores)),
        key=lambda index: scores[index],
        reverse=True
    )

    results = []

    for index in ranked_indices:
        score = float(scores[index])

        if score <= 0:
            continue

        metadata = metadatas[index]

        results.append({
            "chunk_id": ids[index],
            "code": documents[index],
            "name": metadata["name"],
            "type": metadata["type"],
            "repository": metadata["repository"],
            "file_path": metadata["file_path"],
            "language": metadata["language"],
            "parent_class": metadata["parent_class"] or None,
            "start_line": metadata["start_line"],
            "end_line": metadata["end_line"],
            "imports": metadata["imports"],
            "bm25_score": score
        })

        if len(results) == top_k:
            break

    return results
