
from backend.app.retrieval.search_service import search_code
from backend.app.retrieval.bm25_search import search_bm25


RRF_K = 60


def hybrid_search(
    query: str,
    repository: str | None = None,
    top_k: int = 5
):
    """Combine vector and BM25 search using Reciprocal Rank Fusion."""

    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    if not 1 <= top_k <= 20:
        raise ValueError("top_k must be between 1 and 20.")

    # Retrieve candidates from both search systems.
    vector_results = search_code(
        query=query,
        repository=repository,
        top_k=20
    )

    bm25_results = search_bm25(
        query=query,
        repository=repository,
        top_k=20
    )

    combined = {}

    # Add vector search rankings.
    for rank, result in enumerate(vector_results, start=1):
        chunk_id = result["chunk_id"]

        combined[chunk_id] = result.copy()
        combined[chunk_id]["rrf_score"] = 1 / (RRF_K + rank)
        combined[chunk_id]["vector_rank"] = rank
        combined[chunk_id]["bm25_rank"] = None
        combined[chunk_id]["search_methods"] = ["vector"]

    # Add BM25 rankings and combine scores.
    for rank, result in enumerate(bm25_results, start=1):
        chunk_id = result["chunk_id"]

        if chunk_id in combined:
            combined[chunk_id]["rrf_score"] += 1 / (RRF_K + rank)
            combined[chunk_id]["bm25_rank"] = rank
            combined[chunk_id]["search_methods"].append("bm25")
        else:
            combined[chunk_id] = result.copy()
            combined[chunk_id]["rrf_score"] = 1 / (RRF_K + rank)
            combined[chunk_id]["vector_rank"] = None
            combined[chunk_id]["bm25_rank"] = rank
            combined[chunk_id]["search_methods"] = ["bm25"]

    # Sort by combined RRF score.
    ranked_results = sorted(
        combined.values(),
        key=lambda item: item["rrf_score"],
        reverse=True
    )

    return ranked_results[:top_k]

