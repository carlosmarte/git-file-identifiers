"""
Git hash validation utilities.

Provides functions for validating Git SHA-1 hashes.
"""

import re
from typing import Optional

from ..errors import InvalidHashError

# Git SHA-1 hash pattern: 40 hexadecimal characters
GIT_HASH_PATTERN = re.compile(r"^[0-9a-f]{40}$", re.IGNORECASE)


def is_valid_git_hash(hash_value: str) -> bool:
    """
    Check if a string is a valid Git SHA-1 hash.

    A valid Git hash is a 40-character hexadecimal string.

    Args:
        hash_value: String to validate

    Returns:
        True if valid Git hash, False otherwise

    Examples:
        >>> is_valid_git_hash("abc123def456789012345678901234567890abcd")
        True
        >>> is_valid_git_hash("invalid")
        False
        >>> is_valid_git_hash("abc123")  # Too short
        False
    """
    if not isinstance(hash_value, str):
        return False
    return bool(GIT_HASH_PATTERN.match(hash_value))


def validate_git_hash(
    hash_value: str,
    hash_type: Optional[str] = None
) -> None:
    """
    Validate a Git hash and raise an exception if invalid.

    Args:
        hash_value: Hash string to validate
        hash_type: Optional description of hash type (e.g., 'commitHash', 'fileHash')

    Raises:
        InvalidHashError: If hash is invalid

    Examples:
        >>> validate_git_hash("abc123def456789012345678901234567890abcd")
        # No exception raised

        >>> validate_git_hash("invalid", "commitHash")
        # Raises InvalidHashError
    """
    if not is_valid_git_hash(hash_value):
        type_msg = f" ({hash_type})" if hash_type else ""
        raise InvalidHashError(
            f"Invalid Git hash{type_msg}: must be 40-character hexadecimal string",
            hash_value=hash_value,
            hash_type=hash_type
        )


__all__ = [
    "is_valid_git_hash",
    "validate_git_hash",
    "GIT_HASH_PATTERN",
]
