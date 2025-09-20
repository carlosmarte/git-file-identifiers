---
version: 0.0.1
---

# Git File Identifiers - Requirements Specification

## Overview
A Rust/NPM/Python library for Git repository operations, GitHub URL generation, and Git object manipulation. The library provides both native Rust and WASM bindings for JavaScript environments.

## Functional Requirements

### 1. Core Git Repository Operations

#### 1.1 Repository Discovery
- **Function**: `find_repository(file_path: string)` (src/lib.rs:34)
- **Function**: `find_git_root(start_path: &str)` (src/git/repository.rs:6)
- **Purpose**: Locate the Git repository root from any file or directory path
- **Requirements**:
  - Must search upward through parent directories until finding a `.git` directory
  - Must handle both file and directory paths as input
  - Must return the repository root path
  - Must handle cases where no Git repository exists

#### 1.2 Repository Initialization
- **Function**: `GitFileId::new()` (src/lib.rs:28)
- **Purpose**: Create a new GitFileId instance for repository operations
- **Requirements**:
  - Must initialize with empty repository path
  - Must log initialization in console (WASM environment)

### 2. GitHub URL Generation

#### 2.1 Direct URL Generation
- **Function**: `generate_github_url_direct(file_path: &str)` (src/lib.rs:244)
- **Purpose**: Generate GitHub URL in a single operation without instance creation
- **Requirements**:
  - Must find repository root automatically
  - Must extract remote URL from repository
  - Must get current branch commit hash
  - Must build properly formatted GitHub URL

#### 2.2 Instance-based URL Generation
- **Function**: `generate_github_url(file_path: &str)` (src/lib.rs:52)
- **Purpose**: Generate GitHub URL using an existing GitFileId instance
- **Requirements**:
  - Must require prior repository initialization via `find_repository()`
  - Must use cached repository path
  - Must handle relative paths within the repository

#### 2.3 URL Building and Parsing
- **Function**: `parse_remote_url(remote_url: &str)` (src/git/url_builder.rs:11)
- **Function**: `build_github_url(github_info, commit_hash, file_path)` (src/git/url_builder.rs:47)
- **Purpose**: Parse Git remote URLs and construct GitHub URLs
- **Requirements**:
  - Must support SSH format: `git@github.com:owner/repo.git`
  - Must support HTTPS format: `https://github.com/owner/repo.git`
  - Must support HTTP format: `http://github.com/owner/repo.git`
  - Must handle URLs with or without `.git` extension
  - Must normalize file paths (remove leading slashes, convert backslashes)

### 3. Git Object Access

#### 3.1 Blob Operations
- **Function**: `get_blob(hash: &str)` (src/lib.rs:103, src/git/objects.rs:194)
- **Purpose**: Retrieve Git blob objects by hash
- **Requirements**:
  - Must return blob ID, size, and binary status
  - Must validate object hash format
  - Must handle non-existent blobs

#### 3.2 Tree Operations
- **Function**: `get_tree(hash: &str)` (src/lib.rs:123, src/git/objects.rs:201)
- **Purpose**: Retrieve Git tree objects by hash
- **Requirements**:
  - Must return tree ID and entry count
  - Must validate object hash format
  - Must handle non-existent trees

#### 3.3 Commit Operations
- **Function**: `get_commit(hash: &str)` (src/lib.rs:143, src/git/objects.rs:208)
- **Purpose**: Retrieve Git commit objects by hash
- **Requirements**:
  - Must return commit ID, message, author info, timestamp, tree ID
  - Must include parent commit IDs
  - Must handle commits without messages or author info

#### 3.4 Tag Operations
- **Function**: `get_tag(hash: &str)` (src/lib.rs:163, src/git/objects.rs:215)
- **Purpose**: Retrieve Git tag objects by hash
- **Requirements**:
  - Must return tag ID, name, message, and target ID
  - Must handle annotated tags
  - Must handle tags without messages

### 4. Repository Status and Information

#### 4.1 File Hash Retrieval
- **Function**: `get_file_hash(file_path: &str)` (src/lib.rs:83)
- **Function**: `get_current_branch_commit_for_file(repo, file_path)` (src/git/repository.rs:39)
- **Purpose**: Get the commit hash for a specific file
- **Requirements**:
  - Must return current branch's commit hash for the file
  - Must validate file exists in repository
  - Must handle files not tracked in Git

#### 4.2 File Status
- **Function**: `get_file_status(file_path: &str)` (src/lib.rs:204, src/git/repository.rs:77)
- **Purpose**: Get Git status of a specific file
- **Requirements**:
  - Must return status: clean, modified, untracked, added, staged, deleted, unknown
  - Must include untracked files in status check
  - Must exclude ignored files

#### 4.3 HEAD Reference
- **Function**: `get_head_ref()` (src/lib.rs:224, src/git/repository.rs:110)
- **Purpose**: Get current HEAD reference
- **Requirements**:
  - Must return branch name if on a branch
  - Must return commit hash if in detached HEAD state

#### 4.4 Reference Listing
- **Function**: `list_refs()` (src/lib.rs:183, src/git/repository.rs:61)
- **Purpose**: List all Git references in repository
- **Requirements**:
  - Must return all branches, tags, and other references
  - Must include full reference names

#### 4.5 Remote URL Retrieval
- **Function**: `get_remote_url(repo: &Repository)` (src/git/repository.rs:54)
- **Purpose**: Get the origin remote URL
- **Requirements**:
  - Must retrieve "origin" remote URL
  - Must handle repositories without origin remote

### 5. Advanced Repository Operations

#### 5.1 File Hash at Specific Commit
- **Function**: `get_file_hash_at_commit(repo, file_path, commit_hash)` (src/git/repository.rs:29)
- **Purpose**: Get file blob hash at a specific commit
- **Requirements**:
  - Must retrieve file state at given commit
  - Must handle files that don't exist at that commit
  - Must validate commit hash format

## Non-Functional Requirements

### 6. Platform Support

#### 6.1 Native Rust Support
- **Requirements**:
  - Must work as native Rust library
  - Must support standard Rust error handling (Result types)
  - Must work with git2 library for Git operations

#### 6.2 NPM (MJS) Support
- **Requirements**:
  - Must provide ES module (.mjs) compatible package
  - Must export all public functions as named exports
  - Must include TypeScript definitions (.d.ts files)
  - Must handle async operations with Promises
  - Must provide proper JSDoc comments for IDE support
  - Must work in Node.js environments (v14+)

#### 6.3 Python Support
- **Requirements**:
  - Must provide Python bindings via PyO3 or similar
  - Must be installable via pip
  - Must follow Python naming conventions (snake_case)
  - Must provide type hints for all public functions
  - Must support Python 3.8+
  - Must handle Python exceptions appropriately
  - Must integrate with Python's git libraries (GitPython, pygit2)

### 7. Error Handling

#### 7.1 Error Types
- **Requirements**:
  - Must handle invalid file paths
  - Must handle non-existent repositories
  - Must handle invalid Git object hashes
  - Must handle missing remote URLs
  - Must handle unsupported URL formats
  - Must provide descriptive error messages

#### 7.2 WASM Error Conversion
- **Requirements**:
  - Must convert Rust errors to JsValue for JavaScript
  - Must preserve error messages across FFI boundary

### 8. Performance Requirements

#### 8.1 Repository Search
- **Requirements**:
  - Must efficiently search upward for `.git` directory
  - Must cache repository path after initial discovery

#### 8.2 Git Operations
- **Requirements**:
  - Must minimize repository opening operations
  - Must reuse repository handles when possible

### 9. Testing Requirements

#### 9.1 Unit Tests
- **Requirements**:
  - Must test all URL parsing formats
  - Must test path normalization
  - Must test Git object retrieval
  - Must test error conditions

#### 9.2 Integration Tests
- **Requirements**:
  - Must test against actual Git repositories
  - Must test file status detection
  - Must test reference listing

### 10. JavaScript/Node.js Integration

#### 10.1 Module Export
- **Requirements**:
  - Must export as ES module (index.mjs)
  - Must provide TypeScript definitions
  - Must support both CommonJS and ES module imports

#### 10.2 NPM Package
- **Requirements**:
  - Must be publishable as NPM package
  - Must include only necessary files in package
  - Must specify Node.js version requirements (>=14.0.0)

## Data Structures

### GitBlob
- `id`: String - Object SHA hash
- `size`: usize - Blob size in bytes
- `is_binary`: bool - Binary file indicator

### GitTree
- `id`: String - Object SHA hash
- `len`: usize - Number of tree entries

### GitCommit
- `id`: String - Commit SHA hash
- `message`: String - Commit message
- `author_name`: String - Author name
- `author_email`: String - Author email
- `time`: i64 - Unix timestamp
- `tree_id`: String - Tree object hash
- `parent_ids`: Vec<String> - Parent commit hashes

### GitTag
- `id`: String - Tag object SHA hash
- `name`: String - Tag name
- `message`: String - Tag annotation message
- `target_id`: String - Target object hash

### GitHubInfo
- `owner`: String - Repository owner/organization
- `repo`: String - Repository name

## Security Requirements

### 11.1 Input Validation
- Must validate all file paths before filesystem access
- Must validate Git object hashes are valid SHA format
- Must sanitize URLs before parsing

### 11.2 Path Traversal Prevention
- Must prevent directory traversal attacks in file paths
- Must validate paths stay within repository boundaries

## Compatibility Requirements

### 12.1 Git Compatibility
- Must work with Git repositories version 2.0 and above
- Must handle different Git configurations

### 12.2 GitHub Compatibility
- Must generate URLs compatible with GitHub.com
- Must handle both public and private repository URL formats

## Documentation Requirements

### 13.1 API Documentation
- All public functions must have clear documentation
- Must provide usage examples for main operations
- Must document error conditions

### 13.2 Build Documentation
- Must document build process from source
- Must document WASM compilation steps
- Must document testing procedures