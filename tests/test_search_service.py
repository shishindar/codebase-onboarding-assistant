
import pytest

from backend.app.retrieval.search_service import search_code


def test_search_code_returns_results():

    results = search_code(
        query="How are HTTP GET requests implemented?",
        repository="psf__requests",
        top_k=5
    )

    assert len(results) > 0

    for result in results:
        assert result["name"]
        assert result["file_path"]
        assert result["start_line"] > 0
        assert result["end_line"] >= result["start_line"]
        assert result["code"]
        assert result["similarity"] is not None


def test_search_code_rejects_empty_query():

    with pytest.raises(ValueError):
        search_code("")


def test_search_code_rejects_invalid_top_k():

    with pytest.raises(ValueError):
        search_code("authentication", top_k=0)
