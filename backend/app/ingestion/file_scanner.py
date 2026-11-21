
from pathlib import Path

IGNORED_DIRS = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    ".next",
    ".idea",
    ".vscode",
    "coverage"
}

SUPPORTED_EXTENSIONS = {
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

MAX_FILE_SIZE = 500 * 1024


def scan_repository(repo_path: str) -> list:
    """Find supported source files in a repository."""

    root = Path(repo_path).resolve()
    files = []

    for current_path, directories, filenames in __import__("os").walk(root):

        directories[:] = [
            directory for directory in directories
            if directory not in IGNORED_DIRS
        ]

        for filename in filenames:
            file_path = Path(current_path) / filename

            if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            try:
                if file_path.is_symlink():
                    continue

                resolved_path = file_path.resolve()

                if not resolved_path.is_relative_to(root):
                    continue

                if resolved_path.stat().st_size > MAX_FILE_SIZE:
                    continue

                files.append({
                    "file_path": str(resolved_path.relative_to(root)),
                    "language": SUPPORTED_EXTENSIONS[file_path.suffix.lower()],
                    "size": resolved_path.stat().st_size
                })

            except (OSError, ValueError):
                continue

    return files
