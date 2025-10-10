# git-identify

> Generate unique, deterministic file identifiers from Git or GitHub metadata for file change detection without reading content

[![Python Version](https://img.shields.io/badge/python-%3E%3D3.11-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Overview

**git-identify** provides a unified API and CLI for generating unique, deterministic file identifiers derived from Git or GitHub metadata. It enables **file change detection without reading file content** by comparing identifiers generated from metadata at different points in time.

### Key Features

✅ **Metadata-based change detection** - Detect file changes without downloading or reading content
✅ **Deterministic identifiers** - Same metadata → same ID (reproducible across platforms)
✅ **Dual source support** - Works with both GitHub API and local Git repositories
✅ **Async batch operations** - Process multiple files concurrently with error resilience
✅ **Type-safe** - Full type hints for IDE support and type checking
✅ **Zero dependencies** - Uses only Python standard library
✅ **CLI included** - Command-line interface for common operations

## Installation

```bash
# Using pip
pip install git-identify

# Using Poetry
poetry add git-identify
```

## Quick Start

### Local Git Repository

```python
from git_identify import get_local_metadata, generate_identifier

# Get metadata from local Git repository
metadata = get_local_metadata(".", "src/index.py")

# Generate deterministic identifier
result = generate_identifier(metadata)

print(result.identifier)  # "sha256:87ab5dcb..."
print(result.short)       # "87ab5dcb"
```

### GitHub API

```python
import os
from git_identify import get_github_metadata, generate_identifier

# Set GitHub token (optional but recommended)
os.environ["GITHUB_TOKEN"] = "your-token-here"

# Get metadata from GitHub
metadata = get_github_metadata("owner", "repo", "src/index.py", "main")

# Generate identifier
result = generate_identifier(metadata)

print(result.identifier)  # "sha256:87ab5dcb..."
```

### File Change Detection

```python
from git_identify import get_local_metadata, generate_identifier

# Time T1: Store initial identifier
meta1 = get_local_metadata(".", "src/index.py")
id1 = generate_identifier(meta1)
# await storage.set("src/index.py", id1.identifier)

# ... file gets modified and committed ...

# Time T2: Check if file changed
meta2 = get_local_metadata(".", "src/index.py")
id2 = generate_identifier(meta2)
# cached_id = await storage.get("src/index.py")

if id2.identifier != id1.identifier:
    print("File changed - rebuild required")
else:
    print("File unchanged - use cache")
```

## API Reference

### Core Functions

#### `get_local_metadata(repo_path, file_path)`
Extract metadata from a local Git repository.

```python
metadata = get_local_metadata("/path/to/repo", "src/file.py")
# Returns: dict with source, owner, repo, branch, commitHash, fileHash, ...
```

#### `get_github_metadata(owner, repo, file_path, branch='main', token=None)`
Fetch metadata from GitHub API.

```python
metadata = get_github_metadata("user", "repo", "src/file.py", "main")
# Returns: dict with source, owner, repo, branch, commitHash, fileSha, htmlUrl, ...
```

#### `generate_identifier(metadata, algorithm='sha256', encoding='hex', truncate=None)`
Generate deterministic identifier from metadata.

```python
result = generate_identifier(metadata, algorithm="sha256", encoding="hex")
# Returns: IdentifierResult(identifier, short, algorithm)
```

#### `generate_batch_identifiers(inputs, concurrency=10, ...)`
Process multiple files in parallel (async).

```python
import asyncio
from git_identify import generate_batch_identifiers

inputs = [
    {"type": "github", "owner": "user", "repo": "repo", "file_path": "src/a.py"},
    {"type": "local", "repo_path": "/path/to/repo", "file_path": "src/b.py"}
]

results = await generate_batch_identifiers(
    inputs,
    concurrency=10,
    progress_callback=lambda done, total: print(f"{done}/{total}")
)
```

### Change Detection Helpers

#### `has_file_changed(meta1, meta2)`
Compare two metadata objects to detect changes.

```python
changed = has_file_changed(old_metadata, new_metadata)
```

#### `generate_change_report(current, previous)`
Generate detailed change report.

```python
report = generate_change_report(current_results, previous_manifest)
# Returns: ChangeReport(added, modified, unchanged, removed, errors)
```

#### `create_manifest(results)`
Create manifest from batch results for storage.

```python
manifest = create_manifest(batch_results)
# Returns: dict mapping file paths to identifiers
```

#### `save_manifest(manifest, pretty=True)` / `load_manifest(json_str)`
Save/load manifests to/from JSON.

```python
json_str = save_manifest(manifest, pretty=True)
manifest = load_manifest(json_str)
```

### Utility Functions

- `normalize_file_path(path)` - Normalize path to POSIX format
- `parse_github_url(remote_url)` - Parse Git remote URL
- `build_github_url(owner, repo, commit, path)` - Build GitHub permalink
- `is_valid_git_hash(hash)` - Validate Git hash format
- `is_git_repository(path)` - Check if path is a Git repo

## CLI Usage

The package includes a command-line interface:

```bash
# Local repository
git-identify local src/file.py --repo /path/to/repo
git-identify local src/file.py --short  # Short identifier only
git-identify local src/file.py --json   # Full JSON output

# GitHub API
git-identify github owner repo src/file.py --branch main
git-identify github owner repo src/file.py --token YOUR_TOKEN

# Batch processing
git-identify batch inputs.json --output results.json --progress

# Change detection
git-identify diff inputs.json manifest.json --output changes.json

# Repository info
git-identify info src/file.py --repo /path/to/repo
```

## Use Cases

### 1. Cache Invalidation

Automatically invalidate caches when source files change:

```python
from git_identify import get_local_metadata, generate_identifier

async def get_cache_key(source_file: str) -> str:
    meta = get_local_metadata(".", source_file)
    result = generate_identifier(meta)
    return result.identifier

# File change → new identifier → cache miss → rebuild
```

### 2. Incremental Builds

Only rebuild files that changed:

```python
import asyncio
import json
from git_identify import generate_batch_identifiers, generate_change_report

# Load previous manifest
with open("manifest.json") as f:
    previous_manifest = json.load(f)

# Generate current identifiers
inputs = [
    {"type": "local", "repo_path": ".", "file_path": f}
    for f in source_files
]

results = await generate_batch_identifiers(inputs)
report = generate_change_report(results, previous_manifest)

print(f"Modified files: {len(report.modified)}")
# Rebuild only modified files
```

### 3. CI/CD File Tracking

Track which files changed between builds:

```python
import json
from git_identify import generate_batch_identifiers, create_manifest

# In your CI/CD pipeline
results = await generate_batch_identifiers(files_to_track)
manifest = create_manifest(results)

with open("identifiers.json", "w") as f:
    json.dump(manifest, f, indent=2)
```

## Metadata Schema

Both `get_local_metadata()` and `get_github_metadata()` return normalized metadata:

```python
{
    "source": "local-git" | "github-api",
    "owner": str,          # Repository owner
    "repo": str,           # Repository name
    "branch": str,         # Current branch
    "commitHash": str,     # Latest commit (40-char hex)
    "fileHash": str,       # Blob SHA (40-char hex)
    "filePath": str,       # Normalized POSIX path
    "lastModified": str,   # ISO 8601 timestamp
    "htmlUrl": str | None  # GitHub permalink (if applicable)
}
```

## Error Handling

The module provides typed error classes:

```python
from git_identify import (
    GitError,
    RepositoryNotFoundError,
    FileNotFoundError,
    RateLimitError,
    AuthenticationError
)

try:
    metadata = get_local_metadata("/invalid/path", "file.py")
except RepositoryNotFoundError:
    print("Not a Git repository")
except FileNotFoundError:
    print("File not tracked in Git")
```

## Requirements

- **Python:** ≥ 3.11
- **Git:** ≥ 2.20.0 (for local operations)
- **GitHub Token:** Optional (recommended for API to avoid rate limits)

Set `GITHUB_TOKEN` environment variable:

```bash
export GITHUB_TOKEN=your_personal_access_token
```

## Development

```bash
# Install with Poetry
poetry install

# Run tests
poetry run pytest

# Type checking
poetry run mypy git_identify

# Linting
poetry run ruff check git_identify

# Formatting
poetry run black git_identify
```

## License

MIT

## Contributing

Contributions welcome! Please see the [spec document](../spec/spec-2.0.0.md) for detailed requirements.
