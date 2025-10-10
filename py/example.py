"""
Example usage of git-identify package.

Demonstrates common usage patterns for generating file identifiers
and detecting changes.
"""

import asyncio
import json
import os

from git_identify import (
    create_manifest,
    generate_batch_identifiers,
    generate_change_report,
    generate_identifier,
    get_local_metadata,
    get_repository_info,
    has_file_changed,
    is_in_git_repository,
    save_manifest,
)


def example_basic_local():
    """Example: Basic usage with local Git repository."""
    print("\n=== Example 1: Basic Local Repository ===\n")

    # Check if we're in a Git repository
    if not is_in_git_repository("."):
        print("Error: Not in a Git repository")
        return

    # Get metadata for a file
    file_path = "pyproject.toml"
    metadata = get_local_metadata(".", file_path)

    print(f"File: {file_path}")
    print(f"Source: {metadata['source']}")
    print(f"Owner: {metadata['owner']}")
    print(f"Repo: {metadata['repo']}")
    print(f"Branch: {metadata['branch']}")
    print(f"Commit: {metadata['commitHash'][:8]}...")
    print(f"File Hash: {metadata['fileHash'][:8]}...")

    # Generate identifier
    result = generate_identifier(metadata)
    print(f"\nIdentifier: {result.identifier}")
    print(f"Short: {result.short}")


def example_change_detection():
    """Example: File change detection."""
    print("\n=== Example 2: Change Detection ===\n")

    if not is_in_git_repository("."):
        print("Error: Not in a Git repository")
        return

    file_path = "pyproject.toml"

    # Get current metadata
    current_meta = get_local_metadata(".", file_path)
    current_id = generate_identifier(current_meta)

    print(f"Current identifier: {current_id.identifier}")

    # Simulate a previous state (in practice, you'd load this from storage)
    # For demo, we'll use the same metadata
    previous_meta = current_meta
    previous_id = generate_identifier(previous_meta)

    # Check if changed
    if has_file_changed(current_meta, previous_meta):
        print("✗ File has changed")
    else:
        print("✓ File unchanged")

    # Direct identifier comparison
    if current_id.identifier == previous_id.identifier:
        print("✓ Identifiers match - can use cache")
    else:
        print("✗ Identifiers differ - rebuild required")


async def example_batch_processing():
    """Example: Batch processing multiple files."""
    print("\n=== Example 3: Batch Processing ===\n")

    if not is_in_git_repository("."):
        print("Error: Not in a Git repository")
        return

    # Define files to process
    files = [
        "pyproject.toml",
        "README.md",
        "git_identify/__init__.py",
    ]

    # Create batch inputs
    inputs = [
        {"type": "local", "repo_path": ".", "file_path": f}
        for f in files
    ]

    # Progress callback
    def progress(done, total):
        print(f"Progress: {done}/{total}")

    # Process batch
    results = await generate_batch_identifiers(
        inputs,
        concurrency=3,
        progress_callback=progress
    )

    # Display results
    print("\nResults:")
    for result in results:
        status_icon = "✓" if result.status == "success" else "✗"
        print(f"{status_icon} {result.file_path}: {result.identifier or result.error}")

    # Create manifest
    manifest = create_manifest(results)
    print("\nManifest:")
    print(json.dumps(manifest, indent=2))


async def example_change_report():
    """Example: Generate change report."""
    print("\n=== Example 4: Change Report ===\n")

    if not is_in_git_repository("."):
        print("Error: Not in a Git repository")
        return

    # Current files
    files = [
        "pyproject.toml",
        "README.md",
        "git_identify/__init__.py",
    ]

    inputs = [
        {"type": "local", "repo_path": ".", "file_path": f}
        for f in files
    ]

    # Process current state
    current_results = await generate_batch_identifiers(inputs)

    # Create current manifest
    current_manifest = create_manifest(current_results)

    # Simulate previous manifest (in practice, you'd load from file)
    # For demo, we'll modify it slightly
    previous_manifest = current_manifest.copy()

    # Simulate: remove one file, change another
    if "pyproject.toml" in previous_manifest:
        del previous_manifest["pyproject.toml"]  # Simulate new file
    if "README.md" in previous_manifest:
        previous_manifest["README.md"] = "sha256:oldidentifier123"  # Simulate change

    # Generate change report
    report = generate_change_report(current_results, previous_manifest)

    print("Change Report:")
    print(f"  Added: {len(report.added)} files")
    for f in report.added:
        print(f"    + {f}")

    print(f"  Modified: {len(report.modified)} files")
    for f in report.modified:
        print(f"    M {f}")

    print(f"  Unchanged: {len(report.unchanged)} files")
    for f in report.unchanged:
        print(f"    = {f}")

    print(f"  Removed: {len(report.removed)} files")
    for f in report.removed:
        print(f"    - {f}")


def example_repository_info():
    """Example: Get complete repository information."""
    print("\n=== Example 5: Repository Info ===\n")

    if not is_in_git_repository("."):
        print("Error: Not in a Git repository")
        return

    file_path = "pyproject.toml"
    info = get_repository_info(file_path, repo_path=".")

    print(f"File: {file_path}")
    print(f"Identifier: {info['identifier']}")
    print(f"Short: {info['short']}")
    print(f"Algorithm: {info['algorithm']}")
    print(f"\nRepository:")
    print(f"  Root: {info['repository']['root']}")
    print(f"  Owner: {info['repository']['owner']}")
    print(f"  Repo: {info['repository']['repo']}")
    print(f"  Branch: {info['repository']['branch']}")


def main():
    """Run all examples."""
    print("=" * 60)
    print("Git Identify - Example Usage")
    print("=" * 60)

    # Basic examples
    example_basic_local()
    example_change_detection()

    # Async examples
    asyncio.run(example_batch_processing())
    asyncio.run(example_change_report())

    # Repository info
    example_repository_info()

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
