# Git Identify - Rust Module

Native Rust implementation of Git Identify with WASM support.

## 📦 Installation

Add to your `Cargo.toml`:

```toml
[dependencies]
git-identify = "0.0.1"
```

### Development Setup

```bash
# Clone and navigate to rust directory
cd rust

# Build the project
cargo build

# Build release version
cargo build --release

# Run tests
cargo test

# Run tests with output
cargo test -- --nocapture
```

## 🚀 Usage

### Basic Examples

#### Direct URL Generation
```rust
use git_identify::generate_github_url_direct;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let url = generate_github_url_direct("/path/to/file.rs")?;
    println!("GitHub URL: {}", url);
    Ok(())
}
```

#### Using GitFileId Instance
```rust
use git_identify::GitFileId;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut git_id = GitFileId::new();

    // Find repository
    git_id.find_repository("/path/to/repo")?;

    // Generate GitHub URL
    let url = git_id.generate_github_url("src/main.rs")?;
    println!("URL: {}", url);

    // Get file status
    let status = git_id.get_file_status("README.md")?;
    println!("Status: {}", status);

    // Get HEAD reference
    let head = git_id.get_head_ref()?;
    println!("HEAD: {}", head);

    Ok(())
}
```

#### Working with Git Objects
```rust
use git_identify::GitFileId;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut git_id = GitFileId::new();
    git_id.find_repository(".")?;

    // Get a commit
    let commit = git_id.get_commit("abc123def456")?;
    println!("Author: {} <{}>", commit.author_name(), commit.author_email());
    println!("Message: {}", commit.message());

    // Get a blob
    let blob = git_id.get_blob("def456abc789")?;
    println!("Size: {} bytes", blob.size());
    println!("Binary: {}", blob.is_binary());

    // Get a tree
    let tree = git_id.get_tree("789abcdef012")?;
    println!("Entries: {}", tree.len());

    Ok(())
}
```

## 📚 API Reference

### Structs

#### `GitFileId`
Main struct for Git repository operations.

**Methods:**
- `new() -> Self` - Create new instance
- `new_native() -> Self` - Create native instance (non-WASM)
- `find_repository(&mut self, file_path: &str) -> Result<()>` - Find repository
- `generate_github_url(&self, file_path: &str) -> Result<String>` - Generate URL
- `get_file_hash(&self, file_path: &str) -> Result<String>` - Get file hash
- `get_blob(&self, hash: &str) -> Result<GitBlob>` - Get blob
- `get_tree(&self, hash: &str) -> Result<GitTree>` - Get tree
- `get_commit(&self, hash: &str) -> Result<GitCommit>` - Get commit
- `get_tag(&self, hash: &str) -> Result<GitTag>` - Get tag
- `list_refs(&self) -> Result<Vec<String>>` - List references
- `list_refs_native(&self) -> Result<Vec<String>>` - List references (native)
- `get_file_status(&self, file_path: &str) -> Result<String>` - Get file status
- `get_head_ref(&self) -> Result<String>` - Get HEAD reference

### Functions

#### Repository Operations
```rust
pub fn find_git_root(start_path: &str) -> Result<PathBuf>
pub fn get_file_hash_at_commit(repo: &Repository, file_path: &str, commit_hash: &str) -> Result<String>
pub fn get_current_branch_commit_for_file(repo: &Repository, file_path: &str) -> Result<String>
pub fn get_remote_url(repo: &Repository) -> Result<String>
pub fn list_refs(repo: &Repository) -> Result<Vec<String>>
pub fn get_file_status(repo: &Repository, file_path: &str) -> Result<String>
pub fn get_head_ref(repo: &Repository) -> Result<String>
```

#### URL Building
```rust
pub fn parse_remote_url(remote_url: &str) -> Result<GitHubInfo>
pub fn build_github_url(github_info: &GitHubInfo, commit_hash: &str, file_path: &str) -> String
pub fn generate_github_url(remote_url: &str, commit_hash: &str, file_path: &str) -> Result<String>
pub fn generate_github_url_direct(file_path: &str) -> Result<String>
```

### Types

```rust
#[derive(Debug)]
pub struct GitBlob {
    id: String,
    size: usize,
    is_binary: bool,
}

#[derive(Debug)]
pub struct GitTree {
    id: String,
    len: usize,
}

#[derive(Debug)]
pub struct GitCommit {
    id: String,
    message: String,
    author_name: String,
    author_email: String,
    time: i64,
    tree_id: String,
    parent_ids: Vec<String>,
}

#[derive(Debug)]
pub struct GitTag {
    id: String,
    name: String,
    message: String,
    target_id: String,
}

#[derive(Debug, Clone)]
pub struct GitHubInfo {
    pub owner: String,
    pub repo: String,
}
```

## 🧪 Testing

```bash
# Run all tests
cargo test

# Run specific test
cargo test test_git_file_id_creation

# Run tests with output
cargo test -- --nocapture

# Run tests in single thread
cargo test -- --test-threads=1

# Run only unit tests
cargo test --lib

# Run only integration tests
cargo test --test integration_test
```

### Test Structure
- Unit tests: 28 tests in `src/` modules
- Integration tests: 6 tests in `tests/integration_test.rs`
- Total: 34 passing tests

## 🔧 Building

### Debug Build
```bash
cargo build
```

### Release Build
```bash
cargo build --release
```

### WASM Build
```bash
# Install wasm-pack if needed
cargo install wasm-pack

# Build WASM module
wasm-pack build --target web --out-dir pkg
```

## 📋 Features

### Cargo Features
```toml
[features]
default = []
wasm = ["wasm-bindgen", "web-sys"]
```

### Platform Support
- ✅ Linux
- ✅ macOS
- ✅ Windows
- ✅ WASM (WebAssembly)

## 🚀 Advanced Usage

### Error Handling
```rust
use git_identify::{GitFileId, generate_github_url_direct};

fn handle_errors() {
    match generate_github_url_direct("/path/to/file") {
        Ok(url) => println!("URL: {}", url),
        Err(e) => {
            if e.to_string().contains("No .git directory found") {
                eprintln!("Not in a git repository");
            } else if e.to_string().contains("No origin remote") {
                eprintln!("No GitHub remote configured");
            } else {
                eprintln!("Error: {}", e);
            }
        }
    }
}
```

### Custom Repository Operations
```rust
use git_identify::git::{repository, url_builder, objects};
use git2::Repository;

fn custom_operations() -> Result<(), Box<dyn std::error::Error>> {
    let git_root = repository::find_git_root(".")?;
    let repo = Repository::open(&git_root)?;

    // Get remote URL
    let remote_url = repository::get_remote_url(&repo)?;

    // Parse remote URL
    let github_info = url_builder::parse_remote_url(&remote_url)?;
    println!("Owner: {}, Repo: {}", github_info.owner, github_info.repo);

    // Get file status
    let status = repository::get_file_status(&repo, "Cargo.toml")?;
    println!("Cargo.toml status: {}", status);

    Ok(())
}
```

### Working with Multiple Repositories
```rust
use git_identify::GitFileId;

fn multiple_repos() -> Result<(), Box<dyn std::error::Error>> {
    let mut repo1 = GitFileId::new();
    repo1.find_repository("/path/to/repo1")?;

    let mut repo2 = GitFileId::new();
    repo2.find_repository("/path/to/repo2")?;

    // Work with different repositories
    let url1 = repo1.generate_github_url("file.rs")?;
    let url2 = repo2.generate_github_url("file.rs")?;

    Ok(())
}
```

## 📦 Dependencies

```toml
[dependencies]
wasm-bindgen = "0.2"
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
url = "2.5"
anyhow = "1.0"

[target.'cfg(not(target_arch = "wasm32"))'.dependencies]
git2 = { version = "0.18", default-features = false }

[dependencies.web-sys]
version = "0.3"
features = ["console"]
```

## 🐛 Troubleshooting

### Common Issues

1. **Error: failed to resolve: use of undeclared crate**
   - Solution: Run `cargo build` to download dependencies

2. **Error: No .git directory found**
   - Solution: Ensure you're running from within a Git repository

3. **Error: cannot find -lgit2**
   - Solution: Install libgit2 development files:
     - Ubuntu/Debian: `apt-get install libgit2-dev`
     - macOS: `brew install libgit2`
     - Windows: Use vcpkg or build from source

4. **WASM build errors**
   - Solution: Ensure wasm-pack is installed: `cargo install wasm-pack`

## 🚀 Performance

The Rust implementation offers excellent performance:
- Fast repository discovery
- Efficient Git object access
- Minimal memory overhead
- Zero-cost abstractions

### Benchmarks
```bash
cargo bench
```

## 📄 License

MIT

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Write tests for new features
4. Ensure all tests pass: `cargo test`
5. Format code: `cargo fmt`
6. Check lints: `cargo clippy`
7. Submit a pull request

---

For more information, see the [main README](../README.md) and [API specification](../spec/spec-0.0.1.md).