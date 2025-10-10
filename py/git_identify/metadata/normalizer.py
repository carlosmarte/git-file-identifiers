"""
Metadata normalization for consistent identifier generation.

Normalizes metadata from different sources (GitHub API, local Git)
into a consistent format for deterministic identifier generation.
"""

import json
from datetime import datetime
from typing import Any, Literal, Optional

from ..errors import InvalidHashError
from ..utils.hash import validate_git_hash
from ..utils.path import normalize_file_path


MetadataSource = Literal["local-git", "github-api"]


class Metadata:
    """
    Normalized metadata object.

    All fields are in a consistent format regardless of source.
    """

    def __init__(
        self,
        source: MetadataSource,
        owner: str,
        repo: str,
        branch: str,
        commit_hash: str,
        file_hash: str,
        file_path: str,
        last_modified: str,
        html_url: Optional[str] = None,
        repo_path: Optional[str] = None
    ) -> None:
        self.source = source
        self.owner = owner
        self.repo = repo
        self.branch = branch
        self.commit_hash = commit_hash.lower()
        self.file_hash = file_hash.lower()
        self.file_path = file_path
        self.last_modified = last_modified
        self.html_url = html_url
        self.repo_path = repo_path

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        data = {
            "branch": self.branch,
            "commitHash": self.commit_hash,
            "fileHash": self.file_hash,
            "filePath": self.file_path,
            "lastModified": self.last_modified,
            "owner": self.owner,
            "repo": self.repo,
            "source": self.source,
        }

        if self.html_url:
            data["htmlUrl"] = self.html_url

        if self.repo_path:
            data["repoPath"] = self.repo_path

        return data


def normalize_metadata(raw_meta: dict[str, Any]) -> Metadata:
    """
    Normalize raw metadata into consistent format.

    This function:
    - Validates required fields
    - Normalizes Git hashes (lowercase)
    - Normalizes file paths (POSIX format)
    - Ensures ISO 8601 timestamp format
    - Validates hash formats

    Args:
        raw_meta: Raw metadata dictionary

    Returns:
        Normalized Metadata object

    Raises:
        ValueError: If required fields are missing
        InvalidHashError: If hashes are invalid format

    Examples:
        >>> raw = {
        ...     'source': 'local-git',
        ...     'owner': 'user',
        ...     'repo': 'myrepo',
        ...     'branch': 'main',
        ...     'commitHash': 'ABC123...',
        ...     'fileHash': 'DEF456...',
        ...     'filePath': 'src\\\\file.py',
        ...     'lastModified': '2024-01-01T12:00:00Z'
        ... }
        >>> meta = normalize_metadata(raw)
        >>> meta.file_path
        'src/file.py'
        >>> meta.commit_hash
        'abc123...'
    """
    # Validate required fields
    required_fields = [
        "source",
        "owner",
        "repo",
        "branch",
        "commitHash",
        "fileHash",
        "filePath",
        "lastModified"
    ]

    for field in required_fields:
        if field not in raw_meta:
            raise ValueError(f"Missing required field: {field}")

    # Validate source
    source = raw_meta["source"]
    if source not in ("local-git", "github-api"):
        raise ValueError(f"Invalid source: {source}. Must be 'local-git' or 'github-api'")

    # Extract and validate hashes
    commit_hash = raw_meta["commitHash"]
    file_hash = raw_meta["fileHash"]

    validate_git_hash(commit_hash, "commitHash")
    validate_git_hash(file_hash, "fileHash")

    # Normalize file path
    file_path = normalize_file_path(raw_meta["filePath"])

    # Normalize timestamp to ISO 8601
    last_modified = _normalize_timestamp(raw_meta["lastModified"])

    # Create normalized metadata
    return Metadata(
        source=source,
        owner=raw_meta["owner"],
        repo=raw_meta["repo"],
        branch=raw_meta["branch"],
        commit_hash=commit_hash,
        file_hash=file_hash,
        file_path=file_path,
        last_modified=last_modified,
        html_url=raw_meta.get("htmlUrl"),
        repo_path=raw_meta.get("repoPath")
    )


def canonicalize_metadata(metadata: Metadata) -> str:
    """
    Convert metadata to canonical JSON string for hashing.

    This function:
    - Converts to dictionary
    - Sorts keys alphabetically (for determinism)
    - Removes optional fields (htmlUrl, repoPath) that don't affect identity
    - Serializes to JSON without whitespace

    Args:
        metadata: Normalized metadata object

    Returns:
        Canonical JSON string (compact, sorted keys)

    Examples:
        >>> meta = Metadata(...)
        >>> canonical = canonicalize_metadata(meta)
        >>> # Result is compact JSON with sorted keys:
        >>> # {"branch":"main","commitHash":"abc...","fileHash":"def...",...}
    """
    # Get base dictionary
    data = metadata.to_dict()

    # Remove optional fields that don't affect file identity
    data.pop("htmlUrl", None)
    data.pop("repoPath", None)

    # Sort keys and serialize without whitespace
    return json.dumps(_sort_dict_keys(data), separators=(",", ":"))


def _sort_dict_keys(obj: Any) -> Any:
    """
    Recursively sort dictionary keys alphabetically.

    Args:
        obj: Object to sort (dict, list, or other)

    Returns:
        Object with sorted keys
    """
    if isinstance(obj, dict):
        return {k: _sort_dict_keys(v) for k, v in sorted(obj.items())}
    elif isinstance(obj, list):
        return [_sort_dict_keys(item) for item in obj]
    else:
        return obj


def _normalize_timestamp(timestamp: str | datetime) -> str:
    """
    Normalize timestamp to ISO 8601 format.

    Args:
        timestamp: Timestamp as string or datetime object

    Returns:
        ISO 8601 formatted string (UTC)

    Examples:
        >>> _normalize_timestamp("2024-01-01T12:00:00Z")
        '2024-01-01T12:00:00Z'
        >>> _normalize_timestamp(datetime(2024, 1, 1, 12, 0, 0))
        '2024-01-01T12:00:00Z'
    """
    if isinstance(timestamp, datetime):
        # Convert to UTC and ISO format
        return timestamp.isoformat() + "Z"
    elif isinstance(timestamp, str):
        # Try to parse and reformat for consistency
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            # If parsing fails, return as-is
            return timestamp
    else:
        raise TypeError(f"Invalid timestamp type: {type(timestamp)}")


__all__ = [
    "Metadata",
    "MetadataSource",
    "normalize_metadata",
    "canonicalize_metadata",
]
