"""URL building utilities for Git Identify."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
import re


@dataclass
class GitHubInfo:
    """Information about a GitHub repository."""

    owner: str
    repo: str


def parse_remote_url(remote_url: str) -> GitHubInfo:
    """
    Parse a Git remote URL to extract GitHub repository information.

    Args:
        remote_url: Remote URL (SSH or HTTPS format)

    Returns:
        GitHubInfo object with owner and repo name

    Raises:
        ValueError: If URL format is not supported or invalid
    """
    # SSH format: git@github.com:owner/repo.git
    ssh_pattern = r"^git@github\.com:([^/]+)/([^/]+?)(\.git)?$"
    ssh_match = re.match(ssh_pattern, remote_url)

    if ssh_match:
        owner = ssh_match.group(1)
        repo = ssh_match.group(2)
        return GitHubInfo(owner=owner, repo=repo)

    # HTTPS/HTTP format: https://github.com/owner/repo.git
    if remote_url.startswith(("https://github.com/", "http://github.com/")):
        parsed = urlparse(remote_url)
        path_parts = parsed.path.strip("/").split("/")

        if len(path_parts) < 2:
            raise ValueError(f"Invalid GitHub repository URL: {remote_url}")

        owner = path_parts[0]
        repo = path_parts[1]
        if repo.endswith(".git"):
            repo = repo[:-4]  # Remove .git extension
        return GitHubInfo(owner=owner, repo=repo)

    raise ValueError(f"Unsupported remote URL format: {remote_url}")


def build_github_url(github_info: GitHubInfo, commit_hash: str, file_path: str) -> str:
    """
    Build a GitHub URL for a specific file at a specific commit.

    Args:
        github_info: GitHub repository information
        commit_hash: SHA-1 hash of the commit
        file_path: Path to the file relative to repository root

    Returns:
        Complete GitHub URL
    """
    normalized_path = normalize_file_path(file_path)
    return f"https://github.com/{github_info.owner}/{github_info.repo}/blob/{commit_hash}/{normalized_path}"


def normalize_file_path(file_path: str) -> str:
    """
    Normalize a file path for use in a GitHub URL.

    Args:
        file_path: File path to normalize

    Returns:
        Normalized path string
    """
    # Handle empty path
    if not file_path:
        return ""

    path = Path(file_path)

    # Remove leading slash if absolute
    if path.is_absolute():
        # Convert to string and remove leading slash
        path_str = str(path).lstrip("/")
    else:
        path_str = str(path)

    # Convert backslashes to forward slashes (Windows compatibility)
    path_str = path_str.replace("\\", "/")

    # Remove any leading slashes that might remain
    path_str = path_str.lstrip("/")

    return path_str


def generate_github_url(remote_url: str, commit_hash: str, file_path: str) -> str:
    """
    Generate a complete GitHub URL from repository information.

    Args:
        remote_url: Git remote URL
        commit_hash: SHA-1 hash of the commit
        file_path: Path to the file relative to repository root

    Returns:
        Complete GitHub URL

    Raises:
        ValueError: If URL cannot be generated
    """
    try:
        github_info = parse_remote_url(remote_url)
        return build_github_url(github_info, commit_hash, file_path)
    except Exception as e:
        raise ValueError(f"Failed to generate GitHub URL: {e}")