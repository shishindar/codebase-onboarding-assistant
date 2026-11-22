
import pytest

from backend.app.retrieval import hybrid_search as hybrid_module


def test_hybrid_search_combines_results(monkeypatch):

    vector_results = [
        {
            "chunk_id": "chunk_1",
            "name": "get",
            "code": "def get(): pass",
            "file_path": "api.py",
            "similarity": 0.9
        },
        {
            "chunk_id": "chunk_2",
            "name": "post",
            "code": "def post(): pass",
            "file_path": "api.py",
            "similarity": 0.8
        }
    ]

    bm25_results = [
        {
            "chunk_id": "chunk_2",
            "name": "post",
            "code": "def post(): pass",
            "file_path": "api.py",
            "bm25_score": 5.0
        },
        {
            "chunk_id": "chunk_3",
            "name": "delete",
            "code": "def delete(): pass",
            "file_path": "api.py",
            "bm25_score": 4.0
        }
    ]

    monkeypatch.setattr(
        hybrid_module,
        "search_code",
        lambda **kwargs: vector_results
    )

    monkeypatch.setattr(
        hybrid_module,
        "search_bm25",
        lambda **kwargs: bm25_results
    )

    results = hybrid_module.hybrid_search(
        query="HTTP request",
        top_k=5
    )

    assert len(results) == 3

    # chunk_2 appears in both search results.
    chunk_2 = next(
        item for item in results
        if item["chunk_id"] == "chunk_2"
    )

    assert chunk_2["vector_rank"] == 2
    assert chunk_2["bm25_rank"] == 1
    assert set(chunk_2["search_methods"]) == {"vector", "bm25"}


def test_hybrid_search_rejects_empty_query():

    with pytest.raises(ValueError):
        hybrid_module.hybrid_search("")


def test_hybrid_search_rejects_invalid_top_k():

    with pytest.raises(ValueError):
        hybrid_module.hybrid_search(
            "HTTP request",
            top_k=0
        )


def test_hybrid_search_returns_top_k_results(monkeypatch):

    vector_results = [
        {
            "chunk_id": f"chunk_{i}",
            "name": f"function_{i}",
            "code": "pass",
            "file_path": "api.py"
        }
        for i in range(10)
    ]

    monkeypatch.setattr(
        hybrid_module,
        "search_code",
        lambda **kwargs: vector_results
    )

    monkeypatch.setattr(
        hybrid_module,
        "search_bm25",
        lambda **kwargs: []
    )

    results = hybrid_module.hybrid_search(
        query="function",
        top_k=3
    )

    assert len(results) == 3

