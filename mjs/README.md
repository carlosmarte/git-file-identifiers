# git-identify

> Generate unique, deterministic file identifiers from Git or GitHub metadata for file change detection without reading content

[![Node.js Version](https://img.shields.io/badge/node-%3E%3D22.0.0-brightgreen)](https://nodejs.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Overview

**git-identify** provides a unified API and CLI for generating unique, deterministic file identifiers derived from Git or GitHub metadata. It enables **file change detection without reading file content** by comparing identifiers generated from metadata at different points in time.

### Key Features

✅ **Metadata-based change detection** - Detect file changes without downloading or reading content
✅ **Deterministic identifiers** - Same metadata → same ID (reproducible across platforms)
✅ **Dual source support** - Works with both GitHub API and local Git repositories
✅ **Batch operations** - Process multiple files concurrently with error resilience
✅ **Pure ESM** - Modern Node.js 22+ with native APIs (fetch, crypto)
✅ **Zero dependencies** - Uses only Node.js built-in modules
✅ **TypeScript definitions** - Full type safety support

## Installation

```bash
npm install git-identify
```

## Quick Start

### Local Git Repository

```javascript
import { getLocalMetadata, generateIdentifier } from 'git-identify';

// Get metadata from local Git repository
const metadata = await getLocalMetadata(process.cwd(), 'src/index.js');

// Generate deterministic identifier
const { identifier, short } = generateIdentifier(metadata);

console.log(identifier); // "sha256:87ab5dcb..."
console.log(short);      // "87ab5dcb"
```

### GitHub API

```javascript
import { getGitHubMetadata, generateIdentifier } from 'git-identify';

// Set GitHub token (optional but recommended)
process.env.GITHUB_TOKEN = 'your-token-here';

// Get metadata from GitHub
const metadata = await getGitHubMetadata('owner', 'repo', 'src/index.js', 'main');

// Generate identifier
const { identifier } = generateIdentifier(metadata);

console.log(identifier); // "sha256:87ab5dcb..."
```

### File Change Detection

```javascript
import { getLocalMetadata, generateIdentifier } from 'git-identify';

// Time T1: Store initial identifier
const meta1 = await getLocalMetadata(process.cwd(), 'src/index.js');
const id1 = generateIdentifier(meta1);
await storage.set('src/index.js', id1.identifier);

// ... file gets modified and committed ...

// Time T2: Check if file changed
const meta2 = await getLocalMetadata(process.cwd(), 'src/index.js');
const id2 = generateIdentifier(meta2);
const cachedId = await storage.get('src/index.js');

if (id2.identifier !== cachedId) {
  console.log('File changed - rebuild required');
} else {
  console.log('File unchanged - use cache');
}
```

## API Reference

### Core Functions

#### `getLocalMetadata(repoPath, filePath)`
Extract metadata from a local Git repository.

```javascript
const metadata = await getLocalMetadata('/path/to/repo', 'src/file.js');
// Returns: { source, owner, repo, branch, commitHash, fileHash, ... }
```

#### `getGitHubMetadata(owner, repo, filePath, branch?)`
Fetch metadata from GitHub API.

```javascript
const metadata = await getGitHubMetadata('user', 'repo', 'src/file.js', 'main');
// Returns: { source, owner, repo, branch, commitHash, fileSha, htmlUrl, ... }
```

#### `generateIdentifier(metadata, options?)`
Generate deterministic identifier from metadata.

```javascript
const result = generateIdentifier(metadata, {
  algorithm: 'sha256',  // or 'sha1'
  encoding: 'hex',      // or 'base64'
  truncate: false       // or number of chars
});
// Returns: { identifier, short, algorithm }
```

#### `generateBatchIdentifiers(inputs, options?)`
Process multiple files in parallel.

```javascript
const results = await generateBatchIdentifiers([
  { type: 'github', owner: 'user', repo: 'repo', filePath: 'src/a.js' },
  { type: 'local', repoPath: '/path/to/repo', filePath: 'src/b.js' }
], {
  concurrency: 10,
  progressCallback: (done, total) => console.log(`${done}/${total}`)
});
```

### Change Detection Helpers

#### `hasFileChanged(meta1, meta2)`
Compare two metadata objects to detect changes.

```javascript
const changed = hasFileChanged(oldMetadata, newMetadata);
```

#### `generateChangeReport(current, previous)`
Generate detailed change report.

```javascript
const report = generateChangeReport(currentResults, previousManifest);
// Returns: { added: [], modified: [], unchanged: [], removed: [], errors: [] }
```

#### `createManifest(results)`
Create manifest from batch results for storage.

```javascript
const manifest = createManifest(batchResults);
// Returns: { 'file1.js': 'sha256:abc...', 'file2.js': 'sha256:def...' }
```

### Utility Functions

- `normalizeFilePath(path)` - Normalize path to POSIX format
- `parseGitHubUrl(remoteUrl)` - Parse Git remote URL
- `buildGitHubUrl(owner, repo, commit, path)` - Build GitHub permalink
- `isValidGitHash(hash)` - Validate Git hash format
- `isGitRepository(path)` - Check if path is a Git repo

## Use Cases

### 1. Cache Invalidation

Automatically invalidate caches when source files change:

```javascript
import { getLocalMetadata, generateIdentifier } from 'git-identify';

async function getCacheKey(sourceFile) {
  const meta = await getLocalMetadata(process.cwd(), sourceFile);
  const { identifier } = generateIdentifier(meta);
  return identifier;
}

// File change → new identifier → cache miss → rebuild
```

### 2. Incremental Builds

Only rebuild files that changed:

```javascript
import { generateBatchIdentifiers, generateChangeReport } from 'git-identify';

const previousManifest = JSON.parse(fs.readFileSync('manifest.json'));
const inputs = sourceFiles.map(f => ({
  type: 'local',
  repoPath: process.cwd(),
  filePath: f
}));

const results = await generateBatchIdentifiers(inputs);
const report = generateChangeReport(results, previousManifest);

console.log(`Modified files: ${report.modified.length}`);
// Rebuild only modified files
```

### 3. CI/CD File Tracking

Track which files changed between builds:

```javascript
// In your CI/CD pipeline
const results = await generateBatchIdentifiers(filesToTrack);
fs.writeFileSync('identifiers.json', JSON.stringify(results, null, 2));
```

## Metadata Schema

Both `getLocalMetadata()` and `getGitHubMetadata()` return normalized metadata:

```typescript
{
  source: 'local-git' | 'github-api',
  owner: string,          // Repository owner
  repo: string,           // Repository name
  branch: string,         // Current branch
  commitHash: string,     // Latest commit (40-char hex)
  fileHash: string,       // Blob SHA (40-char hex)
  filePath: string,       // Normalized POSIX path
  lastModified: string,   // ISO 8601 timestamp
  htmlUrl?: string        // GitHub permalink (if applicable)
}
```

## Error Handling

The module provides typed error classes:

```javascript
import {
  GitError,
  RepositoryNotFoundError,
  FileNotFoundError,
  RateLimitError,
  AuthenticationError
} from 'git-identify';

try {
  const metadata = await getLocalMetadata('/invalid/path', 'file.js');
} catch (error) {
  if (error instanceof RepositoryNotFoundError) {
    console.error('Not a Git repository');
  } else if (error instanceof FileNotFoundError) {
    console.error('File not tracked in Git');
  }
}
```

## Requirements

- **Node.js:** ≥ 22.0.0
- **Git:** ≥ 2.20.0 (for local operations)
- **GitHub Token:** Optional (recommended for API to avoid rate limits)

Set `GITHUB_TOKEN` environment variable:

```bash
export GITHUB_TOKEN=your_personal_access_token
```

## License

MIT

## Contributing

Contributions welcome! Please see the [spec document](../spec/spec-2.0.1.md) for detailed requirements.
