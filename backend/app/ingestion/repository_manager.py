
import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Where cloned repositories will be stored
REPOSITORY_DIR = PROJECT_ROOT / "data" / "repositories"


def validate_github_url(repo_url: str) -> tuple[str, str]:
    """Validate GitHub URL and extract owner and repository name."""

    parsed = urlparse(repo_url.strip())

    if parsed.scheme != "https" or parsed.hostname != "github.com":
        raise ValueError("Only HTTPS GitHub repository URLs are supported.")

    if parsed.query or parsed.fragment:
        raise ValueError("Invalid GitHub repository URL.")

    parts = [part for part in parsed.path.strip("/").split("/") if part]

    if len(parts) != 2:
        raise ValueError("Expected URL format: https://github.com/owner/repo")

    owner, repo = parts
    repo = repo.removesuffix(".git")

    if not re.fullmatch(r"[A-Za-z0-9_.-]+", owner):
        raise ValueError("Invalid GitHub owner name.")

    if not re.fullmatch(r"[A-Za-z0-9_.-]+", repo):
        raise ValueError("Invalid repository name.")

    return owner, repo


def clone_repository(repo_url: str) -> dict:
    """Clone a GitHub repository into the project data directory."""

    owner, repo = validate_github_url(repo_url)

    REPOSITORY_DIR.mkdir(parents=True, exist_ok=True)

    destination = REPOSITORY_DIR / f"{owner}__{repo}"

    if destination.exists():
        raise FileExistsError(
            "Repository already exists. Remove it before cloning again."
        )

    result = subprocess.run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "--",
            repo_url.strip(),
            str(destination)
        ],
        capture_output=True,
        text=True,
        timeout=180
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip() or "Git clone failed."
        )

    return {
        "owner": owner,
        "repository": repo,
        "local_path": str(destination),
        "status": "cloned"
    }
