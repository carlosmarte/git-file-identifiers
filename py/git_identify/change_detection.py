"""
File change detection utilities.

Provides functions for detecting file changes by comparing metadata
and identifiers without reading file content.
"""

import json
from typing import Any, Optional

from .batch import BatchResult
from .metadata.normalizer import Metadata


class ChangeReport:
    """
    Report of changes between current and previous file states.

    Attributes:
        added: List of file paths that are new (not in previous state)
        modified: List of file paths that changed (identifier differs)
        unchanged: List of file paths that are unchanged (identifier matches)
        removed: List of file paths that were deleted (in previous but not current)
        errors: List of files that had processing errors
    """

    def __init__(
        self,
        added: list[str],
        modified: list[str],
        unchanged: list[str],
        removed: list[str],
        errors: list[dict[str, str]]
    ) -> None:
        self.added = added
        self.modified = modified
        self.unchanged = unchanged
        self.removed = removed
        self.errors = errors

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "added": self.added,
            "modified": self.modified,
            "unchanged": self.unchanged,
            "removed": self.removed,
            "errors": self.errors
        }


def has_file_changed(
    meta1: dict[str, Any] | Metadata,
    meta2: dict[str, Any] | Metadata
) -> bool:
    """
    Check if a file has changed by comparing two metadata objects.

    Compares file hashes (blob SHA) as primary indicator, with fallback
    to commit hash comparison.

    Args:
        meta1: First metadata object or dictionary
        meta2: Second metadata object or dictionary

    Returns:
        True if file content has changed, False otherwise

    Examples:
        >>> meta1 = {'fileHash': 'abc123...', 'commitHash': 'def456...', ...}
        >>> meta2 = {'fileHash': 'abc123...', 'commitHash': 'ghi789...', ...}
        >>> has_file_changed(meta1, meta2)
        False  # Same file hash means same content

        >>> meta3 = {'fileHash': 'xyz789...', ...}
        >>> has_file_changed(meta1, meta3)
        True  # Different file hash means content changed
    """
    if not meta1 or not meta2:
        return True  # If we can't compare, assume changed

    # Convert to dict if Metadata objects
    dict1 = meta1.to_dict() if isinstance(meta1, Metadata) else meta1
    dict2 = meta2.to_dict() if isinstance(meta2, Metadata) else meta2

    # Primary check: file hash (blob SHA)
    # This is the most reliable indicator of file content changes
    file_hash1 = dict1.get("fileHash")
    file_hash2 = dict2.get("fileHash")

    if file_hash1 and file_hash2:
        return file_hash1 != file_hash2

    # Fallback: commit hash
    # If file hashes aren't available, compare commit hashes
    commit_hash1 = dict1.get("commitHash")
    commit_hash2 = dict2.get("commitHash")

    if commit_hash1 and commit_hash2:
        return commit_hash1 != commit_hash2

    # If we can't determine, assume changed
    return True


def compare_identifier(current: str, stored: str) -> bool:
    """
    Compare an identifier against a stored value.

    Args:
        current: Current identifier
        stored: Stored identifier from previous state

    Returns:
        True if identifiers match (file unchanged), False otherwise

    Examples:
        >>> compare_identifier("sha256:abc123...", "sha256:abc123...")
        True
        >>> compare_identifier("sha256:abc123...", "sha256:def456...")
        False
    """
    if not current or not stored:
        return False

    return current == stored


def generate_change_report(
    current: list[BatchResult] | list[dict[str, Any]],
    previous: Optional[dict[str, str]] = None
) -> ChangeReport:
    """
    Generate a change report by comparing current and previous file states.

    Args:
        current: List of current batch results or result dictionaries
        previous: Dictionary mapping file paths to previous identifiers

    Returns:
        ChangeReport with added, modified, unchanged, removed, and error lists

    Raises:
        TypeError: If current is not a list or previous is not a dict

    Examples:
        >>> current_results = [
        ...     {'filePath': 'a.py', 'identifier': 'sha256:abc...', 'status': 'success'},
        ...     {'filePath': 'b.py', 'identifier': 'sha256:def...', 'status': 'success'}
        ... ]
        >>> previous_manifest = {
        ...     'a.py': 'sha256:abc...',  # Unchanged
        ...     'c.py': 'sha256:ghi...'   # Removed
        ... }
        >>> report = generate_change_report(current_results, previous_manifest)
        >>> report.added
        ['b.py']
        >>> report.unchanged
        ['a.py']
        >>> report.removed
        ['c.py']
    """
    if not isinstance(current, list):
        raise TypeError("current must be a list")

    if previous is None:
        previous = {}

    if not isinstance(previous, dict):
        raise TypeError("previous must be a dictionary")

    added = []
    modified = []
    unchanged = []
    removed = []
    errors = []

    # Track which files we've seen
    seen_files = set()

    # Process current files
    for item in current:
        # Convert to dict if BatchResult
        if isinstance(item, BatchResult):
            result = item.to_dict()
        elif isinstance(item, dict):
            result = item
        else:
            continue

        file_path = result.get("filePath")
        if not file_path:
            continue

        seen_files.add(file_path)

        # Handle errors
        if result.get("status") == "error":
            errors.append({
                "filePath": file_path,
                "error": result.get("error", "Unknown error")
            })
            continue

        identifier = result.get("identifier")
        previous_id = previous.get(file_path)

        if not previous_id:
            # New file (not in previous state)
            added.append(file_path)
        elif identifier != previous_id:
            # Modified file (identifier changed)
            modified.append(file_path)
        else:
            # Unchanged file (identifier matches)
            unchanged.append(file_path)

    # Find removed files (in previous but not in current)
    for file_path in previous.keys():
        if file_path not in seen_files:
            removed.append(file_path)

    return ChangeReport(
        added=added,
        modified=modified,
        unchanged=unchanged,
        removed=removed,
        errors=errors
    )


def create_manifest(
    results: list[BatchResult] | list[dict[str, Any]]
) -> dict[str, str]:
    """
    Create a manifest from batch results for storage.

    A manifest is a dictionary mapping file paths to their identifiers,
    useful for persisting state between runs.

    Args:
        results: List of batch results or result dictionaries

    Returns:
        Dictionary mapping file paths to identifiers

    Raises:
        TypeError: If results is not a list

    Examples:
        >>> results = [
        ...     {'filePath': 'a.py', 'identifier': 'sha256:abc...', 'status': 'success'},
        ...     {'filePath': 'b.py', 'identifier': 'sha256:def...', 'status': 'success'},
        ...     {'filePath': 'c.py', 'status': 'error'}  # Excluded from manifest
        ... ]
        >>> manifest = create_manifest(results)
        >>> manifest
        {'a.py': 'sha256:abc...', 'b.py': 'sha256:def...'}
    """
    if not isinstance(results, list):
        raise TypeError("results must be a list")

    manifest = {}

    for item in results:
        # Convert to dict if BatchResult
        if isinstance(item, BatchResult):
            result = item.to_dict()
        elif isinstance(item, dict):
            result = item
        else:
            continue

        # Only include successful results
        if result.get("status") == "success":
            file_path = result.get("filePath")
            identifier = result.get("identifier")

            if file_path and identifier:
                manifest[file_path] = identifier

    return manifest


def load_manifest(json_str: str) -> dict[str, str]:
    """
    Load a manifest from JSON string.

    Args:
        json_str: JSON string representation of manifest

    Returns:
        Manifest dictionary

    Raises:
        ValueError: If JSON is invalid

    Examples:
        >>> json_str = '{"a.py": "sha256:abc...", "b.py": "sha256:def..."}'
        >>> manifest = load_manifest(json_str)
        >>> manifest['a.py']
        'sha256:abc...'
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse manifest JSON: {e}") from e


def save_manifest(
    manifest: dict[str, str],
    pretty: bool = True
) -> str:
    """
    Save a manifest to JSON string.

    Args:
        manifest: Manifest dictionary
        pretty: Pretty-print JSON with indentation (default: True)

    Returns:
        JSON string representation

    Raises:
        TypeError: If manifest is not a dictionary

    Examples:
        >>> manifest = {'a.py': 'sha256:abc...', 'b.py': 'sha256:def...'}
        >>> json_str = save_manifest(manifest, pretty=True)
        >>> print(json_str)
        {
          "a.py": "sha256:abc...",
          "b.py": "sha256:def..."
        }
    """
    if not isinstance(manifest, dict):
        raise TypeError("manifest must be a dictionary")

    if pretty:
        return json.dumps(manifest, indent=2, sort_keys=True)
    else:
        return json.dumps(manifest, sort_keys=True)


__all__ = [
    "ChangeReport",
    "has_file_changed",
    "compare_identifier",
    "generate_change_report",
    "create_manifest",
    "load_manifest",
    "save_manifest",
]
