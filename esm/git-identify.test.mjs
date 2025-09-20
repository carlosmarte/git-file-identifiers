/**
 * Unit tests for git-identify.mjs
 *
 * Run with: node --experimental-vm-modules esm/git-identify.test.mjs
 * Or with Jest: npm test (from esm directory)
 */

import { describe, it, expect, beforeEach, afterEach, jest } from '@jest/globals';
import {
  GitFileId,
  GitBlob,
  GitTree,
  GitCommit,
  GitTag,
  GitBatchProcessor,
  GitError,
  RepositoryNotFoundError,
  FileNotFoundError,
  generateGitHubUrlDirect,
  parseGitHubUrl,
  buildGitHubUrl,
  isValidGitHash,
  normalizeFilePath,
  getRepositoryInfo,
  isInGitRepository
} from './git-identify.mjs';


// ============================================================================
// GitFileId Class Tests
// ============================================================================

describe('GitFileId', () => {
  let git;

  beforeEach(() => {
    git = new GitFileId();
  });

  describe('constructor', () => {
    it('should create a new instance', () => {
      expect(git).toBeInstanceOf(GitFileId);
      expect(git.isInitialized).toBe(false);
    });
  });

  describe('findRepository', () => {
    it('should initialize repository successfully', async () => {
      await git.findRepository('./test');
      expect(git.isInitialized).toBe(true);
    });

    it('should throw error for invalid path', async () => {
      await expect(git.findRepository('/invalid/path')).rejects.toThrow('Failed to find repository');
    });
  });

  describe('generateGitHubUrl', () => {
    it('should generate URL for valid file', async () => {
      await git.findRepository('./test');
      const url = await git.generateGitHubUrl('README.md');
      expect(url).toBe('https://github.com/test/repo/blob/abc123/README.md');
    });

    it('should throw error if not initialized', async () => {
      await expect(git.generateGitHubUrl('README.md')).rejects.toThrow('Repository not initialized');
    });

    it('should throw error for nonexistent file', async () => {
      await git.findRepository('./test');
      await expect(git.generateGitHubUrl('nonexistent.txt')).rejects.toThrow('Failed to generate GitHub URL');
    });
  });

  describe('getFileHash', () => {
    it('should return hash for tracked file', async () => {
      await git.findRepository('./test');
      const hash = await git.getFileHash('README.md');
      expect(hash).toBe('a1b2c3d4e5f6789012345678901234567890abcd');
      expect(hash).toHaveLength(40);
    });

    it('should throw error for untracked file', async () => {
      await git.findRepository('./test');
      await expect(git.getFileHash('untracked.txt')).rejects.toThrow('Failed to get file hash');
    });
  });

  describe('getFileStatus', () => {
    it('should return correct status for files', async () => {
      await git.findRepository('./test');

      expect(await git.getFileStatus('clean.txt')).toBe('clean');
      expect(await git.getFileStatus('modified.txt')).toBe('modified');
      expect(await git.getFileStatus('untracked.txt')).toBe('untracked');
      expect(await git.getFileStatus('staged.txt')).toBe('staged');
      expect(await git.getFileStatus('unknown.txt')).toBe('unknown');
    });
  });

  describe('getHeadRef', () => {
    it('should return current branch', async () => {
      await git.findRepository('./test');
      const head = await git.getHeadRef();
      expect(head).toBe('main');
    });
  });

  describe('listRefs', () => {
    it('should return array of references', async () => {
      await git.findRepository('./test');
      const refs = await git.listRefs();
      expect(Array.isArray(refs)).toBe(true);
      expect(refs).toContain('refs/heads/main');
      expect(refs).toContain('refs/tags/v1.0.0');
    });
  });

  describe('Git object methods', () => {
    beforeEach(async () => {
      await git.findRepository('./test');
    });

    it('should get blob object', async () => {
      const blob = await git.getBlob('abc123');
      expect(blob).toBeInstanceOf(GitBlob);
      expect(blob.id).toBe('abc123');
      expect(blob.size).toBe(1024);
      expect(blob.isBinary).toBe(false);
    });

    it('should get tree object', async () => {
      const tree = await git.getTree('tree456');
      expect(tree).toBeInstanceOf(GitTree);
      expect(tree.id).toBe('tree456');
      expect(tree.length).toBe(10);
    });

    it('should get commit object', async () => {
      const commit = await git.getCommit('commit789');
      expect(commit).toBeInstanceOf(GitCommit);
      expect(commit.id).toBe('commit789');
      expect(commit.message).toBe('Test commit message');
      expect(commit.authorName).toBe('Test Author');
      expect(commit.authorEmail).toBe('test@example.com');
      expect(commit.date).toBeInstanceOf(Date);
    });

    it('should get tag object', async () => {
      const tag = await git.getTag('tag999');
      expect(tag).toBeInstanceOf(GitTag);
      expect(tag.id).toBe('tag999');
      expect(tag.name).toBe('v1.0.0');
      expect(tag.message).toBe('Release version 1.0.0');
      expect(tag.targetId).toBe('target123');
    });

    it('should throw error for invalid hash', async () => {
      await expect(git.getBlob('invalid')).rejects.toThrow('Failed to get blob');
      await expect(git.getTree('invalid')).rejects.toThrow('Failed to get tree');
      await expect(git.getCommit('invalid')).rejects.toThrow('Failed to get commit');
      await expect(git.getTag('invalid')).rejects.toThrow('Failed to get tag');
    });
  });
});

// ============================================================================
// Git Object Classes Tests
// ============================================================================

describe('Git Object Classes', () => {
  describe('GitBlob', () => {
    it('should create blob with correct properties', () => {
      const wasmBlob = { id: 'blob123', size: 2048, is_binary: true };
      const blob = new GitBlob(wasmBlob);

      expect(blob.id).toBe('blob123');
      expect(blob.size).toBe(2048);
      expect(blob.isBinary).toBe(true);
    });

    it('should serialize to JSON correctly', () => {
      const wasmBlob = { id: 'blob123', size: 2048, is_binary: false };
      const blob = new GitBlob(wasmBlob);
      const json = blob.toJSON();

      expect(json).toEqual({
        id: 'blob123',
        size: 2048,
        isBinary: false
      });
    });
  });

  describe('GitTree', () => {
    it('should create tree with correct properties', () => {
      const wasmTree = { id: 'tree456', len: 15 };
      const tree = new GitTree(wasmTree);

      expect(tree.id).toBe('tree456');
      expect(tree.length).toBe(15);
    });

    it('should serialize to JSON correctly', () => {
      const wasmTree = { id: 'tree456', len: 15 };
      const tree = new GitTree(wasmTree);
      const json = tree.toJSON();

      expect(json).toEqual({
        id: 'tree456',
        length: 15
      });
    });
  });

  describe('GitCommit', () => {
    it('should create commit with correct properties', () => {
      const wasmCommit = {
        id: 'commit789',
        message: 'Test commit',
        author_name: 'Author',
        author_email: 'author@test.com',
        time: 1609459200, // 2021-01-01 00:00:00 UTC
        tree_id: 'tree123',
        parent_ids: ['parent1']
      };
      const commit = new GitCommit(wasmCommit);

      expect(commit.id).toBe('commit789');
      expect(commit.message).toBe('Test commit');
      expect(commit.authorName).toBe('Author');
      expect(commit.authorEmail).toBe('author@test.com');
      expect(commit.time).toBe(1609459200);
      expect(commit.date).toBeInstanceOf(Date);
      expect(commit.date.getTime()).toBe(1609459200000);
      expect(commit.treeId).toBe('tree123');
    });

    it('should serialize to JSON correctly', () => {
      const wasmCommit = {
        id: 'commit789',
        message: 'Test',
        author_name: 'Author',
        author_email: 'test@test.com',
        time: 1609459200,
        tree_id: 'tree123'
      };
      const commit = new GitCommit(wasmCommit);
      const json = commit.toJSON();

      expect(json.id).toBe('commit789');
      expect(json.message).toBe('Test');
      expect(json.date).toMatch(/^\d{4}-\d{2}-\d{2}T/); // ISO date format
    });
  });

  describe('GitTag', () => {
    it('should create tag with correct properties', () => {
      const wasmTag = {
        id: 'tag111',
        name: 'v2.0.0',
        message: 'Version 2.0.0',
        target_id: 'commit999'
      };
      const tag = new GitTag(wasmTag);

      expect(tag.id).toBe('tag111');
      expect(tag.name).toBe('v2.0.0');
      expect(tag.message).toBe('Version 2.0.0');
      expect(tag.targetId).toBe('commit999');
    });

    it('should serialize to JSON correctly', () => {
      const wasmTag = {
        id: 'tag111',
        name: 'v2.0.0',
        message: 'Version 2.0.0',
        target_id: 'commit999'
      };
      const tag = new GitTag(wasmTag);
      const json = tag.toJSON();

      expect(json).toEqual({
        id: 'tag111',
        name: 'v2.0.0',
        message: 'Version 2.0.0',
        targetId: 'commit999'
      });
    });
  });
});

// ============================================================================
// Utility Functions Tests
// ============================================================================

describe('Utility Functions', () => {
  describe('generateGitHubUrlDirect', () => {
    it('should generate URL directly', async () => {
      const url = await generateGitHubUrlDirect('src/main.js');
      expect(url).toBe('https://github.com/test/repo/blob/def456/src/main.js');
    });

    it('should throw error for invalid path', async () => {
      await expect(generateGitHubUrlDirect('/invalid/file')).rejects.toThrow('Failed to generate GitHub URL');
    });
  });

  describe('parseGitHubUrl', () => {
    it('should parse SSH URL', () => {
      const result = parseGitHubUrl('git@github.com:owner/repo.git');
      expect(result).toEqual({ owner: 'owner', repo: 'repo' });
    });

    it('should parse SSH URL without .git', () => {
      const result = parseGitHubUrl('git@github.com:owner/repo');
      expect(result).toEqual({ owner: 'owner', repo: 'repo' });
    });

    it('should parse HTTPS URL', () => {
      const result = parseGitHubUrl('https://github.com/owner/repo.git');
      expect(result).toEqual({ owner: 'owner', repo: 'repo' });
    });

    it('should parse HTTP URL', () => {
      const result = parseGitHubUrl('http://github.com/owner/repo.git');
      expect(result).toEqual({ owner: 'owner', repo: 'repo' });
    });

    it('should throw error for invalid URL format', () => {
      expect(() => parseGitHubUrl('not-a-url')).toThrow('Unsupported remote URL format');
    });

    it('should throw error for invalid SSH format', () => {
      expect(() => parseGitHubUrl('git@github.com:invalid')).toThrow('Invalid SSH URL format');
    });

    it('should throw error for invalid HTTPS format', () => {
      expect(() => parseGitHubUrl('https://github.com/')).toThrow('Invalid HTTPS URL format');
    });
  });

  describe('buildGitHubUrl', () => {
    it('should build correct URL', () => {
      const url = buildGitHubUrl('owner', 'repo', 'abc123', 'src/file.js');
      expect(url).toBe('https://github.com/owner/repo/blob/abc123/src/file.js');
    });

    it('should normalize Windows paths', () => {
      const url = buildGitHubUrl('owner', 'repo', 'abc123', 'src\\windows\\file.js');
      expect(url).toBe('https://github.com/owner/repo/blob/abc123/src/windows/file.js');
    });

    it('should remove leading slashes', () => {
      const url = buildGitHubUrl('owner', 'repo', 'abc123', '/src/file.js');
      expect(url).toBe('https://github.com/owner/repo/blob/abc123/src/file.js');
    });
  });

  describe('isValidGitHash', () => {
    it('should validate correct SHA-1 hash', () => {
      expect(isValidGitHash('a1b2c3d4e5f6789012345678901234567890abcd')).toBe(true);
      expect(isValidGitHash('A1B2C3D4E5F6789012345678901234567890ABCD')).toBe(true);
    });

    it('should reject invalid hashes', () => {
      expect(isValidGitHash('abc123')).toBe(false); // Too short
      expect(isValidGitHash('z1b2c3d4e5f6789012345678901234567890abcd')).toBe(false); // Invalid char
      expect(isValidGitHash('a1b2c3d4e5f6789012345678901234567890abcd0')).toBe(false); // Too long
      expect(isValidGitHash('')).toBe(false);
    });
  });

  describe('normalizeFilePath', () => {
    it('should normalize various path formats', () => {
      expect(normalizeFilePath('/src/file.js')).toBe('src/file.js');
      expect(normalizeFilePath('//src//file.js')).toBe('src/file.js');
      expect(normalizeFilePath('src\\windows\\file.js')).toBe('src/windows/file.js');
      expect(normalizeFilePath('src/file.js/')).toBe('src/file.js');
      expect(normalizeFilePath('/src/file.js/')).toBe('src/file.js');
    });
  });

  describe('getRepositoryInfo', () => {
    it('should return repository information', async () => {
      const info = await getRepositoryInfo('README.md');
      expect(info).toHaveProperty('branch');
      expect(info).toHaveProperty('fileStatus');
      expect(info).toHaveProperty('commitHash');
      expect(info).toHaveProperty('gitHubUrl');
      expect(info.branch).toBe('main');
    });

    it('should handle errors gracefully', async () => {
      await expect(getRepositoryInfo('/invalid/path')).rejects.toThrow();
    });
  });

  describe('isInGitRepository', () => {
    it('should return true for valid repository', async () => {
      const result = await isInGitRepository('./test');
      expect(result).toBe(true);
    });

    it('should return false for invalid path', async () => {
      const result = await isInGitRepository('/invalid/path');
      expect(result).toBe(false);
    });
  });
});

// ============================================================================
// GitBatchProcessor Tests
// ============================================================================

describe('GitBatchProcessor', () => {
  let batch;

  beforeEach(() => {
    batch = new GitBatchProcessor();
  });

  describe('initialization', () => {
    it('should initialize successfully', async () => {
      await batch.initialize('./test');
      expect(batch.initialized).toBe(true);
    });

    it('should throw error if not initialized', async () => {
      await expect(batch.generateUrls(['file.js'])).rejects.toThrow('Batch processor not initialized');
      await expect(batch.getStatuses(['file.js'])).rejects.toThrow('Batch processor not initialized');
    });
  });

  describe('generateUrls', () => {
    beforeEach(async () => {
      await batch.initialize('./test');
    });

    it('should generate URLs for multiple files', async () => {
      const results = await batch.generateUrls(['file1.js', 'file2.js']);
      expect(results).toHaveLength(2);
      expect(results[0]).toEqual({
        filePath: 'file1.js',
        url: 'https://github.com/test/repo/blob/abc123/file1.js',
        error: null
      });
    });

    it('should handle errors for individual files', async () => {
      const results = await batch.generateUrls(['valid.js', 'nonexistent.txt']);
      expect(results).toHaveLength(2);
      expect(results[0].error).toBeNull();
      expect(results[1].error).toContain('File does not exist');
    });
  });

  describe('getStatuses', () => {
    beforeEach(async () => {
      await batch.initialize('./test');
    });

    it('should get statuses for multiple files', async () => {
      const results = await batch.getStatuses(['clean.txt', 'modified.txt']);
      expect(results).toHaveLength(2);
      expect(results[0]).toEqual({
        filePath: 'clean.txt',
        status: 'clean',
        error: null
      });
      expect(results[1]).toEqual({
        filePath: 'modified.txt',
        status: 'modified',
        error: null
      });
    });
  });
});

// ============================================================================
// Error Classes Tests
// ============================================================================

describe('Error Classes', () => {
  describe('GitError', () => {
    it('should create error with message and code', () => {
      const error = new GitError('Test error', 'TEST_CODE');
      expect(error).toBeInstanceOf(Error);
      expect(error.name).toBe('GitError');
      expect(error.message).toBe('Test error');
      expect(error.code).toBe('TEST_CODE');
    });

    it('should use default code', () => {
      const error = new GitError('Test error');
      expect(error.code).toBe('GIT_ERROR');
    });
  });

  describe('RepositoryNotFoundError', () => {
    it('should create error with path', () => {
      const error = new RepositoryNotFoundError('/test/path');
      expect(error).toBeInstanceOf(GitError);
      expect(error.name).toBe('RepositoryNotFoundError');
      expect(error.message).toBe('No Git repository found at: /test/path');
      expect(error.code).toBe('REPO_NOT_FOUND');
      expect(error.path).toBe('/test/path');
    });
  });

  describe('FileNotFoundError', () => {
    it('should create error with path', () => {
      const error = new FileNotFoundError('/test/file.js');
      expect(error).toBeInstanceOf(GitError);
      expect(error.name).toBe('FileNotFoundError');
      expect(error.message).toBe('File not found: /test/file.js');
      expect(error.code).toBe('FILE_NOT_FOUND');
      expect(error.path).toBe('/test/file.js');
    });
  });
});

// ============================================================================
// Integration Tests
// ============================================================================

describe('Integration Tests', () => {
  it('should perform complete workflow', async () => {
    const git = new GitFileId();

    // Initialize repository
    await git.findRepository('./test');

    // Get repository information
    const headRef = await git.getHeadRef();
    const refs = await git.listRefs();

    expect(headRef).toBe('main');
    expect(refs.length).toBeGreaterThan(0);

    // File operations
    const status = await git.getFileStatus('clean.txt');
    expect(status).toBe('clean');

    // Generate URL
    const url = await git.generateGitHubUrl('README.md');
    expect(url).toContain('github.com');
  });

  it('should handle batch operations efficiently', async () => {
    const batch = new GitBatchProcessor();
    await batch.initialize('./test');

    const files = ['file1.js', 'file2.js', 'file3.js'];
    const [urls, statuses] = await Promise.all([
      batch.generateUrls(files),
      batch.getStatuses(files)
    ]);

    expect(urls).toHaveLength(3);
    expect(statuses).toHaveLength(3);
  });
});

// ============================================================================
// Run Tests if executed directly
// ============================================================================

if (import.meta.url === `file://${process.argv[1]}`) {
  console.log('Running git-identify.mjs tests...');
  // Note: In a real scenario, you'd use a test runner like Jest
  // This is just for demonstration
  console.log('Tests should be run with: npm test or jest');
}