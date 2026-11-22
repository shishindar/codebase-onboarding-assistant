
import pytest
from backend.app.retrieval.bm25_search import search_bm25


def test_bm25_search_returns_results():
    results = search_bm25(
        query="get HTTP request",
        repository="psf__requests",
        top_k=5
    )

    assert len(results) > 0

    for result in results:
        assert result["name"]
        assert result["file_path"]
        assert result["code"]
        assert result["bm25_score"] > 0


def test_bm25_rejects_empty_query():
    with pytest.raises(ValueError):
        search_bm25("")


def test_bm25_rejects_invalid_top_k():
    with pytest.raises(ValueError):
        search_bm25("get request", top_k=0)
