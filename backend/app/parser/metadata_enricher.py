
import hashlib
from pathlib import Path


LANGUAGE_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".h": "C/C++",
    ".cs": "C#",
    ".go": "Go",
    ".rs": "Rust",
    ".php": "PHP",
    ".rb": "Ruby"
}


def enrich_chunks(chunks, file_path, repo_root, repository):
    """Attach standardized metadata to parsed code chunks."""

    root = Path(repo_root).resolve()
    source_file = Path(file_path).resolve()

    if not source_file.is_relative_to(root):
        raise ValueError("Source file must be inside the repository.")

    relative_path = source_file.relative_to(root).as_posix()

    language = LANGUAGE_MAP.get(source_file.suffix.lower())

    if not language:
        raise ValueError("Unsupported programming language.")

    enriched_chunks = []

    for chunk in chunks:

        code = chunk["code"]
        name = chunk["name"]
        start_line = chunk["start_line"]
        end_line = chunk["end_line"]

        # Generate a deterministic ID for this code chunk
        unique_value = (
            f"{repository}:{relative_path}:"
            f"{name}:{start_line}:{end_line}:{code}"
        )

        chunk_id = hashlib.sha256(
            unique_value.encode("utf-8")
        ).hexdigest()

        enriched_chunk = {
            "chunk_id": chunk_id,
            "repository": repository,
            "name": name,
            "type": chunk["type"],
            "file_path": relative_path,
            "language": language,
            "parent_class": chunk.get("parent_class"),
            "start_line": start_line,
            "end_line": end_line,
            "imports": chunk.get("imports", []),
            "code": code
        }

        enriched_chunks.append(enriched_chunk)

    return enriched_chunks
