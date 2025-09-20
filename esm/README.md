# Git Identify - ESM Module

JavaScript/TypeScript implementation of Git Identify for ES Modules.

## 📦 Installation

```bash
npm install @thinkeloquent/git-identify-esm
# or
yarn add @thinkeloquent/git-identify-esm
# or
pnpm add @thinkeloquent/git-identify-esm
```

### Development Setup

```bash
# Clone and navigate to esm directory
cd esm

# Install dependencies
npm install

# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Build the project
npm run build

# Run linting
npm run lint

# Run type checking
npm run typecheck
```

## 🚀 Usage

```javascript
import { generateGitHubUrlDirect } from '@thinkeloquent/git-identify-esm';

// Generate GitHub URL for a file
const url = await generateGitHubUrlDirect('./src/main.js');
console.log(url); // https://github.com/owner/repo/blob/commit-hash/src/main.js

// With error handling
try {
  const url = await generateGitHubUrlDirect('/path/to/file.js');
  console.log(`GitHub URL: ${url}`);
} catch (error) {
  console.error('Failed to generate URL:', error.message);
}
```

## API Overview

### Core Classes

#### GitFileId
Main class for Git repository operations.

```javascript
import { GitFileId } from '@thinkeloquent/git-identify-esm';

const git = new GitFileId();
await git.findRepository('./path/to/repo');

// Generate GitHub URLs
const url = await git.generateGitHubUrl('src/index.js');

// Get file information
const status = await git.getFileStatus('package.json');
const hash = await git.getFileHash('README.md');

// Access repository information
const branch = await git.getHeadRef();
const refs = await git.listRefs();
```

#### Git Object Classes
- **GitBlob**: Represents file objects
- **GitTree**: Represents directory objects
- **GitCommit**: Represents commit objects
- **GitTag**: Represents tag objects

```javascript
const commit = await git.getCommit(commitHash);
console.log(commit.message, commit.authorName, commit.date);

const blob = await git.getBlob(blobHash);
console.log(blob.size, blob.isBinary);
```

### Utility Functions

```javascript
import {
  parseGitHubUrl,
  buildGitHubUrl,
  isValidGitHash,
  normalizeFilePath,
  getRepositoryInfo,
  isInGitRepository
} from '@thinkeloquent/git-identify-esm';

// Parse Git remote URLs
const { owner, repo } = parseGitHubUrl('git@github.com:user/repo.git');

// Build GitHub URLs
const url = buildGitHubUrl('owner', 'repo', 'commit-hash', 'path/to/file.js');

// Validate Git hashes
const isValid = isValidGitHash('abc123def456...');

// Check repository status
const isRepo = await isInGitRepository('./some/path');
const info = await getRepositoryInfo('package.json');
```

### Batch Processing

Process multiple files efficiently:

```javascript
import { GitBatchProcessor } from '@thinkeloquent/git-identify-esm';

const batch = new GitBatchProcessor();
await batch.initialize('./repo');

// Generate URLs for multiple files
const urls = await batch.generateUrls(['file1.js', 'file2.js', 'file3.js']);

// Get statuses for multiple files
const statuses = await batch.getStatuses(['README.md', 'package.json']);
```

### Error Handling

Custom error classes for better error handling:

```javascript
import {
  GitError,
  RepositoryNotFoundError,
  FileNotFoundError
} from '@thinkeloquent/git-identify-esm';

try {
  await git.findRepository('/invalid/path');
} catch (error) {
  if (error instanceof RepositoryNotFoundError) {
    console.log('No repository found at:', error.path);
  }
}
```

## 📚 Complete Examples

See [`examples.mjs`](./examples.mjs) for comprehensive usage examples covering:

1. Quick URL generation
2. Repository operations
3. File operations
4. Git objects access
5. URL utilities
6. Repository information
7. Repository detection
8. Batch processing
9. Error handling
10. Advanced Git operations

Run the examples:

```bash
node esm/examples.mjs
```

## 🧪 Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm test -- --coverage

# Run specific test file
npm test -- path/to/test.js
```

### Test Structure
- Unit tests for all core functions
- Integration tests for repository operations
- Mock tests for edge cases
- Total: 47 passing tests

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `GitFileId` | Main class for repository operations |
| `GitBlob` | Git blob (file) object |
| `GitTree` | Git tree (directory) object |
| `GitCommit` | Git commit object |
| `GitTag` | Git tag object |
| `GitBatchProcessor` | Batch operations helper |
| `GitError` | Base error class |
| `RepositoryNotFoundError` | Repository not found error |
| `FileNotFoundError` | File not found error |

### Functions

| Function | Description |
|----------|-------------|
| `generateGitHubUrlDirect(path)` | Generate GitHub URL directly |
| `parseGitHubUrl(url)` | Parse Git remote URL |
| `buildGitHubUrl(owner, repo, hash, path)` | Build GitHub URL |
| `isValidGitHash(hash)` | Validate Git hash |
| `normalizeFilePath(path)` | Normalize file path |
| `getRepositoryInfo(path)` | Get repository info |
| `isInGitRepository(path)` | Check if in repository |

## 📋 Requirements

- Node.js >= 14.0.0
- Git repository (for repository operations)
- WASM support in Node.js

## 🚀 Integration Instructions

### NPM Package Integration

1. **Install the package:**
   ```bash
   npm install @thinkeloquent/git-identify-esm
   ```

2. **Import in your project:**
   ```javascript
   // ES Modules
   import { GitFileId, generateGitHubUrlDirect } from '@thinkeloquent/git-identify-esm';

   // CommonJS (if transpiled)
   const { GitFileId, generateGitHubUrlDirect } = require('@thinkeloquent/git-identify-esm');
   ```

3. **Use in your application:**
   ```javascript
   // In an async function
   async function getGitHubLink(filePath) {
     try {
       const url = await generateGitHubUrlDirect(filePath);
       return url;
     } catch (error) {
       console.error('Not in a git repository or no remote configured');
       return null;
     }
   }
   ```

### Browser Integration (via bundler)

```javascript
// webpack.config.js or vite.config.js
export default {
  resolve: {
    alias: {
      '@git-identify': '@thinkeloquent/git-identify-esm'
    }
  }
};
```

### Node.js Script Integration

```javascript
#!/usr/bin/env node
import { GitFileId } from '@thinkeloquent/git-identify-esm';

const git = new GitFileId();
await git.findRepository(process.cwd());

const url = await git.generateGitHubUrl(process.argv[2] || 'README.md');
console.log(url);
```

### Framework Integration

#### React/Next.js
```jsx
import { generateGitHubUrlDirect } from '@thinkeloquent/git-identify-esm';

function FileLink({ path }) {
  const [url, setUrl] = useState(null);

  useEffect(() => {
    generateGitHubUrlDirect(path)
      .then(setUrl)
      .catch(() => setUrl(null));
  }, [path]);

  return url ? <a href={url}>View on GitHub</a> : null;
}
```

#### Vue.js
```vue
<script setup>
import { ref, onMounted } from 'vue';
import { generateGitHubUrlDirect } from '@thinkeloquent/git-identify-esm';

const props = defineProps(['path']);
const githubUrl = ref(null);

onMounted(async () => {
  try {
    githubUrl.value = await generateGitHubUrlDirect(props.path);
  } catch (error) {
    console.error('Failed to get GitHub URL:', error);
  }
});
</script>
```

### CLI Tool Creation

```javascript
#!/usr/bin/env node
import { program } from 'commander';
import { GitFileId } from '@thinkeloquent/git-identify-esm';

program
  .name('git-url')
  .description('Generate GitHub URLs for files')
  .argument('<file>', 'file path to generate URL for')
  .action(async (file) => {
    try {
      const git = new GitFileId();
      await git.findRepository(process.cwd());
      const url = await git.generateGitHubUrl(file);
      console.log(url);
    } catch (error) {
      console.error(error.message);
      process.exit(1);
    }
  });

program.parse();
```

## Performance Considerations

- Repository paths are cached after initialization
- Batch operations use `Promise.allSettled` for parallel processing
- WASM provides native performance for Git operations

## Error Handling Best Practices

1. Always initialize the repository before operations
2. Handle specific error types for better user feedback
3. Use batch operations for multiple files
4. Validate inputs before operations

## TypeScript Support

Full TypeScript definitions are included. Import types:

```typescript
import type { GitFileId, GitCommit, GitBlob } from '@thinkeloquent/git-identify-esm';
```

## 🐛 Troubleshooting

### Common Issues

1. **Error: Cannot find module 'simple-git'**
   - Solution: Run `npm install` in the esm directory

2. **Error: Not in a git repository**
   - Solution: Ensure you're running the code from within a Git repository

3. **Error: No remote configured**
   - Solution: Add a GitHub remote: `git remote add origin git@github.com:user/repo.git`

4. **WASM loading errors**
   - Solution: Ensure your Node.js version supports WASM (>= 14.0.0)

5. **TypeScript errors**
   - Solution: Install types: `npm install --save-dev @types/node`

## 📄 License

MIT

## 🤝 Contributing

Contributions are welcome! Please submit issues and pull requests on GitHub.

1. Fork the repository
2. Create your feature branch
3. Write tests for new features
4. Ensure all tests pass: `npm test`
5. Run linting: `npm run lint`
6. Submit a pull request

## 📚 See Also

- [Main package documentation](../README.md)
- [Rust implementation](../rust/README.md)
- [Python implementation](../py/README.md)
- [API specification](../spec/spec-0.0.1.md)