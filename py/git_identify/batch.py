"""
Batch processing for multiple file identifiers.

Provides concurrent processing of multiple files with error resilience
and progress tracking.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Literal, Optional

from .identifier import Algorithm, Encoding, generate_identifier
from .metadata.github import get_github_metadata
from .metadata.local import get_local_metadata

InputType = Literal["github", "local"]


class BatchResult:
    """
    Result from batch processing a single file.

    Attributes:
        file_path: File path
        identifier: Generated identifier (None if error)
        status: Processing status ('success' or 'error')
        error: Error message (None if success)
        metadata: File metadata (None if error)
        short: Short identifier (None if error)
    """

    def __init__(
        self,
        file_path: str,
        identifier: Optional[str] = None,
        status: str = "error",
        error: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        short: Optional[str] = None
    ) -> None:
        self.file_path = file_path
        self.identifier = identifier
        self.status = status
        self.error = error
        self.metadata = metadata
        self.short = short

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "filePath": self.file_path,
            "identifier": self.identifier,
            "status": self.status
        }

        if self.error:
            result["error"] = self.error
        if self.metadata:
            result["metadata"] = self.metadata
        if self.short:
            result["short"] = self.short

        return result


class BatchInput:
    """
    Input specification for batch processing.

    For GitHub:
        type='github', owner, repo, file_path, branch (optional)

    For Local:
        type='local', repo_path, file_path
    """

    def __init__(
        self,
        type: InputType,
        file_path: str,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
        branch: Optional[str] = None,
        repo_path: Optional[str] = None
    ) -> None:
        self.type = type
        self.file_path = file_path
        self.owner = owner
        self.repo = repo
        self.branch = branch or "main"
        self.repo_path = repo_path

    def validate(self) -> None:
        """Validate input has required fields."""
        if self.type == "github":
            if not self.owner or not self.repo:
                raise TypeError("GitHub input requires: owner, repo, file_path")
        elif self.type == "local":
            if not self.repo_path:
                raise TypeError("Local input requires: repo_path, file_path")
        else:
            raise TypeError(f"Invalid input type: {self.type}. Must be 'github' or 'local'")


async def generate_batch_identifiers(
    inputs: list[dict[str, Any] | BatchInput],
    concurrency: int = 10,
    continue_on_error: bool = True,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    algorithm: Algorithm = "sha256",
    encoding: Encoding = "hex",
    truncate: Optional[int] = None
) -> list[BatchResult]:
    """
    Process multiple file identifiers in batch with concurrency control.

    Args:
        inputs: List of input dictionaries or BatchInput objects
        concurrency: Maximum concurrent operations (default: 10)
        continue_on_error: Continue processing on individual errors (default: True)
        progress_callback: Optional callback function(completed, total)
        algorithm: Hash algorithm for identifier generation
        encoding: Output encoding for identifiers
        truncate: Truncate hash to N characters

    Returns:
        List of BatchResult objects

    Raises:
        TypeError: If inputs is not a list or input validation fails

    Examples:
        >>> inputs = [
        ...     {'type': 'github', 'owner': 'user', 'repo': 'repo', 'file_path': 'src/a.py'},
        ...     {'type': 'local', 'repo_path': '/path/to/repo', 'file_path': 'src/b.py'}
        ... ]
        >>> results = await generate_batch_identifiers(inputs)
        >>> [r.status for r in results]
        ['success', 'success']
    """
    if not isinstance(inputs, list):
        raise TypeError("inputs must be a list")

    if len(inputs) == 0:
        return []

    # Convert dict inputs to BatchInput objects
    batch_inputs = []
    for inp in inputs:
        if isinstance(inp, dict):
            batch_inputs.append(BatchInput(**inp))
        elif isinstance(inp, BatchInput):
            batch_inputs.append(inp)
        else:
            raise TypeError(f"Invalid input type: {type(inp)}")

    # Validate all inputs
    for inp in batch_inputs:
        inp.validate()

    # Track progress
    completed = 0
    total = len(batch_inputs)

    async def process_one(inp: BatchInput) -> BatchResult:
        """Process a single input."""
        nonlocal completed

        result = BatchResult(
            file_path=inp.file_path,
            status="error"
        )

        try:
            # Get metadata based on type
            if inp.type == "github":
                metadata = get_github_metadata(
                    inp.owner,  # type: ignore
                    inp.repo,  # type: ignore
                    inp.file_path,
                    inp.branch  # type: ignore
                )
            else:  # local
                metadata = get_local_metadata(
                    inp.repo_path,  # type: ignore
                    inp.file_path
                )

            # Generate identifier
            id_result = generate_identifier(
                metadata,
                algorithm=algorithm,
                encoding=encoding,
                truncate=truncate
            )

            result.identifier = id_result.identifier
            result.short = id_result.short
            result.status = "success"
            result.metadata = metadata

        except Exception as e:
            result.error = str(e)
            if not continue_on_error:
                raise

        finally:
            # Update progress
            completed += 1
            if progress_callback:
                progress_callback(completed, total)

        return result

    # Process with concurrency control using semaphore
    semaphore = asyncio.Semaphore(concurrency)

    async def process_with_semaphore(inp: BatchInput) -> BatchResult:
        async with semaphore:
            # Run blocking operations in thread pool
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                return await loop.run_in_executor(executor, lambda: asyncio.run(process_one(inp)))

    # Process all inputs concurrently
    tasks = [process_with_semaphore(inp) for inp in batch_inputs]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Convert exceptions to error results
    final_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            final_results.append(BatchResult(
                file_path=batch_inputs[i].file_path,
                status="error",
                error=str(result)
            ))
        else:
            final_results.append(result)

    return final_results


class GitBatchProcessor:
    """
    Batch processor class for reusable batch operations.

    Provides a convenient interface for batch processing with progress tracking.

    Examples:
        >>> processor = GitBatchProcessor(concurrency=5)
        >>> processor.on_progress(lambda done, total: print(f"{done}/{total}"))
        >>> results = await processor.process(inputs)
    """

    def __init__(
        self,
        concurrency: int = 10,
        continue_on_error: bool = True,
        algorithm: Algorithm = "sha256",
        encoding: Encoding = "hex",
        truncate: Optional[int] = None
    ) -> None:
        self.concurrency = concurrency
        self.continue_on_error = continue_on_error
        self.algorithm = algorithm
        self.encoding = encoding
        self.truncate = truncate
        self.progress_callbacks: list[Callable[[int, int], None]] = []

    def on_progress(self, callback: Callable[[int, int], None]) -> "GitBatchProcessor":
        """
        Add a progress callback.

        Args:
            callback: Function(completed, total) to call on progress

        Returns:
            Self for method chaining
        """
        if callable(callback):
            self.progress_callbacks.append(callback)
        return self

    async def process(
        self,
        inputs: list[dict[str, Any] | BatchInput]
    ) -> list[BatchResult]:
        """
        Process batch inputs.

        Args:
            inputs: List of input dictionaries or BatchInput objects

        Returns:
            List of BatchResult objects
        """
        def progress_callback(completed: int, total: int) -> None:
            for callback in self.progress_callbacks:
                callback(completed, total)

        return await generate_batch_identifiers(
            inputs,
            concurrency=self.concurrency,
            continue_on_error=self.continue_on_error,
            progress_callback=progress_callback if self.progress_callbacks else None,
            algorithm=self.algorithm,
            encoding=self.encoding,
            truncate=self.truncate
        )


__all__ = [
    "BatchResult",
    "BatchInput",
    "InputType",
    "generate_batch_identifiers",
    "GitBatchProcessor",
]
