"""Repository operations for Git Identify."""

from pathlib import Path
from typing import List, Optional, Any, Union
import os

try:
    import pygit2
    USE_PYGIT2 = True
except ImportError:
    USE_PYGIT2 = False

import git  # GitPython as fallback


def find_git_root(start_path: str) -> Path:
    """
    Find the Git repository root from a file or directory path.

    Args:
        start_path: Path to start searching from

    Returns:
        Path to the repository root

    Raises:
        ValueError: If no Git repository is found
    """
    path = Path(start_path).resolve()

    if path.is_file():
        current_dir = path.parent
    else:
        current_dir = path

    while True:
        git_dir = current_dir / ".git"
        if git_dir.exists():
            return current_dir

        if current_dir.parent == current_dir:
            raise ValueError("No .git directory found")

        current_dir = current_dir.parent


def get_file_hash_at_commit(repo: Any, file_path: str, commit_hash: str) -> str:
    """
    Get the blob hash of a file at a specific commit.

    Args:
        repo: Repository object (pygit2.Repository or git.Repo)
        file_path: Path to the file relative to repository root
        commit_hash: SHA-1 hash of the commit

    Returns:
        SHA-1 hash of the file blob

    Raises:
        ValueError: If commit or file not found
    """
    try:
        if USE_PYGIT2 and isinstance(repo, pygit2.Repository):
            commit = repo.revparse_single(commit_hash)
            tree = commit.tree
            entry = tree[file_path]
            return str(entry.id)
        else:
            commit = repo.commit(commit_hash)
            blob = commit.tree[file_path]
            return blob.binsha.hex()
    except Exception as e:
        raise ValueError(f"Failed to get file hash at commit: {e}")


def get_current_branch_commit_for_file(repo: Any, file_path: str) -> str:
    """
    Get the current branch's commit hash for a file.

    Args:
        repo: Repository object (pygit2.Repository or git.Repo)
        file_path: Path to the file

    Returns:
        SHA-1 hash of the current commit

    Raises:
        ValueError: If file doesn't exist
    """
    try:
        # Get repository working directory
        if USE_PYGIT2 and isinstance(repo, pygit2.Repository):
            repo_path = Path(repo.workdir)
        else:
            repo_path = Path(repo.working_dir)

        # Check if file exists
        full_path = repo_path / file_path
        if not full_path.exists():
            raise ValueError(f"File does not exist: {file_path}")

        # Get HEAD commit
        if USE_PYGIT2 and isinstance(repo, pygit2.Repository):
            head = repo.head
            commit = repo[head.target]
            return str(commit.id)
        else:
            head = repo.head.commit
            return head.hexsha
    except Exception as e:
        raise ValueError(f"Failed to get commit for file: {e}")


def get_remote_url(repo: Any) -> str:
    """
    Get the origin remote URL.

    Args:
        repo: Repository object (pygit2.Repository or git.Repo)

    Returns:
        Remote URL string

    Raises:
        ValueError: If no origin remote found
    """
    try:
        if USE_PYGIT2 and isinstance(repo, pygit2.Repository):
            origin = repo.remotes.get("origin")
            if not origin:
                raise ValueError("No origin remote found")
            return origin.url
        else:
            if "origin" not in repo.remotes:
                raise ValueError("No origin remote found")
            return repo.remotes["origin"].url
    except Exception as e:
        raise ValueError(f"Failed to get remote URL: {e}")


def list_refs(repo: Any) -> List[str]:
    """
    List all Git references in the repository.

    Args:
        repo: Repository object (pygit2.Repository or git.Repo)

    Returns:
        List of reference names

    Raises:
        ValueError: If listing fails
    """
    try:
        refs = []

        if USE_PYGIT2 and isinstance(repo, pygit2.Repository):
            for ref in repo.references:
                refs.append(ref)
        else:
            for ref in repo.references:
                refs.append(ref.path)

        return refs
    except Exception as e:
        raise ValueError(f"Failed to list refs: {e}")


def get_file_status(repo: Any, file_path: str) -> str:
    """
    Get the Git status of a file.

    Args:
        repo: Repository object (pygit2.Repository or git.Repo)
        file_path: Path to the file

    Returns:
        Status string: "clean", "modified", "untracked", "added", "staged", "deleted", "unknown"

    Raises:
        ValueError: If status check fails
    """
    try:
        if USE_PYGIT2 and isinstance(repo, pygit2.Repository):
            status_flags = repo.status_file(file_path)

            if status_flags == pygit2.GIT_STATUS_CURRENT:
                return "clean"
            elif status_flags & pygit2.GIT_STATUS_WT_NEW:
                return "untracked"
            elif status_flags & pygit2.GIT_STATUS_WT_MODIFIED:
                return "modified"
            elif status_flags & pygit2.GIT_STATUS_INDEX_NEW:
                return "added"
            elif status_flags & pygit2.GIT_STATUS_INDEX_MODIFIED:
                return "staged"
            elif status_flags & pygit2.GIT_STATUS_INDEX_DELETED:
                return "deleted"
            else:
                return "unknown"
        else:
            # GitPython approach
            if file_path in repo.untracked_files:
                return "untracked"

            # Check index (staged files)
            diff_index = repo.index.diff(repo.head.commit)
            for diff in diff_index:
                if diff.a_path == file_path or diff.b_path == file_path:
                    if diff.change_type == "A":
                        return "added"
                    elif diff.change_type == "M":
                        return "staged"
                    elif diff.change_type == "D":
                        return "deleted"

            # Check working directory
            diff_work = repo.index.diff(None)
            for diff in diff_work:
                if diff.a_path == file_path or diff.b_path == file_path:
                    return "modified"

            return "clean"
    except Exception as e:
        raise ValueError(f"Failed to get file status: {e}")


def get_head_ref(repo: Any) -> str:
    """
    Get the current HEAD reference.

    Args:
        repo: Repository object (pygit2.Repository or git.Repo)

    Returns:
        Branch name if on a branch, commit hash if detached HEAD

    Raises:
        ValueError: If HEAD ref retrieval fails
    """
    try:
        if USE_PYGIT2 and isinstance(repo, pygit2.Repository):
            head = repo.head

            # Check if HEAD is a symbolic reference (branch)
            if hasattr(head, 'shorthand'):
                return head.shorthand
            else:
                # Detached HEAD - return commit hash
                commit = repo[head.target]
                return str(commit.id)
        else:
            if repo.head.is_detached:
                return repo.head.commit.hexsha
            else:
                return repo.active_branch.name
    except Exception as e:
        raise ValueError(f"Failed to get HEAD ref: {e}")