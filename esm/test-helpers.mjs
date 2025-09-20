/**
 * Test helpers and utilities for git-identify tests
 */

/**
 * Create a mock WASM GitFileId instance with custom behavior
 */
export function createMockWasmGitFileId(options = {}) {
  const {
    repoPath = null,
    shouldFailFind = false,
    shouldFailUrl = false,
    customRefs = null,
    customStatus = null
  } = options;

  return class MockWasmGitFileId {
    constructor() {
      this.repoPath = repoPath;
    }

    async find_repository(path) {
      if (shouldFailFind || path.includes('invalid') || path.includes('/definitely/not/a/repo')) {
        throw new Error('No .git directory found');
      }
      this.repoPath = path;
      return Promise.resolve();
    }

    async generate_github_url(path) {
      if (!this.repoPath) {
        throw new Error('Repository not found. Call find_repository first.');
      }
      if (shouldFailUrl || path.includes('nonexistent')) {
        throw new Error('File does not exist');
      }
      return `https://github.com/test/repo/blob/abc123/${path}`;
    }

    async get_file_hash(path) {
      if (!this.repoPath) {
        throw new Error('Repository not found. Call find_repository first.');
      }
      if (path.includes('untracked')) {
        throw new Error('File not tracked');
      }
      return 'a1b2c3d4e5f6789012345678901234567890abcd';
    }

    async get_file_status(path) {
      if (!this.repoPath) {
        throw new Error('Repository not found. Call find_repository first.');
      }

      if (customStatus) {
        return customStatus[path] || 'unknown';
      }

      const statuses = {
        'clean.txt': 'clean',
        'modified.txt': 'modified',
        'untracked.txt': 'untracked',
        'staged.txt': 'staged',
        'added.txt': 'added',
        'deleted.txt': 'deleted'
      };
      return statuses[path] || 'unknown';
    }

    async get_head_ref() {
      if (!this.repoPath) {
        throw new Error('Repository not found. Call find_repository first.');
      }
      return 'main';
    }

    async list_refs() {
      if (!this.repoPath) {
        throw new Error('Repository not found. Call find_repository first.');
      }

      if (customRefs) {
        return customRefs;
      }

      return [
        'refs/heads/main',
        'refs/heads/develop',
        'refs/heads/feature/test',
        'refs/tags/v1.0.0',
        'refs/tags/v2.0.0',
        'refs/remotes/origin/main'
      ];
    }

    async get_blob(hash) {
      if (!this.repoPath) {
        throw new Error('Repository not found. Call find_repository first.');
      }
      if (hash === 'invalid' || !hash) {
        throw new Error('Invalid object hash');
      }
      return {
        id: hash,
        size: 1024,
        is_binary: hash.startsWith('bin')
      };
    }

    async get_tree(hash) {
      if (!this.repoPath) {
        throw new Error('Repository not found. Call find_repository first.');
      }
      if (hash === 'invalid' || !hash) {
        throw new Error('Invalid object hash');
      }
      // Return fixed length for tree456 test case
      if (hash === 'tree456') {
        return {
          id: hash,
          len: 10
        };
      }
      return {
        id: hash,
        len: parseInt(hash.slice(-1), 16) || 10
      };
    }

    async get_commit(hash) {
      if (!this.repoPath) {
        throw new Error('Repository not found. Call find_repository first.');
      }
      if (hash === 'invalid' || !hash) {
        throw new Error('Invalid object hash');
      }
      // Return specific message for commit789 test case
      if (hash === 'commit789') {
        return {
          id: hash,
          message: 'Test commit message',
          author_name: 'Test Author',
          author_email: 'test@example.com',
          time: 1234567890,
          tree_id: `tree_${hash}`,
          parent_ids: hash === 'initial' ? [] : [`parent_${hash}`]
        };
      }
      return {
        id: hash,
        message: `Commit message for ${hash}`,
        author_name: 'Test Author',
        author_email: 'test@example.com',
        time: 1234567890,
        tree_id: `tree_${hash}`,
        parent_ids: hash === 'initial' ? [] : [`parent_${hash}`]
      };
    }

    async get_tag(hash) {
      if (!this.repoPath) {
        throw new Error('Repository not found. Call find_repository first.');
      }
      if (hash === 'invalid' || !hash) {
        throw new Error('Invalid object hash');
      }
      // Return specific values for tag999 test case
      if (hash === 'tag999') {
        return {
          id: hash,
          name: 'v1.0.0',
          message: 'Release version 1.0.0',
          target_id: 'target123'
        };
      }
      return {
        id: hash,
        name: `v${hash.slice(0, 5)}`,
        message: `Tag message for ${hash}`,
        target_id: `target_${hash}`
      };
    }
  };
}

/**
 * Create mock file system structure for testing
 */
export function createMockFileSystem() {
  return {
    '/test/repo/.git': { type: 'directory' },
    '/test/repo/README.md': { type: 'file', content: '# Test Repo' },
    '/test/repo/src/main.js': { type: 'file', content: 'console.log("test");' },
    '/test/repo/src/lib.js': { type: 'file', content: 'export default {};' },
    '/test/repo/package.json': { type: 'file', content: '{"name": "test"}' },
    '/test/no-git/file.txt': { type: 'file', content: 'no git here' }
  };
}

/**
 * Create sample Git objects for testing
 */
export const sampleGitObjects = {
  blob: {
    text: {
      id: 'blob123text',
      size: 1024,
      is_binary: false
    },
    binary: {
      id: 'blob456bin',
      size: 2048,
      is_binary: true
    }
  },

  tree: {
    small: {
      id: 'tree789small',
      len: 5
    },
    large: {
      id: 'tree012large',
      len: 100
    }
  },

  commit: {
    simple: {
      id: 'commit345',
      message: 'Initial commit',
      author_name: 'Jane Doe',
      author_email: 'jane@example.com',
      time: 1609459200,
      tree_id: 'tree789',
      parent_ids: []
    },
    merge: {
      id: 'commit678',
      message: 'Merge branch feature',
      author_name: 'John Smith',
      author_email: 'john@example.com',
      time: 1609545600,
      tree_id: 'tree012',
      parent_ids: ['parent1', 'parent2']
    }
  },

  tag: {
    lightweight: {
      id: 'tag901',
      name: 'v1.0.0',
      message: '',
      target_id: 'commit345'
    },
    annotated: {
      id: 'tag234',
      name: 'v2.0.0',
      message: 'Release version 2.0.0\n\n- New features\n- Bug fixes',
      target_id: 'commit678'
    }
  }
};

/**
 * Helper to create test scenarios
 */
export function createTestScenario(name) {
  const scenarios = {
    'clean-repo': {
      files: ['README.md', 'src/main.js', 'package.json'],
      statuses: {
        'README.md': 'clean',
        'src/main.js': 'clean',
        'package.json': 'clean'
      },
      branch: 'main',
      hasRemote: true
    },

    'dirty-repo': {
      files: ['README.md', 'src/main.js', 'new-file.txt'],
      statuses: {
        'README.md': 'modified',
        'src/main.js': 'staged',
        'new-file.txt': 'untracked'
      },
      branch: 'feature/test',
      hasRemote: true
    },

    'no-remote': {
      files: ['local-file.txt'],
      statuses: {
        'local-file.txt': 'clean'
      },
      branch: 'master',
      hasRemote: false
    },

    'detached-head': {
      files: ['README.md'],
      statuses: {
        'README.md': 'clean'
      },
      branch: 'abc123def456',
      hasRemote: true,
      isDetached: true
    }
  };

  return scenarios[name] || scenarios['clean-repo'];
}

/**
 * Assertion helpers
 */
export const assertHelpers = {
  isValidGitHash(hash) {
    return /^[0-9a-f]{40}$/i.test(hash);
  },

  isValidGitHubUrl(url) {
    const pattern = /^https:\/\/github\.com\/[\w-]+\/[\w-]+\/blob\/[0-9a-f]{6,40}\/.+$/;
    return pattern.test(url);
  },

  isValidRef(ref) {
    return ref.startsWith('refs/') || ref === 'HEAD';
  },

  isValidStatus(status) {
    const validStatuses = ['clean', 'modified', 'untracked', 'added', 'staged', 'deleted', 'unknown'];
    return validStatuses.includes(status);
  }
};

/**
 * Wait helper for async tests
 */
export function wait(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Create a mock console for testing logging
 */
export function createMockConsole() {
  return {
    logs: [],
    errors: [],
    warns: [],

    log(...args) {
      this.logs.push(args.join(' '));
    },

    error(...args) {
      this.errors.push(args.join(' '));
    },

    warn(...args) {
      this.warns.push(args.join(' '));
    },

    clear() {
      this.logs = [];
      this.errors = [];
      this.warns = [];
    }
  };
}

/**
 * Test data generators
 */
export const generators = {
  /**
   * Generate a random Git hash
   */
  randomHash() {
    const chars = '0123456789abcdef';
    let hash = '';
    for (let i = 0; i < 40; i++) {
      hash += chars[Math.floor(Math.random() * chars.length)];
    }
    return hash;
  },

  /**
   * Generate file paths
   */
  filePaths(count = 5) {
    const paths = [];
    const dirs = ['src', 'lib', 'test', 'docs', ''];
    const names = ['index', 'main', 'utils', 'config', 'helper'];
    const exts = ['.js', '.mjs', '.ts', '.json', '.md'];

    for (let i = 0; i < count; i++) {
      const dir = dirs[Math.floor(Math.random() * dirs.length)];
      const name = names[Math.floor(Math.random() * names.length)];
      const ext = exts[Math.floor(Math.random() * exts.length)];
      const path = dir ? `${dir}/${name}${ext}` : `${name}${ext}`;
      paths.push(path);
    }

    return paths;
  },

  /**
   * Generate commit data
   */
  commit(overrides = {}) {
    return {
      id: this.randomHash(),
      message: 'Test commit message',
      author_name: 'Test Author',
      author_email: 'test@example.com',
      time: Date.now() / 1000,
      tree_id: this.randomHash(),
      parent_ids: [],
      ...overrides
    };
  }
};

/**
 * Performance testing helper
 */
export class PerformanceTimer {
  constructor(name) {
    this.name = name;
    this.times = [];
  }

  start() {
    this.startTime = process.hrtime.bigint();
  }

  end() {
    const endTime = process.hrtime.bigint();
    const duration = Number(endTime - this.startTime) / 1000000; // Convert to ms
    this.times.push(duration);
    return duration;
  }

  average() {
    if (this.times.length === 0) return 0;
    return this.times.reduce((a, b) => a + b, 0) / this.times.length;
  }

  report() {
    console.log(`Performance: ${this.name}`);
    console.log(`  Runs: ${this.times.length}`);
    console.log(`  Average: ${this.average().toFixed(2)}ms`);
    console.log(`  Min: ${Math.min(...this.times).toFixed(2)}ms`);
    console.log(`  Max: ${Math.max(...this.times).toFixed(2)}ms`);
  }
}

/**
 * Create a mock generate_github_url_direct function
 */
export function createMockGenerateGitHubUrlDirect() {
  return async function(filePath) {
    // Parse the path to extract parts for URL generation
    // For test mode, return a fixed URL format
    if (filePath === '/invalid/file') {
      throw new Error('File does not exist');
    }
    // Keep the full path, just remove leading slashes
    const cleanPath = filePath.replace(/^\/+/, '');
    return `https://github.com/test/repo/blob/def456/${cleanPath}`;
  };
}