"""
Path normalization utilities.

Provides functions for normalizing file paths to ensure consistency
across different platforms (Windows, macOS, Linux).
"""

import os
from pathlib import Path


def normalize_file_path(file_path: str) -> str:
    """
    Normalize a file path to POSIX format for consistency.

    This function:
    - Converts backslashes to forward slashes (Windows compatibility)
    - Removes leading "./" prefix
    - Removes trailing slashes
    - Removes duplicate consecutive slashes
    - Preserves relative vs absolute path nature

    Args:
        file_path: File path to normalize

    Returns:
        Normalized path string in POSIX format

    Examples:
        >>> normalize_file_path("./src/index.py")
        'src/index.py'
        >>> normalize_file_path("src\\\\utils\\\\path.py")
        'src/utils/path.py'
        >>> normalize_file_path("src/file.py/")
        'src/file.py'
        >>> normalize_file_path("src//utils///file.py")
        'src/utils/file.py'
    """
    if not file_path:
        return file_path

    # Convert backslashes to forward slashes (Windows)
    normalized = file_path.replace("\\", "/")

    # Remove leading "./"
    if normalized.startswith("./"):
        normalized = normalized[2:]

    # Remove trailing slashes
    normalized = normalized.rstrip("/")

    # Remove duplicate consecutive slashes
    while "//" in normalized:
        normalized = normalized.replace("//", "/")

    return normalized


def resolve_file_path(repo_path: str, file_path: str) -> str:
    """
    Resolve a file path relative to a repository path.

    Handles both absolute and relative file paths, converting them
    to paths relative to the repository root.

    Args:
        repo_path: Repository root path
        file_path: File path (absolute or relative)

    Returns:
        Normalized path relative to repository root

    Examples:
        >>> resolve_file_path("/repo", "src/file.py")
        'src/file.py'
        >>> resolve_file_path("/repo", "/repo/src/file.py")
        'src/file.py'
        >>> resolve_file_path("/repo", "./src/file.py")
        'src/file.py'
    """
    # Convert to Path objects
    repo = Path(repo_path).resolve()
    file = Path(file_path)

    # If file path is absolute, make it relative to repo
    if file.is_absolute():
        try:
            file = file.resolve().relative_to(repo)
        except ValueError:
            # File is not under repo - use as-is
            pass

    # Convert to string and normalize
    return normalize_file_path(str(file))


__all__ = [
    "normalize_file_path",
    "resolve_file_path",
]
