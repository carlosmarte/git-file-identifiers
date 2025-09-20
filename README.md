# Git Identify

A multi-language library for Git repository operations, GitHub URL generation, and Git object manipulation. Available for JavaScript/TypeScript (ESM), Rust, and Python.

## 📋 Overview

Git Identify provides a unified API across multiple programming languages for:
- 🔍 Repository discovery from any file or directory path
- 🔗 GitHub URL generation with commit hash
- 📦 Git object access (blobs, trees, commits, tags)
- 📊 Repository status and information
- ✨ File status checking and reference listing

## 🚀 Quick Start

### JavaScript/TypeScript (ESM)

```bash
cd esm
npm install
npm test
```

```javascript
import { GitFileId, generateGithubUrlDirect } from '@git-identify/esm';

// Direct URL generation
const url = await generateGithubUrlDirect('/path/to/file.js');
console.log(url); // https://github.com/owner/repo/blob/commit/path/to/file.js
```

[Full ESM documentation →](./esm/README.md)

### Rust

```bash
cd rust
cargo build --release
cargo test
```

```rust
use git_identify::{GitFileId, generate_github_url_direct};

// Direct URL generation
let url = generate_github_url_direct("/path/to/file.rs")?;
println!("{}", url); // https://github.com/owner/repo/blob/commit/path/to/file.rs
```

[Full Rust documentation →](./rust/README.md)

### Python

```bash
cd py
pip install GitPython pytest
python3 -m pytest tests/
```

```python
from git_identify import GitFileId, generate_github_url_direct

# Direct URL generation
url = generate_github_url_direct("/path/to/file.py")
print(url)  # https://github.com/owner/repo/blob/commit/path/to/file.py
```

[Full Python documentation →](./py/README.md)

## 📁 Project Structure

```
git-identify/
├── esm/          # JavaScript/TypeScript implementation
├── rust/         # Rust implementation
├── py/           # Python implementation
└── spec/         # Specification documents
```

## 🧪 Testing

### Run All Tests

```bash
# JavaScript/TypeScript
cd esm && npm test

# Rust
cd rust && cargo test

# Python
cd py && python3 -m pytest tests/
```

### Test Results Summary

| Language | Tests | Status |
|----------|-------|--------|
| JavaScript/TypeScript | 47 tests | ✅ All passing |
| Rust | 34 tests | ✅ All passing |
| Python | 126 tests | ✅ All passing |

## 🛠️ Development Setup

### Prerequisites

- **Node.js** ≥ 14.0.0 (for ESM)
- **Rust** ≥ 1.70.0 (for Rust)
- **Python** ≥ 3.8 (for Python)
- **Git** repository (for testing)

### Installation Commands

#### JavaScript/TypeScript (ESM)
```bash
cd esm
npm install
npm run build        # Build the project
npm test            # Run tests
npm run test:watch  # Run tests in watch mode
```

#### Rust
```bash
cd rust
cargo build         # Build debug version
cargo build --release  # Build release version
cargo test          # Run all tests
cargo test -- --nocapture  # Run tests with output
```

#### Python
```bash
cd py
# Install dependencies
python3 -m pip install GitPython pytest

# Install in development mode
pip install -e .

# Run tests
python3 -m pytest tests/ -v  # Verbose output
python3 -m pytest tests/ -q  # Quiet output
python3 example.py  # Run example script
```

## 📊 Feature Matrix

| Feature | ESM | Rust | Python |
|---------|-----|------|--------|
| Repository Discovery | ✅ | ✅ | ✅ |
| GitHub URL Generation | ✅ | ✅ | ✅ |
| Git Objects Access | ✅ | ✅ | ✅ |
| File Status | ✅ | ✅ | ✅ |
| Reference Listing | ✅ | ✅ | ✅ |
| HEAD Reference | ✅ | ✅ | ✅ |
| WASM Support | 🚧 | ✅ | N/A |
| Async/Await | ✅ | N/A | N/A |
| Type Safety | ✅ (TS) | ✅ | ✅ (hints) |

## 🔧 Core API

All implementations provide these core functions:

### Repository Operations
- `findGitRoot(path)` - Find repository root from any path
- `getFileStatus(path)` - Get Git status of a file
- `getHeadRef()` - Get current HEAD reference
- `listRefs()` - List all repository references

### GitHub URL Generation
- `generateGithubUrlDirect(path)` - Generate URL in one call
- `generateGithubUrl(path)` - Generate URL with instance

### Git Objects
- `getBlob(hash)` - Retrieve blob by hash
- `getTree(hash)` - Retrieve tree by hash
- `getCommit(hash)` - Retrieve commit by hash
- `getTag(hash)` - Retrieve tag by hash

## 📝 Examples

### Complete Example (Python)
```python
from git_identify import GitFileId

# Create instance
git_id = GitFileId()
git_id.find_repository("/path/to/repo")

# Get repository information
head = git_id.get_head_ref()
refs = git_id.list_refs()
status = git_id.get_file_status("README.md")

# Generate GitHub URL
url = git_id.generate_github_url("src/main.py")
print(f"File URL: {url}")
```

### Complete Example (TypeScript)
```typescript
import { GitFileId } from '@git-identify/esm';

// Create instance
const gitId = new GitFileId();
await gitId.findRepository('/path/to/repo');

// Get repository information
const head = await gitId.getHeadRef();
const refs = await gitId.listRefs();
const status = await gitId.getFileStatus('README.md');

// Generate GitHub URL
const url = await gitId.generateGithubUrl('src/main.ts');
console.log(`File URL: ${url}`);
```

### Complete Example (Rust)
```rust
use git_identify::GitFileId;

// Create instance
let mut git_id = GitFileId::new();
git_id.find_repository("/path/to/repo")?;

// Get repository information
let head = git_id.get_head_ref()?;
let refs = git_id.list_refs()?;
let status = git_id.get_file_status("README.md")?;

// Generate GitHub URL
let url = git_id.generate_github_url("src/main.rs")?;
println!("File URL: {}", url);
```

## 🧪 Test Coverage

### JavaScript/TypeScript Tests
```bash
cd esm
npm test -- --coverage
```

### Rust Tests
```bash
cd rust
cargo test -- --test-threads=1
```

### Python Tests
```bash
cd py
python3 -m pytest tests/ --cov=git_identify
```

## 🔍 Debugging

### Enable Debug Output

#### JavaScript/TypeScript
```bash
DEBUG=git-identify npm test
```

#### Rust
```bash
RUST_LOG=debug cargo test
```

#### Python
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Documentation

- [ESM Module Documentation](./esm/README.md)
- [Rust Module Documentation](./rust/README.md)
- [Python Module Documentation](./py/README.md)
- [API Specification](./spec/spec-0.0.1.md)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests in your target language
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built with git2 (Rust), simple-git (JavaScript), and GitPython (Python)
- Inspired by the need for cross-language Git repository tooling
- Specification-driven development for consistency across implementations

## 🚦 Status

| Component | Status | Version |
|-----------|--------|---------|
| ESM Module | ✅ Stable | 0.0.1 |
| Rust Module | ✅ Stable | 0.0.1 |
| Python Module | ✅ Stable | 0.0.1 |
| WASM Support | 🚧 In Progress | - |

## 🐛 Troubleshooting

### Common Issues

#### JavaScript/TypeScript
- **Issue**: `Cannot find module 'simple-git'`
  - **Solution**: Run `npm install` in the esm directory

#### Rust
- **Issue**: `error[E0433]: failed to resolve: use of undeclared crate`
  - **Solution**: Run `cargo build` to download dependencies

#### Python
- **Issue**: `ImportError: cannot import name 'GitFileId'`
  - **Solution**: Install with `pip install -e .` in the py directory

### Getting Help

- Check the [specification](./spec/spec-0.0.1.md) for API details
- Review language-specific README files
- Open an issue on GitHub for bugs or questions

---

**Made with ❤️ for the Git community**