# Git Identify - Python Module

A Python library for Git repository operations, GitHub URL generation, and Git object manipulation.

## 📋 Features

- **Repository Discovery**: Find Git repository root from any file or directory path
- **GitHub URL Generation**: Generate GitHub URLs for files with commit hash
- **Git Object Access**: Retrieve blobs, trees, commits, and tags by hash
- **Repository Status**: Check file status, list references, get HEAD reference
- **Dual Backend Support**: Works with both pygit2 and GitPython
- **Type Hints**: Full type annotations for better IDE support
- **Cross-platform**: Works on Windows, macOS, and Linux

## 📦 Installation

### From PyPI
```bash
pip install git-identify
```

### From Source
```bash
cd py
pip install -e .
```

### Development Setup

```bash
# Clone and navigate to py directory
cd py

# Install dependencies
pip install GitPython pytest

# Install in development mode
pip install -e .

# Run tests
python3 -m pytest tests/

# Run tests with verbose output
python3 -m pytest tests/ -v

# Run tests with quiet output
python3 -m pytest tests/ -q

# Run example script
python3 example.py
```

## 🚀 Quick Start

```python
from git_identify import GitFileId, generate_github_url_direct

# Method 1: Direct URL generation
url = generate_github_url_direct("/path/to/file.py")
print(f"GitHub URL: {url}")
# Output: https://github.com/owner/repo/blob/commit/path/to/file.py

# Method 2: Using GitFileId instance
git_id = GitFileId()
git_id.find_repository("/path/to/file.py")

# Generate GitHub URL
url = git_id.generate_github_url("/path/to/file.py")

# Get file status
status = git_id.get_file_status("/path/to/file.py")
print(f"Status: {status}")  # clean, modified, staged, etc.

# List all references
refs = git_id.list_refs()
print(f"References: {refs}")

# Get current HEAD reference
head = git_id.get_head_ref()
print(f"HEAD: {head}")
```

## 📚 Complete Examples

### Repository Operations
```python
from git_identify import GitFileId

# Create instance
git_id = GitFileId()

# Find repository from any path
git_id.find_repository("/path/to/repo/src/main.py")

# Get repository information
head = git_id.get_head_ref()
refs = git_id.list_refs()

print(f"Current branch/commit: {head}")
print(f"All references: {refs}")
```

### Working with Git Objects
```python
from git_identify import GitFileId

git_id = GitFileId()
git_id.find_repository(".")

# Get a commit
commit = git_id.get_commit("abc123def456")
print(f"Author: {commit.author_name} <{commit.author_email}>")
print(f"Message: {commit.message}")
print(f"Time: {commit.time}")

# Get a blob (file)
blob = git_id.get_blob("def456abc789")
print(f"Size: {blob.size} bytes")
print(f"Binary: {blob.is_binary}")

# Get a tree (directory)
tree = git_id.get_tree("789abcdef012")
print(f"Entries: {tree.len}")

# Get a tag
tag = git_id.get_tag("v1.0.0")
print(f"Name: {tag.name}")
print(f"Message: {tag.message}")
```

### Error Handling
```python
from git_identify import GitFileId, generate_github_url_direct

# Handle repository not found
try:
    git_id = GitFileId()
    git_id.find_repository("/not/a/repo")
except ValueError as e:
    print(f"Error: {e}")  # No .git directory found

# Handle missing remote
try:
    url = generate_github_url_direct("/path/to/file.py")
except ValueError as e:
    if "No origin remote" in str(e):
        print("Repository has no GitHub remote")
    else:
        print(f"Error: {e}")
```

### File Status Checking
```python
from git_identify import GitFileId

git_id = GitFileId()
git_id.find_repository(".")

# Check various file statuses
files = ["README.md", "src/main.py", "new_file.txt"]

for file in files:
    try:
        status = git_id.get_file_status(file)
        print(f"{file}: {status}")
    except ValueError:
        print(f"{file}: not found")

# Possible statuses:
# - clean: File is tracked and unmodified
# - modified: File has unstaged changes
# - staged: File has staged changes
# - added: File is newly staged
# - deleted: File is deleted
# - untracked: File is not tracked by Git
```

## 📚 API Reference

### Classes

#### GitFileId
Main class for Git repository operations.

**Methods:**
- `find_repository(file_path: str) -> None` - Find and set the Git repository root
- `generate_github_url(file_path: str) -> str` - Generate GitHub URL for a file
- `get_file_hash(file_path: str) -> str` - Get commit hash for a file
- `get_blob(hash: str) -> GitBlob` - Get blob object by hash
- `get_tree(hash: str) -> GitTree` - Get tree object by hash
- `get_commit(hash: str) -> GitCommit` - Get commit object by hash
- `get_tag(hash: str) -> GitTag` - Get tag object by hash
- `list_refs() -> List[str]` - List all repository references
- `get_file_status(file_path: str) -> str` - Get file Git status
- `get_head_ref() -> str` - Get current HEAD reference

### Standalone Functions

- `generate_github_url_direct(file_path: str) -> str` - Generate GitHub URL without creating instance
- `find_git_root(start_path: str) -> Path` - Find repository root directory
- `parse_remote_url(remote_url: str) -> GitHubInfo` - Parse GitHub remote URL
- `build_github_url(github_info, commit_hash, file_path) -> str` - Build GitHub URL
- `normalize_file_path(file_path: str) -> str` - Normalize file path for URLs

### Data Classes

#### GitBlob
```python
@dataclass
class GitBlob:
    id: str        # Blob SHA hash
    size: int      # Size in bytes
    is_binary: bool  # Binary file indicator
```

#### GitTree
```python
@dataclass
class GitTree:
    id: str   # Tree SHA hash
    len: int  # Number of entries
```

#### GitCommit
```python
@dataclass
class GitCommit:
    id: str              # Commit SHA hash
    message: str         # Commit message
    author_name: str     # Author name
    author_email: str    # Author email
    time: int           # Unix timestamp
    tree_id: str        # Tree SHA hash
    parent_ids: List[str]  # Parent commit hashes
```

#### GitTag
```python
@dataclass
class GitTag:
    id: str         # Tag SHA hash
    name: str       # Tag name
    message: str    # Tag message
    target_id: str  # Target object hash
```

#### GitHubInfo
```python
@dataclass
class GitHubInfo:
    owner: str  # Repository owner
    repo: str   # Repository name
```

## 🧪 Testing

### Run All Tests
```bash
# Run all tests
python3 -m pytest tests/

# Run with verbose output
python3 -m pytest tests/ -v

# Run with quiet output
python3 -m pytest tests/ -q

# Run with coverage
python3 -m pytest tests/ --cov=git_identify

# Run specific test file
python3 -m pytest tests/test_url_builder.py

# Run specific test
python3 -m pytest tests/test_url_builder.py::TestParseRemoteUrl::test_parse_ssh_url
```

### Test Structure
- **Unit Tests**: 109 tests
  - `test_url_builder.py` - 32 tests for URL parsing and building
  - `test_repository.py` - 24 tests for repository operations
  - `test_objects.py` - 26 tests for Git objects
  - `test_git_file_id.py` - 27 tests for main class
- **Integration Tests**: 17 tests
  - `test_integration.py` - End-to-end testing with real repositories
- **Total**: 126 tests, all passing ✅

## 🚀 Integration Instructions

### Package Integration

1. **Install the package:**
   ```bash
   pip install git-identify
   ```

2. **Import in your project:**
   ```python
   from git_identify import GitFileId, generate_github_url_direct
   ```

3. **Use in your application:**
   ```python
   def get_github_link(file_path):
       """Get GitHub URL for a file."""
       try:
           return generate_github_url_direct(file_path)
       except ValueError as e:
           print(f"Error: {e}")
           return None
   ```

### Django Integration

```python
# views.py
from django.shortcuts import render
from git_identify import generate_github_url_direct

def source_view(request, file_path):
    try:
        github_url = generate_github_url_direct(file_path)
    except ValueError:
        github_url = None

    return render(request, 'source.html', {
        'file_path': file_path,
        'github_url': github_url
    })
```

### Flask Integration

```python
from flask import Flask, jsonify
from git_identify import GitFileId

app = Flask(__name__)
git_id = GitFileId()
git_id.find_repository(".")

@app.route('/github-url/<path:file_path>')
def get_github_url(file_path):
    try:
        url = git_id.generate_github_url(file_path)
        return jsonify({'url': url})
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
```

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from git_identify import GitFileId

app = FastAPI()
git_id = GitFileId()
git_id.find_repository(".")

@app.get("/github-url/{file_path:path}")
async def get_github_url(file_path: str):
    try:
        url = git_id.generate_github_url(file_path)
        return {"url": url}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

### CLI Tool Creation

```python
#!/usr/bin/env python3
import argparse
import sys
from git_identify import generate_github_url_direct

def main():
    parser = argparse.ArgumentParser(description='Generate GitHub URLs for files')
    parser.add_argument('file', help='File path to generate URL for')
    parser.add_argument('--copy', action='store_true', help='Copy URL to clipboard')

    args = parser.parse_args()

    try:
        url = generate_github_url_direct(args.file)
        print(url)

        if args.copy:
            import pyperclip
            pyperclip.copy(url)
            print("URL copied to clipboard!")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Jupyter Notebook Integration

```python
# In a Jupyter notebook cell
from IPython.display import HTML
from git_identify import generate_github_url_direct

def show_github_link(file_path):
    """Display a clickable GitHub link in Jupyter."""
    try:
        url = generate_github_url_direct(file_path)
        return HTML(f'<a href="{url}" target="_blank">View on GitHub</a>')
    except ValueError as e:
        return f"Error: {e}"

# Usage
show_github_link("notebook.ipynb")
```

### VS Code Extension Integration

```python
# Python script for VS Code extension
import json
import sys
from git_identify import generate_github_url_direct

def handle_request(file_path):
    try:
        url = generate_github_url_direct(file_path)
        return json.dumps({"success": True, "url": url})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else "."
    print(handle_request(file_path))
```

## 📋 Requirements

- Python >= 3.8
- Git repository (for repository operations)
- One of:
  - pygit2 >= 1.12.0 (preferred, C-based, faster)
  - GitPython >= 3.1.0 (pure Python, easier to install)

## 🔧 Development

### Install Development Dependencies

```bash
cd py
pip install -e ".[dev]"
# or manually:
pip install GitPython pytest black mypy
```

### Run Tests

```bash
# All tests
python3 -m pytest tests/

# With coverage
python3 -m pytest tests/ --cov=git_identify --cov-report=html

# Watch mode (requires pytest-watch)
pip install pytest-watch
ptw tests/
```

### Code Quality

```bash
# Format code
black git_identify/ tests/

# Type checking
mypy git_identify/

# Linting (if ruff is installed)
ruff check git_identify/
```

### Build Distribution

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Check package
twine check dist/*

# Upload to PyPI (requires credentials)
twine upload dist/*
```

## 🐛 Troubleshooting

### Common Issues

1. **ImportError: cannot import name 'GitFileId'**
   - Solution: Install with `pip install -e .` in the py directory

2. **ValueError: No .git directory found**
   - Solution: Ensure you're running from within a Git repository

3. **ValueError: No origin remote found**
   - Solution: Add a GitHub remote: `git remote add origin git@github.com:user/repo.git`

4. **ImportError: No module named 'pygit2'**
   - Solution: Install GitPython as fallback: `pip install GitPython`

5. **Path resolution errors on Windows**
   - Solution: Use forward slashes or `Path` objects from pathlib

### Backend Selection

The library automatically selects the best available backend:

```python
# Check which backend is being used
import git_identify.repository as repo
print("Using pygit2" if repo.USE_PYGIT2 else "Using GitPython")

# Force a specific backend (before importing GitFileId)
import sys
sys.modules['pygit2'] = None  # Force GitPython
from git_identify import GitFileId
```

## 🚦 Performance Tips

1. **Reuse GitFileId instances** - Repository discovery is cached
2. **Use batch operations** - Process multiple files with the same instance
3. **Prefer pygit2** - C-based implementation is faster for large repositories
4. **Cache results** - Store generated URLs if they don't change frequently

## 📄 License

MIT

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass: `python3 -m pytest tests/`
5. Format code: `black git_identify/`
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📚 See Also

- [Main package documentation](../README.md)
- [Rust implementation](../rust/README.md)
- [JavaScript/TypeScript implementation](../esm/README.md)
- [API specification](../spec/spec-0.0.1.md)

---

**Made with ❤️ for the Git community**