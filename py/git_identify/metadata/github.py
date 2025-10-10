"""
GitHub API metadata extraction.

Fetches file metadata from GitHub's REST API v3.
"""

import json
import os
import urllib.request
from typing import Any, Optional
from urllib.error import HTTPError, URLError

from ..errors import (
    AuthenticationError,
    FileNotFoundError,
    GitError,
    RateLimitError,
    RepositoryNotFoundError,
)
from ..utils.path import normalize_file_path
from ..utils.url import build_github_url


def get_github_metadata(
    owner: str,
    repo: str,
    file_path: str,
    branch: str = "main",
    token: Optional[str] = None
) -> dict[str, Any]:
    """
    Fetch file metadata from GitHub API.

    Retrieves metadata for a file including:
    - Latest commit hash affecting the file
    - File content SHA (blob hash)
    - Last modified timestamp
    - Permalink URL

    Args:
        owner: Repository owner
        repo: Repository name
        file_path: File path relative to repository root
        branch: Branch name (default: 'main')
        token: GitHub personal access token (optional, uses GITHUB_TOKEN env var if not provided)

    Returns:
        Dictionary with normalized metadata

    Raises:
        RepositoryNotFoundError: If repository doesn't exist or is inaccessible
        FileNotFoundError: If file doesn't exist in repository
        AuthenticationError: If authentication fails
        RateLimitError: If API rate limit is exceeded
        GitError: For other API errors

    Examples:
        >>> meta = get_github_metadata("user", "repo", "src/file.py", "main")
        >>> meta['commitHash']
        'abc123def456...'
        >>> meta['fileHash']
        'def456abc789...'
    """
    # Normalize file path
    normalized_path = normalize_file_path(file_path)

    # Get token from parameter or environment
    if token is None:
        token = os.environ.get("GITHUB_TOKEN")

    # Build API URLs
    # 1. Contents API - get file SHA and metadata
    contents_url = (
        f"https://api.github.com/repos/{owner}/{repo}/contents/{normalized_path}"
        f"?ref={branch}"
    )

    # 2. Commits API - get latest commit for file
    commits_url = (
        f"https://api.github.com/repos/{owner}/{repo}/commits"
        f"?path={normalized_path}&sha={branch}&per_page=1"
    )

    try:
        # Fetch file contents metadata
        contents_data = _github_api_request(contents_url, token)

        # Validate response type (should be a file, not a directory)
        if contents_data.get("type") != "file":
            raise FileNotFoundError(
                f"Path is not a file: {file_path}",
                file_path=file_path
            )

        # Fetch commits for this file
        commits_data = _github_api_request(commits_url, token)

        if not commits_data or not isinstance(commits_data, list):
            raise GitError(
                f"No commits found for file: {file_path}",
                context={"file_path": file_path, "branch": branch}
            )

        latest_commit = commits_data[0]

        # Build metadata dictionary
        return {
            "source": "github-api",
            "owner": owner,
            "repo": repo,
            "branch": branch,
            "filePath": normalized_path,
            "commitHash": latest_commit["sha"],
            "fileHash": contents_data["sha"],
            "lastModified": latest_commit["commit"]["committer"]["date"],
            "htmlUrl": build_github_url(owner, repo, latest_commit["sha"], normalized_path)
        }

    except HTTPError as e:
        if e.code == 404:
            if "commits" in e.url:
                raise FileNotFoundError(
                    f"File not found: {file_path}",
                    file_path=file_path,
                    cause=e
                ) from e
            else:
                raise RepositoryNotFoundError(
                    f"Repository not found: {owner}/{repo}",
                    path=f"{owner}/{repo}",
                    cause=e
                ) from e
        elif e.code == 401 or e.code == 403:
            # Check if it's a rate limit error
            if "rate limit" in e.reason.lower():
                reset_time = e.headers.get("X-RateLimit-Reset")
                remaining = e.headers.get("X-RateLimit-Remaining")
                raise RateLimitError(
                    "GitHub API rate limit exceeded",
                    reset_time=int(reset_time) if reset_time else None,
                    remaining=int(remaining) if remaining else 0,
                    cause=e
                ) from e
            else:
                raise AuthenticationError(
                    "GitHub API authentication failed. Please provide a valid GITHUB_TOKEN.",
                    cause=e
                ) from e
        else:
            raise GitError(
                f"GitHub API error: {e.reason}",
                code=f"HTTP_{e.code}",
                context={"url": e.url},
                cause=e
            ) from e

    except URLError as e:
        raise GitError(
            f"Network error accessing GitHub API: {e.reason}",
            code="NETWORK_ERROR",
            cause=e
        ) from e


def _github_api_request(url: str, token: Optional[str] = None) -> Any:
    """
    Make a request to GitHub API.

    Args:
        url: API endpoint URL
        token: GitHub personal access token

    Returns:
        Parsed JSON response

    Raises:
        HTTPError: For HTTP errors
        URLError: For network errors
    """
    # Build request with headers
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "git-identify-python/2.0.0"
    }

    if token:
        headers["Authorization"] = f"token {token}"

    request = urllib.request.Request(url, headers=headers)

    # Make request
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read()
        return json.loads(data.decode("utf-8"))


__all__ = [
    "get_github_metadata",
]
