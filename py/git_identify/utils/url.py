"""
URL parsing and building utilities for GitHub and other Git hosting platforms.

Provides functions for parsing Git remote URLs and building GitHub permalinks.
"""

import re
from typing import Optional

from .path import normalize_file_path


def parse_github_url(remote_url: str) -> Optional[dict[str, str]]:
    """
    Parse a GitHub remote URL to extract owner and repository name.

    Supports both SSH and HTTPS URL formats:
    - SSH: git@github.com:owner/repo.git
    - HTTPS: https://github.com/owner/repo.git

    Also supports GitLab and Bitbucket URLs with similar formats.

    Args:
        remote_url: Git remote URL

    Returns:
        Dictionary with 'owner' and 'repo' keys, or None if parsing fails

    Examples:
        >>> parse_github_url("git@github.com:user/myrepo.git")
        {'owner': 'user', 'repo': 'myrepo'}

        >>> parse_github_url("https://github.com/user/myrepo.git")
        {'owner': 'user', 'repo': 'myrepo'}

        >>> parse_github_url("https://github.com/user/myrepo")
        {'owner': 'user', 'repo': 'myrepo'}
    """
    # SSH format: git@github.com:owner/repo.git
    ssh_pattern = re.compile(
        r"^git@(?:github\.com|gitlab\.com|bitbucket\.org):([^/]+)/(.+?)(?:\.git)?$"
    )

    # HTTPS format: https://github.com/owner/repo.git
    https_pattern = re.compile(
        r"^https://(?:github\.com|gitlab\.com|bitbucket\.org)/([^/]+)/(.+?)(?:\.git)?$"
    )

    # Try SSH pattern
    match = ssh_pattern.match(remote_url)
    if match:
        return {
            "owner": match.group(1),
            "repo": match.group(2)
        }

    # Try HTTPS pattern
    match = https_pattern.match(remote_url)
    if match:
        return {
            "owner": match.group(1),
            "repo": match.group(2)
        }

    # Unable to parse
    return None


def build_github_url(
    owner: str,
    repo: str,
    commit_hash: str,
    file_path: str
) -> str:
    """
    Build a GitHub permalink URL for a file at a specific commit.

    Args:
        owner: Repository owner
        repo: Repository name
        commit_hash: Full commit SHA
        file_path: File path relative to repository root

    Returns:
        GitHub permalink URL

    Examples:
        >>> build_github_url("user", "repo", "abc123...", "src/file.py")
        'https://github.com/user/repo/blob/abc123.../src/file.py'
    """
    # Normalize file path and remove leading slash
    normalized_path = normalize_file_path(file_path).lstrip("/")

    return f"https://github.com/{owner}/{repo}/blob/{commit_hash}/{normalized_path}"


def build_gitlab_url(
    owner: str,
    repo: str,
    commit_hash: str,
    file_path: str
) -> str:
    """
    Build a GitLab permalink URL for a file at a specific commit.

    Args:
        owner: Repository owner
        repo: Repository name
        commit_hash: Full commit SHA
        file_path: File path relative to repository root

    Returns:
        GitLab permalink URL

    Examples:
        >>> build_gitlab_url("user", "repo", "abc123...", "src/file.py")
        'https://gitlab.com/user/repo/-/blob/abc123.../src/file.py'
    """
    normalized_path = normalize_file_path(file_path).lstrip("/")
    return f"https://gitlab.com/{owner}/{repo}/-/blob/{commit_hash}/{normalized_path}"


def build_bitbucket_url(
    owner: str,
    repo: str,
    commit_hash: str,
    file_path: str
) -> str:
    """
    Build a Bitbucket permalink URL for a file at a specific commit.

    Args:
        owner: Repository owner
        repo: Repository name
        commit_hash: Full commit SHA
        file_path: File path relative to repository root

    Returns:
        Bitbucket permalink URL

    Examples:
        >>> build_bitbucket_url("user", "repo", "abc123...", "src/file.py")
        'https://bitbucket.org/user/repo/src/abc123.../src/file.py'
    """
    normalized_path = normalize_file_path(file_path).lstrip("/")
    return f"https://bitbucket.org/{owner}/{repo}/src/{commit_hash}/{normalized_path}"


__all__ = [
    "parse_github_url",
    "build_github_url",
    "build_gitlab_url",
    "build_bitbucket_url",
]
