"""
Custom exception classes for git-identify module.

Provides a hierarchy of exceptions for handling various error conditions
related to Git operations, GitHub API interactions, and file operations.
"""

from typing import Any, Optional


class GitError(Exception):
    """
    Base exception class for all git-identify errors.

    Attributes:
        message: Error message
        code: Error code for programmatic handling
        context: Additional context information about the error
    """

    def __init__(
        self,
        message: str,
        code: str = "GIT_ERROR",
        context: Optional[dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.context = context or {}
        self.__cause__ = cause

    def __str__(self) -> str:
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} ({context_str})"
        return self.message


class RepositoryNotFoundError(GitError):
    """
    Raised when a Git repository cannot be found at the specified path.

    This typically occurs when:
    - The path does not exist
    - The path is not a Git repository
    - The .git directory is missing or inaccessible
    """

    def __init__(
        self,
        message: str,
        path: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        context = {"path": path} if path else {}
        super().__init__(
            message,
            code="REPOSITORY_NOT_FOUND",
            context=context,
            cause=cause
        )


class FileNotFoundError(GitError):
    """
    Raised when a file cannot be found in the Git repository.

    This typically occurs when:
    - The file path does not exist in the repository
    - The file is not tracked by Git
    - The file was deleted in the specified commit/branch
    """

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        context = {"file_path": file_path} if file_path else {}
        super().__init__(
            message,
            code="FILE_NOT_FOUND",
            context=context,
            cause=cause
        )


class InvalidHashError(GitError):
    """
    Raised when a Git hash is invalid or malformed.

    Git hashes should be 40-character hexadecimal strings (SHA-1).
    This error is raised when:
    - Hash length is incorrect
    - Hash contains non-hexadecimal characters
    - Hash format is otherwise invalid
    """

    def __init__(
        self,
        message: str,
        hash_value: Optional[str] = None,
        hash_type: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        context = {}
        if hash_value:
            context["hash_value"] = hash_value
        if hash_type:
            context["hash_type"] = hash_type
        super().__init__(
            message,
            code="INVALID_HASH",
            context=context,
            cause=cause
        )


class RateLimitError(GitError):
    """
    Raised when GitHub API rate limit is exceeded.

    GitHub has rate limits for API requests:
    - Authenticated: 5000 requests/hour
    - Unauthenticated: 60 requests/hour

    Attributes:
        reset_time: Unix timestamp when rate limit resets
        remaining: Number of remaining requests (typically 0)
    """

    def __init__(
        self,
        message: str,
        reset_time: Optional[int] = None,
        remaining: Optional[int] = None,
        cause: Optional[Exception] = None
    ) -> None:
        context = {}
        if reset_time is not None:
            context["reset_time"] = reset_time
        if remaining is not None:
            context["remaining"] = remaining
        super().__init__(
            message,
            code="RATE_LIMIT_EXCEEDED",
            context=context,
            cause=cause
        )


class AuthenticationError(GitError):
    """
    Raised when GitHub API authentication fails.

    This typically occurs when:
    - GitHub token is invalid or expired
    - Token lacks necessary permissions
    - Token is not provided for a private repository
    """

    def __init__(
        self,
        message: str,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(
            message,
            code="AUTHENTICATION_FAILED",
            cause=cause
        )


class GitCommandError(GitError):
    """
    Raised when a Git command execution fails.

    This occurs when:
    - Git command returns non-zero exit code
    - Git command produces an error message
    - Git is not installed or not in PATH

    Attributes:
        command: The Git command that failed
        exit_code: Exit code returned by Git
        stderr: Error output from Git command
    """

    def __init__(
        self,
        message: str,
        command: Optional[str] = None,
        exit_code: Optional[int] = None,
        stderr: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        context = {}
        if command:
            context["command"] = command
        if exit_code is not None:
            context["exit_code"] = exit_code
        if stderr:
            context["stderr"] = stderr
        super().__init__(
            message,
            code="GIT_COMMAND_FAILED",
            context=context,
            cause=cause
        )


# Export all error classes
__all__ = [
    "GitError",
    "RepositoryNotFoundError",
    "FileNotFoundError",
    "InvalidHashError",
    "RateLimitError",
    "AuthenticationError",
    "GitCommandError",
]
