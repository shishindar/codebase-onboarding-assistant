
from pathlib import Path

from backend.app.ingestion.file_scanner import scan_repository
from backend.app.parser.code_parser import parse_python_file
from backend.app.parser.metadata_enricher import enrich_chunks
from backend.app.embeddings.embedding_service import generate_embeddings
from backend.app.retrieval.vector_store import store_chunks, get_collection_stats


def index_repository(repo_path: str, repository_name: str):
    """Parse, enrich, embed and store a Python repository."""

    root = Path(repo_path).resolve()

    if not root.is_dir():
        raise ValueError("Repository directory does not exist.")

    files = scan_repository(str(root))

    all_chunks = []

    for item in files:

        if item["language"] != "Python":
            continue

        file_path = root / item["file_path"]

        parsed_chunks = parse_python_file(str(file_path))

        enriched_chunks = enrich_chunks(
            parsed_chunks,
            file_path,
            root,
            repository_name
        )

        all_chunks.extend(enriched_chunks)

    if not all_chunks:
        return {
            "repository": repository_name,
            "indexed_chunks": 0,
            "database": get_collection_stats()
        }

    embeddings = generate_embeddings(all_chunks)

    stored_count = store_chunks(
        all_chunks,
        embeddings
    )

    return {
        "repository": repository_name,
        "scanned_files": len(files),
        "indexed_chunks": stored_count,
        "database": get_collection_stats()
    }
