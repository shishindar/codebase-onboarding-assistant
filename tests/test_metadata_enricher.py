
from backend.app.parser.metadata_enricher import enrich_chunks


def test_metadata_enrichment(tmp_path):

    repo = tmp_path / "sample_repo"
    repo.mkdir()

    source_file = repo / "sample.py"
    source_file.write_text("def login():\n    return True\n")

    chunks = [
        {
            "name": "login",
            "type": "function",
            "parent_class": None,
            "start_line": 1,
            "end_line": 2,
            "imports": ["import os"],
            "code": "def login():\n    return True"
        }
    ]

    result = enrich_chunks(
        chunks,
        source_file,
        repo,
        "sample_repo"
    )

    assert len(result) == 1

    chunk = result[0]

    assert chunk["name"] == "login"
    assert chunk["type"] == "function"
    assert chunk["file_path"] == "sample.py"
    assert chunk["language"] == "Python"
    assert chunk["repository"] == "sample_repo"
    assert chunk["start_line"] == 1
    assert chunk["end_line"] == 2
    assert chunk["imports"] == ["import os"]
    assert len(chunk["chunk_id"]) == 64


def test_chunk_id_is_deterministic(tmp_path):

    repo = tmp_path / "sample_repo"
    repo.mkdir()

    source_file = repo / "sample.py"
    source_file.write_text("def login():\n    return True\n")

    chunks = [{
        "name": "login",
        "type": "function",
        "parent_class": None,
        "start_line": 1,
        "end_line": 2,
        "imports": [],
        "code": "def login():\n    return True"
    }]

    first = enrich_chunks(chunks, source_file, repo, "sample_repo")
    second = enrich_chunks(chunks, source_file, repo, "sample_repo")

    assert first[0]["chunk_id"] == second[0]["chunk_id"]

