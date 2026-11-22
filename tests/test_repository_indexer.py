
from pathlib import Path

from backend.app.ingestion.repository_indexer import index_repository


def test_index_repository():

    repo_path = Path("data/repositories/psf__requests")

    result = index_repository(
        str(repo_path),
        "psf__requests"
    )

    assert result["indexed_chunks"] > 0
    assert result["database"]["total_chunks"] > 0
