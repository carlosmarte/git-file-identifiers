"""
Local Git repository metadata extraction.

Extracts file metadata from local Git repositories using Git commands.
"""

import os
import re
from typing import Any, Optional

from ..errors import FileNotFoundError, RepositoryNotFoundError
from ..utils.git import (
    execute_git_command,
    get_current_branch,
    get_remote_url,
    get_repository_root,
)
from ..utils.path import normalize_file_path, resolve_file_path
from ..utils.url import parse_github_url


def get_local_metadata(
    repo_path: str,
    file_path: str
) -> dict[str, Any]:
    """
    Extract metadata from a local Git repository.

    Retrieves metadata for a file including:
    - Latest commit hash affecting the file
    - File content SHA (blob hash)
    - Last modified timestamp
    - Repository information (owner, repo, branch)

    Args:
        repo_path: Path to Git repository (can be any path within repo)
        file_path: File path (absolute or relative to repo root)

    Returns:
        Dictionary with normalized metadata

    Raises:
        RepositoryNotFoundError: If path is not in a Git repository
        FileNotFoundError: If file is not tracked by Git

    Examples:
        >>> meta = get_local_metadata("/path/to/repo", "src/file.py")
        >>> meta['commitHash']
        'abc123def456...'
        >>> meta['fileHash']
        'def456abc789...'
    """
    # Get repository root
    try:
        repo_root = get_repository_root(repo_path)
    except RepositoryNotFoundError as e:
        raise RepositoryNotFoundError(
            f"Not a Git repository: {repo_path}",
            path=repo_path,
            cause=e
        ) from e

    # Resolve file path relative to repo root
    relative_path = resolve_file_path(repo_root, file_path)

    # Check if file exists in repository
    if not is_file_in_git(repo_root, relative_path):
        raise FileNotFoundError(
            f"File not tracked by Git: {relative_path}",
            file_path=relative_path
        )

    # Get commit hash for latest commit affecting this file
    commit_hash = execute_git_command(
        f'git log -1 --pretty=format:%H -- "{relative_path}"',
        cwd=repo_root
    )

    if not commit_hash:
        raise FileNotFoundError(
            f"No commits found for file: {relative_path}",
            file_path=relative_path
        )

    # Get last modified timestamp (committer date in ISO 8601)
    last_modified = execute_git_command(
        f'git log -1 --pretty=format:%cI -- "{relative_path}"',
        cwd=repo_root
    )

    # Get current branch
    branch = get_current_branch(repo_root)

    # Get file hash (blob SHA) using git ls-tree
    ls_tree_output = execute_git_command(
        f'git ls-tree HEAD "{relative_path}"',
        cwd=repo_root
    )

    # Parse ls-tree output: "100644 blob <hash>\t<path>"
    match = re.match(r"^\d+ blob ([0-9a-f]{40})\t", ls_tree_output)
    if not match:
        raise FileNotFoundError(
            f"Could not determine file hash for: {relative_path}",
            file_path=relative_path
        )

    file_hash = match.group(1)

    # Get repository owner/name from remote URL
    owner, repo = _get_repo_info(repo_root)

    # Build metadata dictionary
    return {
        "source": "local-git",
        "owner": owner,
        "repo": repo,
        "repoPath": repo_root,
        "branch": branch,
        "filePath": relative_path,
        "commitHash": commit_hash,
        "fileHash": file_hash,
        "lastModified": last_modified
    }


def is_file_in_git(repo_path: str, file_path: str) -> bool:
    """
    Check if a file is tracked by Git.

    Args:
        repo_path: Repository root path
        file_path: File path relative to repo root

    Returns:
        True if file is tracked, False otherwise

    Examples:
        >>> is_file_in_git("/path/to/repo", "src/file.py")
        True
        >>> is_file_in_git("/path/to/repo", "untracked.py")
        False
    """
    try:
        # Try to get file info from git ls-files
        output = execute_git_command(
            f'git ls-files --error-unmatch "{file_path}"',
            cwd=repo_path
        )
        return bool(output)
    except Exception:
        return False


def _get_repo_info(repo_path: str) -> tuple[str, str]:
    """
    Get repository owner and name from remote URL.

    Falls back to directory name if remote URL is not available.

    Args:
        repo_path: Repository root path

    Returns:
        Tuple of (owner, repo_name)

    Examples:
        >>> _get_repo_info("/path/to/repo")
        ('owner', 'repo')
    """
    # Try to get remote URL
    remote_url = get_remote_url(repo_path)

    if remote_url:
        # Parse remote URL
        parsed = parse_github_url(remote_url)
        if parsed:
            return parsed["owner"], parsed["repo"]

    # Fallback: use directory name
    repo_name = os.path.basename(repo_path)

    # Try to get user name from git config
    try:
        owner = execute_git_command("git config user.name", cwd=repo_path)
        if owner:
            return owner, repo_name
    except Exception:
        pass

    # Final fallback
    return "unknown", repo_name


__all__ = [
    "get_local_metadata",
    "is_file_in_git",
]
