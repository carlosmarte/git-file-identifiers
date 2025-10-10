# Git Identifier Module - Requirements Specification

**Version:** 2.0.1
**Date:** 2025-10-10
**Status:** Draft

---

## 1. Executive Summary

### 1.1 Purpose
The **Git Identifier Module** provides a unified API and CLI interface for generating unique, deterministic file identifiers derived from Git or GitHub metadata. It abstracts both remote GitHub API operations and local Git repository introspection into a consistent metadata format.

### 1.2 Core Capabilities
- Generate deterministic unique identifiers for tracked files in GitHub repositories
- Generate deterministic unique identifiers for files in local Git repositories
- **Detect file changes without examining file content** by comparing identifiers
- Support both single-file and batch operations
- Provide programmatic API (ESM) and command-line interface (CLI)
- Normalize metadata across different sources (GitHub API vs local Git)

### 1.3 Use Cases
- **File change detection**: Compare identifiers to determine if files have changed without reading content
- **CI/CD pipeline file tracking**: Track which files changed between builds
- **Content-addressable file systems**: Use identifiers as immutable file references
- **Build artifact provenance**: Link build outputs to source file versions
- **Cross-repository file deduplication**: Identify identical files across repositories
- **Automated documentation systems**: Detect documentation updates based on source changes
- **Cache invalidation**: Determine when to rebuild or revalidate cached resources

---

## 2. System Architecture

### 2.1 High-Level Components

| Component | Responsibility | Dependencies |
|-----------|---------------|--------------|
| **GitHub Metadata Extractor** | Fetch repository, branch, commit, and file metadata via GitHub REST API | GitHub API v3, normalizeFilePath, isValidGitHash |
| **Local Git Metadata Extractor** | Extract commit, branch, and file hash from local repository using Git CLI | Git CLI (or WASM bindings), normalizeFilePath |
| **Metadata Normalizer** | Convert both remote and local metadata into standard JSON schema | parseGitHubUrl, buildGitHubUrl |
| **Identifier Generator** | Produce deterministic, reproducible identifier from normalized metadata | crypto (SHA-256) |
| **Batch Processor** | Process multiple file paths concurrently with error resilience | Promise.allSettled, GitBatchProcessor |
| **CLI Tool** | Command-line interface for identifier generation | Commander.js or similar |
| **ESM Module API** | Programmatic access for NodeJS/ESM environments | All core components |

### 2.2 Data Flow

```
┌─────────────────┐         ┌──────────────────┐
│  GitHub API     │         │  Local Git Repo  │
│  (Remote)       │         │  (Local)         │
└────────┬────────┘         └────────┬─────────┘
         │                           │
         v                           v
┌────────────────────────────────────────────┐
│       Metadata Normalizer                  │
│  (Standardized JSON Schema)                │
└────────┬───────────────────────────────────┘
         │
         v
┌────────────────────────────────────────────┐
│       Identifier Generator                 │
│  (SHA-256 Deterministic Hash)              │
└────────┬───────────────────────────────────┘
         │
         v
    Unique Identifier
```

---

## 3. Functional Requirements

### FR1: GitHub API Metadata Retrieval

**Priority:** High
**Status:** Required

#### Description
Retrieve comprehensive file metadata from GitHub REST API using repository coordinates and file path.

#### Input Schema
```json
{
  "owner": "string (required)",
  "repo": "string (required)",
  "filePath": "string (required)",
  "branch": "string (default: main/master)"
}
```

#### Process
1. Normalize file path using `normalizeFilePath()`
2. Call GitHub API endpoints:
   - `GET /repos/:owner/:repo/commits?path=:filePath&sha=:branch` → commit metadata
   - `GET /repos/:owner/:repo/contents/:filePath?ref=:branch` → file SHA and URL
3. Validate commit hash with `isValidGitHash()`
4. Construct metadata object
5. Handle rate limiting and authentication

#### Output Schema
```json
{
  "source": "github-api",
  "owner": "string",
  "repo": "string",
  "branch": "string",
  "filePath": "string (normalized)",
  "commitHash": "string (40-char hex)",
  "fileSha": "string (40-char hex)",
  "lastModified": "ISO 8601 timestamp",
  "htmlUrl": "string (GitHub permalink)"
}
```

#### Error Handling
- `FileNotFoundError`: File does not exist at specified path/branch
- `RepositoryNotFoundError`: Repository does not exist or is inaccessible
- `RateLimitError`: GitHub API rate limit exceeded
- `AuthenticationError`: Invalid or missing GitHub token

#### Acceptance Criteria
- ✅ Successfully retrieves metadata for any public repository file
- ✅ Supports authentication via `GITHUB_TOKEN` environment variable
- ✅ Returns normalized file paths (POSIX format)
- ✅ Validates all hash formats before returning

---

### FR2: Local Git Repository Metadata Retrieval

**Priority:** High
**Status:** Required

#### Description
Extract file metadata from a local Git repository using Git CLI commands or WASM bindings.

#### Input Schema
```json
{
  "repoPath": "string (required, absolute path)",
  "filePath": "string (required, relative to repo root)"
}
```

#### Process
1. Discover repository root: `git rev-parse --show-toplevel`
2. Normalize file path using `normalizeFilePath()`
3. Execute Git commands:
   - `git log -1 --pretty=format:%H -- <file>` → last commit hash
   - `git log -1 --pretty=format:%cI -- <file>` → commit timestamp
   - `git rev-parse --abbrev-ref HEAD` → current branch
   - `git ls-tree HEAD <file>` → blob hash
   - `git config --get remote.origin.url` → remote URL
4. Parse remote URL using `parseGitHubUrl()` to extract owner/repo
5. Construct metadata object

#### Output Schema
```json
{
  "source": "local-git",
  "owner": "string (from remote URL)",
  "repo": "string (from remote URL)",
  "repoPath": "string (absolute path)",
  "filePath": "string (relative, normalized)",
  "branch": "string",
  "commitHash": "string (40-char hex)",
  "fileHash": "string (40-char hex)",
  "lastModified": "ISO 8601 timestamp",
  "htmlUrl": "string (if GitHub remote detected)"
}
```

#### Error Handling
- `RepositoryNotFoundError`: No Git repository found at path
- `FileNotFoundError`: File not tracked in Git history
- `GitCommandError`: Git command execution failed

#### Acceptance Criteria
- ✅ Works with any valid Git repository
- ✅ Handles detached HEAD state
- ✅ Extracts owner/repo from GitHub, GitLab, and Bitbucket remotes
- ✅ Falls back gracefully when remote URL is not parseable

---

### FR3: Metadata Normalization

**Priority:** High
**Status:** Required

#### Description
Ensure consistent schema and canonical field ordering across both GitHub API and local Git sources.

#### Function Signature
```javascript
function normalizeMetadata(rawMeta: object): NormalizedMetadata
```

#### Normalized Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `source` | string | Yes | "github-api" or "local-git" |
| `owner` | string | Yes | GitHub username or derived from remote |
| `repo` | string | Yes | Repository name |
| `branch` | string | Yes | Current branch name |
| `commitHash` | string | Yes | Latest commit hash (40-char hex) |
| `filePath` | string | Yes | Normalized file path (POSIX) |
| `fileHash` | string | Yes | Blob SHA (40-char hex) |
| `lastModified` | string | Yes | ISO 8601 timestamp |
| `htmlUrl` | string | No | GitHub permalink (if applicable) |

#### Normalization Rules
1. All file paths converted to POSIX format (`/` separator)
2. Fields sorted alphabetically when serialized
3. All hashes validated with `isValidGitHash()`
4. Timestamps normalized to ISO 8601 UTC format
5. Empty/null fields excluded from output

#### Utility Dependencies
- `normalizeFilePath(filePath)`
- `parseGitHubUrl(remoteUrl)`
- `buildGitHubUrl(owner, repo, commitHash, filePath)`
- `isValidGitHash(hash)`

#### Acceptance Criteria
- ✅ Identical metadata produces identical normalized output
- ✅ Cross-platform path consistency (Windows ↔ Unix)
- ✅ Validates all hash formats
- ✅ Deterministic field ordering

---

### FR4: Unique Identifier Generation

**Priority:** High
**Status:** Required

#### Description
Generate a deterministic, reproducible unique identifier from normalized metadata.

#### Function Signature
```javascript
function generateIdentifier(
  meta: NormalizedMetadata,
  options?: IdentifierOptions
): IdentifierResult
```

#### Options Schema
```javascript
{
  algorithm: 'sha256' | 'sha1',  // default: sha256
  encoding: 'hex' | 'base64',    // default: hex
  truncate: number | false        // default: false (full hash)
}
```

#### Algorithm
1. Sort metadata keys alphabetically
2. Serialize to canonical JSON (no whitespace)
3. Hash serialized string using specified algorithm
4. Encode in specified format
5. Optionally truncate to specified length

#### Output Schema
```json
{
  "identifier": "string (full hash with prefix)",
  "short": "string (first 8 chars)",
  "algorithm": "string",
  "metadata": "object (input metadata)"
}
```

#### Example

**Input:**
```json
{
  "owner": "user",
  "repo": "repository",
  "branch": "main",
  "commitHash": "abc123def456...",
  "filePath": "src/index.js"
}
```

**Output:**
```json
{
  "identifier": "sha256:87ab5dcb40fefcc5d2e1a3b9f7c8d9e0...",
  "short": "87ab5dcb",
  "algorithm": "sha256"
}
```

#### Acceptance Criteria
- ✅ Identical metadata produces identical identifiers
- ✅ Different metadata produces different identifiers (collision resistance)
- ✅ Reproducible across different Node.js versions
- ✅ Supports both SHA-256 and SHA-1 algorithms

#### Change Detection Use Case

**Core Principle:** The identifier is derived from metadata including `fileHash` (blob SHA), which changes when file content changes. This enables change detection without reading file content.

**Workflow:**
1. Generate identifier at time T1 → store as `id1`
2. Generate identifier at time T2 → store as `id2`
3. Compare: `id1 === id2` → file unchanged; `id1 !== id2` → file changed

**Key Metadata Fields for Change Detection:**
- `fileHash`: Changes when file content changes (Git blob SHA)
- `commitHash`: Changes when any commit is made to the repository
- `branch`: Changes when branch switches occur

**Example:**
```javascript
// Time T1: Initial check
const meta1 = {
  owner: 'user',
  repo: 'repository',
  branch: 'main',
  commitHash: 'abc123def456...',
  filePath: 'src/index.js',
  fileHash: 'def456abc789...'  // Current file content hash
};
const id1 = generateIdentifier(meta1);
// id1.identifier = "sha256:87ab5dcb..."

// Time T2: File modified and committed
const meta2 = {
  owner: 'user',
  repo: 'repository',
  branch: 'main',
  commitHash: 'xyz789abc123...',  // New commit
  filePath: 'src/index.js',
  fileHash: '123abc456def...'     // New file content hash (CHANGED)
};
const id2 = generateIdentifier(meta2);
// id2.identifier = "sha256:9f2e1a3b..." (DIFFERENT)

// Detect change
if (id1.identifier !== id2.identifier) {
  console.log('File has changed since last check');
}
```

**Benefits:**
- ✅ No need to download or read file content
- ✅ Works across GitHub API and local Git repositories
- ✅ Deterministic and reproducible
- ✅ Efficient for large files or batch operations

---

### FR5: Batch Operations

**Priority:** Medium
**Status:** Required

#### Description
Process multiple files concurrently (GitHub API or local Git) with error resilience.

#### Function Signature
```javascript
async function generateBatchIdentifiers(
  inputs: BatchInput[],
  options?: BatchOptions
): Promise<BatchResult[]>
```

#### Input Schema
```javascript
// GitHub API batch
[
  { type: 'github', owner: 'user', repo: 'repo1', filePath: 'src/a.js' },
  { type: 'github', owner: 'user', repo: 'repo2', filePath: 'src/b.js' }
]

// Local Git batch
[
  { type: 'local', repoPath: '/path/to/repo', filePath: 'src/a.js' },
  { type: 'local', repoPath: '/path/to/repo', filePath: 'src/b.js' }
]
```

#### Options Schema
```javascript
{
  concurrency: number,        // default: 10
  continueOnError: boolean,   // default: true
  progressCallback: function  // optional
}
```

#### Output Schema
```json
[
  {
    "filePath": "src/a.js",
    "identifier": "sha256:abc123...",
    "status": "success",
    "metadata": { }
  },
  {
    "filePath": "src/b.js",
    "identifier": null,
    "status": "error",
    "error": "FileNotFoundError: File not tracked in Git"
  }
]
```

#### Implementation Details
- Uses `Promise.allSettled()` for robust parallelism
- Reuses `GitBatchProcessor` pattern from original module
- Respects GitHub API rate limits (automatic throttling)
- Provides progress callbacks for long-running operations

#### Acceptance Criteria
- ✅ Processes at least 50 files concurrently
- ✅ Continues processing on individual file errors
- ✅ Returns detailed error information for failed files
- ✅ Respects GitHub rate limits without failing

---

### FR6: CLI Interface

**Priority:** High
**Status:** Required

#### Description
Provide a command-line interface for generating identifiers from terminal.

#### Commands

##### 6.1 Single File (GitHub)
```bash
git-identify github <owner>/<repo> <filePath> [options]
```

**Options:**
- `--branch <name>`: Specify branch (default: main)
- `--output <format>`: Output format (json, yaml, text)
- `--short`: Use shortened identifier
- `--token <token>`: GitHub personal access token (or use GITHUB_TOKEN env)

**Example:**
```bash
$ git-identify github user/repo src/index.js --branch develop --short
87ab5dcb
```

##### 6.2 Single File (Local)
```bash
git-identify local <repoPath> <filePath> [options]
```

**Options:**
- `--output <format>`: Output format (json, yaml, text)
- `--short`: Use shortened identifier

**Example:**
```bash
$ git-identify local /Users/carlos/projects/repo src/index.js --output json
{
  "identifier": "sha256:87ab5dcb40fefcc5d2e1a3b9f7c8d9e0...",
  "filePath": "src/index.js",
  "commitHash": "abc123..."
}
```

##### 6.3 Batch Mode
```bash
git-identify batch <inputFile> [options]
```

**Input File Format (JSON):**
```json
[
  { "type": "github", "owner": "user", "repo": "repo", "filePath": "src/a.js" },
  { "type": "local", "repoPath": "/path/to/repo", "filePath": "src/b.js" }
]
```

**Options:**
- `--output <file>`: Write results to file
- `--parallel <n>`: Concurrency limit (default: 10)
- `--verbose`: Show progress and detailed errors

**Example:**
```bash
$ git-identify batch files.json --parallel 20 --output results.json
Processing 45 files...
✓ 43 succeeded
✗ 2 failed
Results written to results.json
```

#### Global Flags

| Flag | Description |
|------|-------------|
| `--version` | Show version number |
| `--help` | Display help information |
| `--no-color` | Disable colored output |
| `--verbose` | Enable verbose logging |

#### Acceptance Criteria
- ✅ All commands support stdin/stdout piping
- ✅ Exit codes: 0 (success), 1 (error), 2 (partial success in batch)
- ✅ Colored output for TTY, plain text for pipes
- ✅ Progress indicators for batch operations

---

### FR7: Programmatic API (ESM)

**Priority:** High
**Status:** Required

#### Description
Provide a clean, async JavaScript API for programmatic usage in Node.js or ESM environments.

#### Module Exports

```javascript
// Main functions
export async function getGitHubMetadata(owner, repo, filePath, branch?)
export async function getLocalMetadata(repoPath, filePath)
export function normalizeMetadata(rawMeta)
export function generateIdentifier(meta, options?)
export async function generateBatchIdentifiers(inputs, options?)

// Utility functions (re-exported)
export function normalizeFilePath(filePath)
export function parseGitHubUrl(remoteUrl)
export function buildGitHubUrl(owner, repo, commitHash, filePath)
export function isValidGitHash(hash)

// Classes
export class GitBatchProcessor
export class GitError
export class FileNotFoundError
export class RepositoryNotFoundError

// Helper functions
export async function getRepositoryInfo(filePath)
export async function isInGitRepository(path)
```

#### Usage Examples

##### Example 1: GitHub Metadata
```javascript
import { getGitHubMetadata, generateIdentifier } from 'git-identify';

const meta = await getGitHubMetadata('user', 'repo', 'src/index.js', 'main');
const id = generateIdentifier(meta, { truncate: 8 });
console.log(id.short); // "87ab5dcb"
```

##### Example 2: Local Repository
```javascript
import { getLocalMetadata, generateIdentifier } from 'git-identify';

const meta = await getLocalMetadata('/Users/carlos/projects/repo', 'src/index.js');
const id = generateIdentifier(meta);
console.log(id.identifier); // "sha256:87ab5dcb..."
```

##### Example 3: Batch Processing
```javascript
import { generateBatchIdentifiers } from 'git-identify';

const inputs = [
  { type: 'github', owner: 'user', repo: 'repo1', filePath: 'src/a.js' },
  { type: 'local', repoPath: '/path/to/repo', filePath: 'src/b.js' }
];

const results = await generateBatchIdentifiers(inputs, {
  concurrency: 10,
  progressCallback: (done, total) => console.log(`${done}/${total}`)
});

results.forEach(r => {
  if (r.status === 'success') {
    console.log(`${r.filePath}: ${r.identifier}`);
  } else {
    console.error(`${r.filePath}: ${r.error}`);
  }
});
```

#### Type Definitions (TypeScript)
```typescript
export interface NormalizedMetadata {
  source: 'github-api' | 'local-git';
  owner: string;
  repo: string;
  branch: string;
  commitHash: string;
  filePath: string;
  fileHash: string;
  lastModified: string;
  htmlUrl?: string;
}

export interface IdentifierOptions {
  algorithm?: 'sha256' | 'sha1';
  encoding?: 'hex' | 'base64';
  truncate?: number | false;
}

export interface IdentifierResult {
  identifier: string;
  short: string;
  algorithm: string;
  metadata?: NormalizedMetadata;
}

export interface BatchInput {
  type: 'github' | 'local';
  owner?: string;
  repo?: string;
  repoPath?: string;
  filePath: string;
  branch?: string;
}

export interface BatchResult {
  filePath: string;
  identifier: string | null;
  status: 'success' | 'error';
  error?: string;
  metadata?: NormalizedMetadata;
}
```

#### Acceptance Criteria
- ✅ All functions are fully async (return Promises)
- ✅ TypeScript definitions provided (index.d.ts)
- ✅ Tree-shakeable (supports ES module imports)
- ✅ Compatible with Node.js ≥ 18.0.0

---

### FR8: File Change Detection Patterns

**Priority:** High
**Status:** Required

#### Description
Provide patterns and workflows for detecting file changes by comparing identifiers generated from metadata at different points in time, **without needing to read file content**.

#### Core Concept

The module generates deterministic identifiers from file metadata. When metadata changes (particularly `fileHash`), the identifier changes. This enables lightweight change detection.

**Metadata Changes That Trigger New Identifiers:**
- **`fileHash`** (blob SHA) → File content modified
- **`commitHash`** → New commit to repository
- **`branch`** → Branch switch or rename

#### Pattern 1: Single File Change Detection

**Use Case:** Determine if a specific file has changed between two points in time.

**Workflow:**
```javascript
import { getGitHubMetadata, generateIdentifier } from 'git-identify';

// Store identifier at time T1
const meta1 = await getGitHubMetadata('user', 'repo', 'src/index.js', 'main');
const id1 = generateIdentifier(meta1);
await store('cache:src/index.js', id1.identifier);  // Store in cache/db

// Later, at time T2: check if file changed
const meta2 = await getGitHubMetadata('user', 'repo', 'src/index.js', 'main');
const id2 = generateIdentifier(meta2);
const cachedId = await retrieve('cache:src/index.js');

if (id2.identifier !== cachedId) {
  console.log('File changed - invalidate cache and rebuild');
} else {
  console.log('File unchanged - use cached version');
}
```

**Benefits:**
- ✅ No file download required
- ✅ Lightweight metadata-only comparison
- ✅ Works with GitHub API or local Git

#### Pattern 2: Batch File Change Detection

**Use Case:** Detect which files in a set have changed (e.g., in a CI/CD pipeline).

**Workflow:**
```javascript
import { generateBatchIdentifiers } from 'git-identify';

// Previous build identifiers (stored from last run)
const previousIds = {
  'src/index.js': 'sha256:abc123...',
  'src/lib.js': 'sha256:def456...',
  'src/utils.js': 'sha256:ghi789...'
};

// Current build: generate new identifiers
const inputs = [
  { type: 'github', owner: 'user', repo: 'repo', filePath: 'src/index.js' },
  { type: 'github', owner: 'user', repo: 'repo', filePath: 'src/lib.js' },
  { type: 'github', owner: 'user', repo: 'repo', filePath: 'src/utils.js' }
];

const results = await generateBatchIdentifiers(inputs);

// Compare and detect changes
const changed Files = results.filter(r => {
  return r.status === 'success' && r.identifier !== previousIds[r.filePath];
});

console.log(`${changedFiles.length} files changed:`, changedFiles.map(f => f.filePath));
```

**Benefits:**
- ✅ Efficient batch processing
- ✅ Parallel metadata fetching
- ✅ Identifies specific changed files

#### Pattern 3: Cache Invalidation

**Use Case:** Determine whether to rebuild cached assets based on source file changes.

**Implementation:**
```javascript
import { getLocalMetadata, generateIdentifier } from 'git-identify';
import fs from 'fs/promises';

async function shouldRebuild(sourceFile, cacheFile) {
  // Check if cache exists
  try {
    await fs.access(cacheFile);
  } catch {
    return true;  // Cache doesn't exist - rebuild
  }

  // Read stored identifier from cache metadata
  const cacheMetadata = JSON.parse(await fs.readFile(`${cacheFile}.meta`, 'utf8'));
  const cachedId = cacheMetadata.sourceIdentifier;

  // Generate current identifier
  const meta = await getLocalMetadata(process.cwd(), sourceFile);
  const currentId = generateIdentifier(meta);

  // Compare
  return currentId.identifier !== cachedId;
}

// Usage
if (await shouldRebuild('src/styles.scss', 'dist/styles.css')) {
  console.log('Source changed - rebuilding...');
  await rebuild();
} else {
  console.log('Source unchanged - using cache');
}
```

**Benefits:**
- ✅ Smart cache invalidation
- ✅ Avoids unnecessary rebuilds
- ✅ Fast metadata-based checks

#### Pattern 4: Cross-Repository File Tracking

**Use Case:** Track the same file across different repositories or branches.

**Workflow:**
```javascript
// Track file across multiple branches
const branches = ['main', 'develop', 'feature-x'];
const identifiers = {};

for (const branch of branches) {
  const meta = await getGitHubMetadata('user', 'repo', 'src/config.json', branch);
  const id = generateIdentifier(meta);
  identifiers[branch] = id.identifier;
}

// Check if branches have diverged for this file
const uniqueVersions = new Set(Object.values(identifiers));
if (uniqueVersions.size > 1) {
  console.log('File has different versions across branches');
} else {
  console.log('File is identical across all branches');
}
```

**Benefits:**
- ✅ Multi-branch comparison
- ✅ Detect divergence or synchronization
- ✅ Content-addressable file tracking

#### Pattern 5: Incremental Build System

**Use Case:** Only rebuild files that have changed since last build.

**Workflow:**
```javascript
import { generateBatchIdentifiers } from 'git-identify';

// Load previous build manifest
const manifest = JSON.parse(await fs.readFile('build-manifest.json', 'utf8'));

// Get current identifiers for all source files
const inputs = sourceFiles.map(f => ({
  type: 'local',
  repoPath: process.cwd(),
  filePath: f
}));

const results = await generateBatchIdentifiers(inputs);

// Detect changes
const filesToRebuild = results.filter(r => {
  return r.status === 'success' &&
         r.identifier !== manifest[r.filePath]?.identifier;
});

// Rebuild only changed files
for (const file of filesToRebuild) {
  console.log(`Rebuilding ${file.filePath}...`);
  await buildFile(file.filePath);

  // Update manifest
  manifest[file.filePath] = {
    identifier: file.identifier,
    builtAt: new Date().toISOString()
  };
}

// Save updated manifest
await fs.writeFile('build-manifest.json', JSON.stringify(manifest, null, 2));
```

**Benefits:**
- ✅ Incremental builds
- ✅ Build time optimization
- ✅ Accurate change tracking

#### API Support

**New Helper Functions:**
```javascript
// Compare two metadata objects
export function hasFileChanged(meta1, meta2): boolean

// Compare identifier against stored value
export function compareIdentifier(current, stored): boolean

// Generate change report for batch
export function generateChangeReport(current, previous): ChangeReport
```

**ChangeReport Schema:**
```typescript
interface ChangeReport {
  added: string[];      // New files
  modified: string[];   // Changed files
  removed: string[];    // Deleted files
  unchanged: string[];  // Identical files
}
```

#### Acceptance Criteria
- ✅ Identifiers deterministically reflect file content changes
- ✅ Metadata-only comparison (no file content download required)
- ✅ Supports both GitHub API and local Git workflows
- ✅ Batch operations efficiently detect multiple file changes
- ✅ Helper functions provided for common change detection patterns

---

## 4. Non-Functional Requirements

### NFR1: Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| Single file (GitHub API) | < 500ms | Average response time |
| Single file (Local Git) | < 100ms | Average execution time |
| Batch processing (50 files) | < 5s | Total execution time |
| Identifier generation | < 5ms | Per identifier |
| Memory usage (batch) | < 100MB | For 1000 files |

**Acceptance Criteria:**
- ✅ Batch mode processes at least 50 files concurrently
- ✅ No memory leaks in long-running batch operations
- ✅ Graceful degradation under GitHub rate limiting

---

### NFR2: Security

**Requirements:**
1. **Token Management**
   - Support GitHub tokens via `GITHUB_TOKEN` environment variable
   - Never log or expose tokens in error messages
   - Never accept tokens as CLI arguments (use env vars or config files)

2. **Input Validation**
   - Validate all file paths to prevent directory traversal
   - Sanitize all inputs before passing to Git CLI
   - Validate hash formats before processing

3. **Dependency Security**
   - No dependencies with known high/critical vulnerabilities
   - Regular security audits (`npm audit`)
   - Minimal dependency footprint

**Acceptance Criteria:**
- ✅ All file paths validated against directory traversal attacks
- ✅ No sensitive data logged to stdout/stderr
- ✅ Passes security audit with zero high/critical issues

---

### NFR3: Portability

**Requirements:**
- **Node.js:** ≥ 18.0.0 (native fetch support)
- **Git:** ≥ 2.20.0 (for local operations)
- **Operating Systems:** macOS, Linux, Windows
- **Module Format:** ESM (ECMAScript Modules)

**Acceptance Criteria:**
- ✅ Runs on Node.js 18.x, 20.x, 22.x
- ✅ Tests pass on macOS, Ubuntu, and Windows
- ✅ Uses POSIX path normalization for cross-platform consistency

---

### NFR4: Testability

**Requirements:**
1. **Mockable Dependencies**
   - GitHub API calls mockable (via fetch mocking)
   - Git CLI commands mockable (via command injection)
   - File system operations mockable

2. **Test Coverage**
   - Minimum 85% code coverage
   - 100% coverage for identifier generation
   - Integration tests for both GitHub API and local Git

3. **Test Utilities**
   - Mock GitHub API responses
   - Mock Git repository fixtures
   - Deterministic test outputs

**Acceptance Criteria:**
- ✅ All modules independently testable
- ✅ No external API calls in unit tests
- ✅ Fast test suite (< 10s for unit tests)

---

### NFR5: Determinism

**Requirements:**
1. **Reproducibility**
   - Identical metadata → identical identifiers
   - Consistent across Node.js versions
   - Consistent across operating systems

2. **Canonical Serialization**
   - Alphabetically sorted JSON keys
   - No whitespace in serialized JSON
   - UTC timestamps only

**Acceptance Criteria:**
- ✅ Same metadata produces same identifier across 100 runs
- ✅ Same identifier on macOS, Linux, Windows
- ✅ Same identifier on Node.js 18, 20, 22

---

### NFR6: Extensibility

**Future Support:**
- GitLab API integration
- Bitbucket API integration
- Custom hash algorithms (BLAKE3, etc.)
- Custom metadata schemas
- Plugin architecture for custom sources

**Design Patterns:**
- Abstract metadata extractor interface
- Strategy pattern for identifier generation
- Factory pattern for source selection

**Acceptance Criteria:**
- ✅ Pluggable architecture for new Git hosts
- ✅ Extensible metadata schema (custom fields)
- ✅ No breaking changes for new features

---

## 5. Error Handling

### Error Hierarchy

```
GitError (base class)
├── RepositoryNotFoundError
├── FileNotFoundError
├── InvalidHashError
├── RateLimitError
├── AuthenticationError
└── GitCommandError
```

### Error Properties

| Property | Type | Description |
|----------|------|-------------|
| `code` | string | Machine-readable error code |
| `message` | string | Human-readable error message |
| `cause` | Error | Original error (if wrapped) |
| `context` | object | Additional context (file path, repo, etc.) |

### Example Error
```javascript
{
  name: 'FileNotFoundError',
  code: 'FILE_NOT_FOUND',
  message: 'File "src/missing.js" not found in repository',
  context: {
    filePath: 'src/missing.js',
    repo: 'user/repository',
    branch: 'main'
  },
  cause: { /* original error */ }
}
```

### Error Handling Strategy
1. **User Errors:** Return descriptive error messages (e.g., "File not found")
2. **System Errors:** Log stack traces, return generic message
3. **Network Errors:** Retry with exponential backoff
4. **Rate Limit Errors:** Queue and retry after reset time

---

## 6. Deliverables

### 6.1 Core Module
**Path:** `src/git-identify.mjs`

**Contents:**
- GitFileId class
- Metadata extractors (GitHub API, Local Git)
- Metadata normalizer
- Identifier generator
- Batch processor
- Error classes
- Utility functions

---

### 6.2 CLI Entrypoint
**Path:** `bin/git-identify.js`

**Contents:**
- Command parser (using Commander.js or similar)
- Output formatters (JSON, YAML, text)
- Progress indicators
- Error handlers

---

### 6.3 Type Definitions
**Path:** `index.d.ts`

**Contents:**
- TypeScript definitions for all exported functions
- Interface definitions for metadata, identifiers, options
- Error class definitions

---

### 6.4 Tests
**Path:** `tests/`

**Files:**
- `github-api.test.mjs` - GitHub API metadata extraction
- `local-git.test.mjs` - Local Git metadata extraction
- `identifier.test.mjs` - Identifier generation
- `batch.test.mjs` - Batch operations
- `cli.test.mjs` - CLI interface
- `integration.test.mjs` - End-to-end tests
- `fixtures/` - Mock repositories and API responses

---

### 6.5 Documentation
**Path:** `README.md`

**Sections:**
- Installation
- Quick start
- API reference
- CLI reference
- Examples
- Error handling
- Contributing
- License

**Path:** `docs/`

**Files:**
- `api.md` - Detailed API documentation
- `cli.md` - Detailed CLI documentation
- `architecture.md` - System architecture
- `examples/` - Code examples

---

### 6.6 Configuration
**Path:** `package.json`

**Key Fields:**
```json
{
  "name": "git-identify",
  "version": "2.0.0",
  "type": "module",
  "exports": {
    ".": "./src/git-identify.mjs"
  },
  "bin": {
    "git-identify": "./bin/git-identify.js"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
```

---

### 6.7 Schema Definition
**Path:** `schema/metadata.schema.json`

**Purpose:** JSON Schema for normalized metadata format (for validation and documentation)

---

## 7. Acceptance Criteria Summary

### Must Have (MVP)
- ✅ FR1: GitHub API metadata retrieval
- ✅ FR2: Local Git metadata retrieval
- ✅ FR3: Metadata normalization
- ✅ FR4: Identifier generation (SHA-256)
- ✅ FR6: CLI interface (single file mode)
- ✅ FR7: Programmatic API
- ✅ NFR1-5: Performance, Security, Portability, Testability, Determinism

### Should Have (v2.1)
- ✅ FR5: Batch operations
- ✅ CLI batch mode
- ✅ Progress indicators
- ✅ Comprehensive error handling

### Could Have (Future)
- GitLab support
- Bitbucket support
- Custom hash algorithms
- Caching layer
- Plugin architecture

---

## 8. Appendix

### A. Example Outputs

#### A.1 Single File (CLI)
```bash
$ git-identify github user/repo src/index.js

Identifier: sha256:87ab5dcb40fefcc5d2e1a3b9f7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6
Short:      87ab5dcb
File:       src/index.js
Commit:     1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0
Branch:     main
```

#### A.2 Batch File (JSON Output)
```json
[
  {
    "filePath": "src/index.js",
    "identifier": "sha256:87ab5dcb...",
    "short": "87ab5dcb",
    "status": "success",
    "metadata": {
      "source": "github-api",
      "owner": "user",
      "repo": "repository",
      "commitHash": "1a2b3c4d..."
    }
  },
  {
    "filePath": "src/missing.js",
    "identifier": null,
    "status": "error",
    "error": "FileNotFoundError: File not tracked in Git"
  }
]
```

### B. Integration Patterns

#### B.1 CI/CD Pipeline
```yaml
# .github/workflows/track-files.yml
- name: Generate file identifiers
  run: |
    git-identify batch files.json --output identifiers.json

- name: Upload artifacts
  uses: actions/upload-artifact@v3
  with:
    name: file-identifiers
    path: identifiers.json
```

#### B.2 Build System
```javascript
// build.js
import { getLocalMetadata, generateIdentifier } from 'git-identify';

const files = ['src/index.js', 'src/lib.js'];
const identifiers = await Promise.all(
  files.map(async f => {
    const meta = await getLocalMetadata(process.cwd(), f);
    return generateIdentifier(meta);
  })
);

console.log('Build identifiers:', identifiers);
```

#### B.3 File Change Detection Workflow

**Scenario:** Detect which documentation files changed between two Git commits to determine which pages need regeneration.

```javascript
// detect-doc-changes.js
import { generateBatchIdentifiers } from 'git-identify';
import fs from 'fs/promises';

async function detectChangedDocs() {
  // Define documentation files to track
  const docFiles = [
    'docs/api.md',
    'docs/cli.md',
    'docs/examples.md',
    'docs/architecture.md'
  ];

  // Load previous commit identifiers (from last deployment)
  let previousIds = {};
  try {
    previousIds = JSON.parse(
      await fs.readFile('deploy-manifest.json', 'utf8')
    );
  } catch {
    console.log('No previous manifest found - treating all files as new');
  }

  // Generate current identifiers from HEAD
  const inputs = docFiles.map(filePath => ({
    type: 'local',
    repoPath: process.cwd(),
    filePath
  }));

  const results = await generateBatchIdentifiers(inputs, {
    concurrency: 10
  });

  // Analyze changes
  const report = {
    changed: [],
    unchanged: [],
    added: [],
    errors: []
  };

  for (const result of results) {
    if (result.status === 'error') {
      report.errors.push(result.filePath);
      continue;
    }

    const previousId = previousIds[result.filePath];

    if (!previousId) {
      // New file
      report.added.push(result.filePath);
    } else if (result.identifier !== previousId) {
      // Modified file
      report.changed.push(result.filePath);
    } else {
      // Unchanged file
      report.unchanged.push(result.filePath);
    }
  }

  // Output report
  console.log('\n📊 Documentation Change Report\n');
  console.log(`✅ Unchanged: ${report.unchanged.length} files`);
  console.log(`📝 Modified: ${report.changed.length} files`);
  console.log(`➕ Added: ${report.added.length} files`);
  console.log(`❌ Errors: ${report.errors.length} files\n`);

  if (report.changed.length > 0) {
    console.log('Modified files:');
    report.changed.forEach(f => console.log(`  - ${f}`));
  }

  if (report.added.length > 0) {
    console.log('\nAdded files:');
    report.added.forEach(f => console.log(`  - ${f}`));
  }

  // Update manifest for next run
  const newManifest = {};
  results.forEach(r => {
    if (r.status === 'success') {
      newManifest[r.filePath] = r.identifier;
    }
  });

  await fs.writeFile(
    'deploy-manifest.json',
    JSON.stringify(newManifest, null, 2)
  );

  console.log('\n✅ Manifest updated');

  // Only regenerate changed/added pages
  const filesToRegen = [...report.changed, ...report.added];
  if (filesToRegen.length > 0) {
    console.log(`\n🔨 Regenerating ${filesToRegen.length} pages...`);
    for (const file of filesToRegen) {
      await regenerateDoc(file);
    }
  } else {
    console.log('\n⏭️  No changes detected - skipping regeneration');
  }

  return report;
}

// Run detection
await detectChangedDocs();
```

**Output Example:**
```
📊 Documentation Change Report

✅ Unchanged: 2 files
📝 Modified: 1 files
➕ Added: 1 files
❌ Errors: 0 files

Modified files:
  - docs/api.md

Added files:
  - docs/architecture.md

✅ Manifest updated

🔨 Regenerating 2 pages...
```

**Benefits:**
- ✅ No content diffing required
- ✅ Fast metadata-only comparison
- ✅ Accurate change detection
- ✅ Works with any Git repository

#### B.4 Smart Cache Invalidation

**Scenario:** Cache compiled assets and only rebuild when source files change.

```javascript
// smart-cache.js
import { getLocalMetadata, generateIdentifier } from 'git-identify';
import fs from 'fs/promises';
import path from 'path';

class SmartCache {
  constructor(cacheDir = '.cache') {
    this.cacheDir = cacheDir;
  }

  async getCacheKey(sourceFile) {
    const meta = await getLocalMetadata(process.cwd(), sourceFile);
    const id = generateIdentifier(meta);
    return id.identifier;
  }

  async isCached(sourceFile) {
    const key = await this.getCacheKey(sourceFile);
    const cachePath = path.join(this.cacheDir, `${key}.json`);

    try {
      await fs.access(cachePath);
      return { cached: true, path: cachePath, key };
    } catch {
      return { cached: false, key };
    }
  }

  async get(sourceFile) {
    const { cached, path: cachePath } = await this.isCached(sourceFile);

    if (cached) {
      const data = await fs.readFile(cachePath, 'utf8');
      return JSON.parse(data);
    }

    return null;
  }

  async set(sourceFile, data) {
    const key = await this.getCacheKey(sourceFile);
    const cachePath = path.join(this.cacheDir, `${key}.json`);

    // Ensure cache directory exists
    await fs.mkdir(this.cacheDir, { recursive: true });

    // Write cache
    await fs.writeFile(cachePath, JSON.stringify(data, null, 2));

    console.log(`✅ Cached: ${sourceFile} → ${key.substring(0, 12)}...`);
  }

  async getOrCompute(sourceFile, computeFn) {
    // Check cache first
    const cached = await this.get(sourceFile);

    if (cached) {
      console.log(`📦 Cache hit: ${sourceFile}`);
      return cached;
    }

    // Cache miss - compute and store
    console.log(`🔨 Cache miss: ${sourceFile} - computing...`);
    const result = await computeFn(sourceFile);
    await this.set(sourceFile, result);

    return result;
  }
}

// Usage example
const cache = new SmartCache('.build-cache');

async function compileTypeScript(sourceFile) {
  return await cache.getOrCompute(sourceFile, async (file) => {
    // Expensive compilation here
    console.log(`  Compiling ${file}...`);
    const output = await compile(file);
    return { output, compiledAt: new Date().toISOString() };
  });
}

// First run: cache miss - compiles
await compileTypeScript('src/index.ts');
// Output: 🔨 Cache miss: src/index.ts - computing...
//           Compiling src/index.ts...
//         ✅ Cached: src/index.ts → sha256:87ab5...

// Second run: cache hit - no compilation
await compileTypeScript('src/index.ts');
// Output: 📦 Cache hit: src/index.ts

// After file modification: cache miss - recompiles
// (file change → new identifier → different cache key → cache miss)
```

**Benefits:**
- ✅ Automatic cache invalidation on file changes
- ✅ No manual cache key management
- ✅ Git-aware caching
- ✅ Works with any file type

### C. Migration Notes

#### From v1.x to v2.0
1. **Breaking Changes:**
   - ESM-only (no CommonJS support)
   - Async API (all functions return Promises)
   - Renamed `getFileHash()` → `getLocalMetadata()`

2. **Migration Guide:**
   ```javascript
   // v1.x (CommonJS, sync)
   const git = require('git-identify');
   const hash = git.getFileHash('src/index.js');

   // v2.0 (ESM, async)
   import { getLocalMetadata, generateIdentifier } from 'git-identify';
   const meta = await getLocalMetadata(process.cwd(), 'src/index.js');
   const id = generateIdentifier(meta);
   ```

---

## 9. References

- [Git Documentation](https://git-scm.com/doc)
- [GitHub REST API v3](https://docs.github.com/en/rest)
- [Node.js ESM](https://nodejs.org/api/esm.html)
- [SHA-256 Specification](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf)

---

**Document Control**
- **Author:** System Generated
- **Reviewers:** TBD
- **Last Updated:** 2025-10-10
- **Next Review:** TBD
