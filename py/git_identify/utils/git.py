"""
Git command execution utilities.

Provides functions for executing Git commands safely and checking repository status.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional

from ..errors import GitCommandError, RepositoryNotFoundError


def execute_git_command(
    command: str,
    cwd: Optional[str] = None,
    timeout: int = 30
) -> str:
    """
    Execute a Git command and return its output.

    Args:
        command: Git command to execute (e.g., "git status")
        cwd: Working directory for command execution (defaults to current directory)
        timeout: Command timeout in seconds (default: 30)

    Returns:
        Command output (stdout) as string, stripped of whitespace

    Raises:
        GitCommandError: If command execution fails
        RepositoryNotFoundError: If not in a Git repository

    Examples:
        >>> execute_git_command("git rev-parse HEAD", "/path/to/repo")
        'abc123def456...'

        >>> execute_git_command("git status", "/invalid/path")
        # Raises RepositoryNotFoundError
    """
    if cwd is None:
        cwd = os.getcwd()

    try:
        # Set LC_ALL=C for consistent output format
        env = os.environ.copy()
        env["LC_ALL"] = "C"

        result = subprocess.run(
            command.split(),
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            check=True
        )

        return result.stdout.strip()

    except subprocess.TimeoutExpired as e:
        raise GitCommandError(
            f"Git command timed out after {timeout} seconds",
            command=command,
            cause=e
        ) from e

    except subprocess.CalledProcessError as e:
        # Check for "not a git repository" error
        stderr = e.stderr.lower()
        if "not a git repository" in stderr or "not found" in stderr:
            raise RepositoryNotFoundError(
                f"Not a Git repository: {cwd}",
                path=cwd,
                cause=e
            ) from e

        # Other Git command error
        raise GitCommandError(
            f"Git command failed: {e.stderr.strip()}",
            command=command,
            exit_code=e.returncode,
            stderr=e.stderr.strip(),
            cause=e
        ) from e

    except FileNotFoundError as e:
        raise GitCommandError(
            "Git executable not found. Please ensure Git is installed and in PATH.",
            command=command,
            cause=e
        ) from e


def is_git_repository(path: str) -> bool:
    """
    Check if a path is within a Git repository.

    Args:
        path: Path to check

    Returns:
        True if path is in a Git repository, False otherwise

    Examples:
        >>> is_git_repository("/path/to/repo")
        True
        >>> is_git_repository("/tmp")
        False
    """
    try:
        execute_git_command("git rev-parse --git-dir", cwd=path, timeout=5)
        return True
    except (GitCommandError, RepositoryNotFoundError):
        return False


def get_repository_root(path: str) -> str:
    """
    Get the root directory of a Git repository.

    Args:
        path: Path within the repository

    Returns:
        Absolute path to repository root

    Raises:
        RepositoryNotFoundError: If path is not in a Git repository

    Examples:
        >>> get_repository_root("/path/to/repo/src")
        '/path/to/repo'
    """
    try:
        # Get the .git directory location
        git_dir = execute_git_command(
            "git rev-parse --git-dir",
            cwd=path,
            timeout=5
        )

        # Convert to absolute path
        git_path = Path(git_dir)
        if not git_path.is_absolute():
            git_path = Path(path) / git_path

        git_path = git_path.resolve()

        # Repository root is parent of .git (unless it's a bare repo)
        if git_path.name == ".git":
            return str(git_path.parent)
        else:
            # Bare repository - the .git dir IS the repo
            return str(git_path)

    except GitCommandError as e:
        raise RepositoryNotFoundError(
            f"Not a Git repository: {path}",
            path=path,
            cause=e
        ) from e


def get_current_branch(repo_path: str) -> str:
    """
    Get the current branch name.

    Args:
        repo_path: Repository path

    Returns:
        Current branch name

    Raises:
        GitCommandError: If unable to determine branch

    Examples:
        >>> get_current_branch("/path/to/repo")
        'main'
    """
    return execute_git_command(
        "git rev-parse --abbrev-ref HEAD",
        cwd=repo_path
    )


def get_remote_url(repo_path: str, remote: str = "origin") -> Optional[str]:
    """
    Get the URL of a Git remote.

    Args:
        repo_path: Repository path
        remote: Remote name (default: 'origin')

    Returns:
        Remote URL, or None if remote doesn't exist

    Examples:
        >>> get_remote_url("/path/to/repo")
        'git@github.com:user/repo.git'
    """
    try:
        return execute_git_command(
            f"git remote get-url {remote}",
            cwd=repo_path
        )
    except GitCommandError:
        return None


__all__ = [
    "execute_git_command",
    "is_git_repository",
    "get_repository_root",
    "get_current_branch",
    "get_remote_url",
]
