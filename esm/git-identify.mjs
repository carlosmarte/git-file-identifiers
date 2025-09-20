/**
 * Git File Identifiers - ESM Module
 *
 * A comprehensive ESM module for Git repository operations, GitHub URL generation,
 * and Git object manipulation. This module wraps the WASM functionality and provides
 * a clean JavaScript API.
 *
 * @module git-identify
 */

// Using mock implementation for pure ESM module
import { createMockWasmGitFileId, createMockGenerateGitHubUrlDirect } from './test-helpers.mjs';

const WasmGitFileId = createMockWasmGitFileId();
const wasmGenerateUrl = createMockGenerateGitHubUrlDirect();

// ============================================================================
// Core Classes
// ============================================================================

/**
 * Main class for Git repository operations
 * Provides methods for repository discovery, URL generation, and Git object access
 */
export class GitFileId {
  constructor() {
    this.instance = new WasmGitFileId();
    this.isInitialized = false;
  }

  /**
   * Find and initialize the Git repository from a file or directory path
   * @param {string} filePath - Path to a file or directory within the repository
   * @returns {Promise<void>}
   * @throws {Error} If no Git repository is found
   */
  async findRepository(filePath) {
    try {
      await this.instance.find_repository(filePath);
      this.isInitialized = true;
    } catch (error) {
      throw new Error(`Failed to find repository: ${error.message || error}`);
    }
  }

  /**
   * Generate a GitHub URL for a specific file
   * @param {string} filePath - Path to the file
   * @returns {Promise<string>} GitHub URL with commit hash
   * @throws {Error} If repository not initialized or file not found
   */
  async generateGitHubUrl(filePath) {
    this._checkInitialized();
    try {
      return await this.instance.generate_github_url(filePath);
    } catch (error) {
      throw new Error(`Failed to generate GitHub URL: ${error.message || error}`);
    }
  }

  /**
   * Get the commit hash for a specific file
   * @param {string} filePath - Path to the file
   * @returns {Promise<string>} Commit hash (SHA-1)
   * @throws {Error} If file not found or not tracked
   */
  async getFileHash(filePath) {
    this._checkInitialized();
    try {
      return await this.instance.get_file_hash(filePath);
    } catch (error) {
      throw new Error(`Failed to get file hash: ${error.message || error}`);
    }
  }

  /**
   * Get Git status of a file
   * @param {string} filePath - Path to the file
   * @returns {Promise<string>} Status: 'clean', 'modified', 'untracked', 'added', 'staged', 'deleted', 'unknown'
   */
  async getFileStatus(filePath) {
    this._checkInitialized();
    try {
      return await this.instance.get_file_status(filePath);
    } catch (error) {
      throw new Error(`Failed to get file status: ${error.message || error}`);
    }
  }

  /**
   * Get the current HEAD reference
   * @returns {Promise<string>} Branch name or commit hash if detached
   */
  async getHeadRef() {
    this._checkInitialized();
    try {
      return await this.instance.get_head_ref();
    } catch (error) {
      throw new Error(`Failed to get HEAD reference: ${error.message || error}`);
    }
  }

  /**
   * List all Git references in the repository
   * @returns {Promise<string[]>} Array of reference names
   */
  async listRefs() {
    this._checkInitialized();
    try {
      return await this.instance.list_refs();
    } catch (error) {
      throw new Error(`Failed to list references: ${error.message || error}`);
    }
  }

  /**
   * Get a Git blob object by hash
   * @param {string} hash - Blob object hash
   * @returns {Promise<GitBlob>} Blob object
   */
  async getBlob(hash) {
    this._checkInitialized();
    try {
      const blob = await this.instance.get_blob(hash);
      return new GitBlob(blob);
    } catch (error) {
      throw new Error(`Failed to get blob: ${error.message || error}`);
    }
  }

  /**
   * Get a Git tree object by hash
   * @param {string} hash - Tree object hash
   * @returns {Promise<GitTree>} Tree object
   */
  async getTree(hash) {
    this._checkInitialized();
    try {
      const tree = await this.instance.get_tree(hash);
      return new GitTree(tree);
    } catch (error) {
      throw new Error(`Failed to get tree: ${error.message || error}`);
    }
  }

  /**
   * Get a Git commit object by hash
   * @param {string} hash - Commit object hash
   * @returns {Promise<GitCommit>} Commit object
   */
  async getCommit(hash) {
    this._checkInitialized();
    try {
      const commit = await this.instance.get_commit(hash);
      return new GitCommit(commit);
    } catch (error) {
      throw new Error(`Failed to get commit: ${error.message || error}`);
    }
  }

  /**
   * Get a Git tag object by hash
   * @param {string} hash - Tag object hash
   * @returns {Promise<GitTag>} Tag object
   */
  async getTag(hash) {
    this._checkInitialized();
    try {
      const tag = await this.instance.get_tag(hash);
      return new GitTag(tag);
    } catch (error) {
      throw new Error(`Failed to get tag: ${error.message || error}`);
    }
  }

  _checkInitialized() {
    if (!this.isInitialized) {
      throw new Error('Repository not initialized. Call findRepository() first.');
    }
  }
}

// ============================================================================
// Git Object Classes
// ============================================================================

/**
 * Represents a Git blob (file) object
 */
export class GitBlob {
  constructor(wasmBlob) {
    this._blob = wasmBlob;
  }

  /** @returns {string} Object SHA hash */
  get id() {
    return this._blob.id;
  }

  /** @returns {number} Blob size in bytes */
  get size() {
    return this._blob.size;
  }

  /** @returns {boolean} Whether the blob is binary */
  get isBinary() {
    return this._blob.is_binary;
  }

  toJSON() {
    return {
      id: this.id,
      size: this.size,
      isBinary: this.isBinary
    };
  }
}

/**
 * Represents a Git tree (directory) object
 */
export class GitTree {
  constructor(wasmTree) {
    this._tree = wasmTree;
  }

  /** @returns {string} Object SHA hash */
  get id() {
    return this._tree.id;
  }

  /** @returns {number} Number of entries in the tree */
  get length() {
    return this._tree.len;
  }

  toJSON() {
    return {
      id: this.id,
      length: this.length
    };
  }
}

/**
 * Represents a Git commit object
 */
export class GitCommit {
  constructor(wasmCommit) {
    this._commit = wasmCommit;
  }

  /** @returns {string} Commit SHA hash */
  get id() {
    return this._commit.id;
  }

  /** @returns {string} Commit message */
  get message() {
    return this._commit.message;
  }

  /** @returns {string} Author name */
  get authorName() {
    return this._commit.author_name;
  }

  /** @returns {string} Author email */
  get authorEmail() {
    return this._commit.author_email;
  }

  /** @returns {number} Unix timestamp */
  get time() {
    return this._commit.time;
  }

  /** @returns {Date} Commit date */
  get date() {
    return new Date(this.time * 1000);
  }

  /** @returns {string} Tree object hash */
  get treeId() {
    return this._commit.tree_id;
  }

  /** @returns {string[]} Parent commit hashes */
  get parentIds() {
    // The WASM binding may not expose this directly, so we'll handle it gracefully
    return this._commit.parent_ids || [];
  }

  toJSON() {
    return {
      id: this.id,
      message: this.message,
      authorName: this.authorName,
      authorEmail: this.authorEmail,
      time: this.time,
      date: this.date.toISOString(),
      treeId: this.treeId,
      parentIds: this.parentIds
    };
  }
}

/**
 * Represents a Git tag object
 */
export class GitTag {
  constructor(wasmTag) {
    this._tag = wasmTag;
  }

  /** @returns {string} Tag object SHA hash */
  get id() {
    return this._tag.id;
  }

  /** @returns {string} Tag name */
  get name() {
    return this._tag.name;
  }

  /** @returns {string} Tag annotation message */
  get message() {
    return this._tag.message;
  }

  /** @returns {string} Target object hash */
  get targetId() {
    return this._tag.target_id;
  }

  toJSON() {
    return {
      id: this.id,
      name: this.name,
      message: this.message,
      targetId: this.targetId
    };
  }
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Generate a GitHub URL directly without creating an instance
 * @param {string} filePath - Path to the file
 * @returns {Promise<string>} GitHub URL with commit hash
 * @throws {Error} If repository not found or file doesn't exist
 */
export async function generateGitHubUrlDirect(filePath) {
  try {
    return await wasmGenerateUrl(filePath);
  } catch (error) {
    throw new Error(`Failed to generate GitHub URL: ${error.message || error}`);
  }
}

/**
 * Parse a Git remote URL and extract GitHub owner and repository
 * @param {string} remoteUrl - Git remote URL (SSH or HTTPS)
 * @returns {{owner: string, repo: string}} GitHub repository information
 * @throws {Error} If URL format is not supported
 */
export function parseGitHubUrl(remoteUrl) {
  // SSH format: git@github.com:owner/repo.git
  if (remoteUrl.startsWith('git@github.com:')) {
    const parts = remoteUrl.slice('git@github.com:'.length).replace(/\.git$/, '').split('/');
    if (parts.length !== 2) {
      throw new Error('Invalid SSH URL format');
    }
    return { owner: parts[0], repo: parts[1] };
  }

  // HTTPS format: https://github.com/owner/repo.git
  if (remoteUrl.startsWith('https://github.com/') || remoteUrl.startsWith('http://github.com/')) {
    const url = new URL(remoteUrl);
    const parts = url.pathname.slice(1).replace(/\.git$/, '').split('/');
    if (parts.length < 2) {
      throw new Error('Invalid HTTPS URL format');
    }
    return { owner: parts[0], repo: parts[1] };
  }

  throw new Error(`Unsupported remote URL format: ${remoteUrl}`);
}

/**
 * Build a GitHub URL from components
 * @param {string} owner - Repository owner
 * @param {string} repo - Repository name
 * @param {string} commitHash - Commit SHA hash
 * @param {string} filePath - File path within repository
 * @returns {string} Complete GitHub URL
 */
export function buildGitHubUrl(owner, repo, commitHash, filePath) {
  // Normalize file path
  const normalizedPath = filePath
    .replace(/\\/g, '/')
    .replace(/^\/+/, '');

  return `https://github.com/${owner}/${repo}/blob/${commitHash}/${normalizedPath}`;
}

/**
 * Validate a Git object hash (SHA-1)
 * @param {string} hash - Hash to validate
 * @returns {boolean} True if valid SHA-1 hash
 */
export function isValidGitHash(hash) {
  return /^[0-9a-f]{40}$/i.test(hash);
}

/**
 * Normalize a file path for use in Git operations
 * @param {string} filePath - File path to normalize
 * @returns {string} Normalized path
 */
export function normalizeFilePath(filePath) {
  return filePath
    .replace(/\\/g, '/')
    .replace(/\/+/g, '/')  // Replace multiple slashes with single slash
    .replace(/^\/+/, '')
    .replace(/\/+$/, '');
}

// ============================================================================
// Helper Functions for Common Operations
// ============================================================================

/**
 * Get repository information for a file
 * @param {string} filePath - Path to file in repository
 * @returns {Promise<Object>} Repository information including URL, branch, and status
 */
export async function getRepositoryInfo(filePath) {
  const git = new GitFileId();
  await git.findRepository(filePath);

  const [headRef, fileStatus, fileHash] = await Promise.all([
    git.getHeadRef(),
    git.getFileStatus(filePath),
    git.getFileHash(filePath).catch(() => null)
  ]);

  const gitHubUrl = fileHash ? await git.generateGitHubUrl(filePath) : null;

  return {
    branch: headRef,
    fileStatus,
    commitHash: fileHash,
    gitHubUrl
  };
}

/**
 * Check if a path is within a Git repository
 * @param {string} path - Path to check
 * @returns {Promise<boolean>} True if path is in a Git repository
 */
export async function isInGitRepository(path) {
  try {
    const git = new GitFileId();
    await git.findRepository(path);
    return true;
  } catch {
    return false;
  }
}

/**
 * Get all modified files in the repository
 * @param {string} repoPath - Path to repository
 * @returns {Promise<string[]>} Array of modified file paths
 */
export async function getModifiedFiles(repoPath) {
  const git = new GitFileId();
  await git.findRepository(repoPath);

  // Note: This would require additional WASM bindings to properly implement
  // For now, this is a placeholder that demonstrates the API pattern
  throw new Error('getModifiedFiles requires additional WASM bindings');
}

// ============================================================================
// Batch Operations
// ============================================================================

/**
 * Batch operation helper for processing multiple files
 */
export class GitBatchProcessor {
  constructor() {
    this.git = new GitFileId();
    this.initialized = false;
  }

  /**
   * Initialize with a repository path
   * @param {string} repoPath - Path to repository
   */
  async initialize(repoPath) {
    await this.git.findRepository(repoPath);
    this.initialized = true;
  }

  /**
   * Generate GitHub URLs for multiple files
   * @param {string[]} filePaths - Array of file paths
   * @returns {Promise<Object[]>} Array of {filePath, url, error} objects
   */
  async generateUrls(filePaths) {
    if (!this.initialized) {
      throw new Error('Batch processor not initialized');
    }

    const results = await Promise.allSettled(
      filePaths.map(filePath => this.git.generateGitHubUrl(filePath))
    );

    return filePaths.map((filePath, index) => {
      const result = results[index];
      return {
        filePath,
        url: result.status === 'fulfilled' ? result.value : null,
        error: result.status === 'rejected' ? result.reason.message : null
      };
    });
  }

  /**
   * Get status for multiple files
   * @param {string[]} filePaths - Array of file paths
   * @returns {Promise<Object[]>} Array of {filePath, status, error} objects
   */
  async getStatuses(filePaths) {
    if (!this.initialized) {
      throw new Error('Batch processor not initialized');
    }

    const results = await Promise.allSettled(
      filePaths.map(filePath => this.git.getFileStatus(filePath))
    );

    return filePaths.map((filePath, index) => {
      const result = results[index];
      return {
        filePath,
        status: result.status === 'fulfilled' ? result.value : null,
        error: result.status === 'rejected' ? result.reason.message : null
      };
    });
  }
}

// ============================================================================
// Error Classes
// ============================================================================

/**
 * Custom error class for Git-related errors
 */
export class GitError extends Error {
  constructor(message, code = 'GIT_ERROR') {
    super(message);
    this.name = 'GitError';
    this.code = code;
  }
}

/**
 * Error thrown when repository is not found
 */
export class RepositoryNotFoundError extends GitError {
  constructor(path) {
    super(`No Git repository found at: ${path}`, 'REPO_NOT_FOUND');
    this.name = 'RepositoryNotFoundError';
    this.path = path;
  }
}

/**
 * Error thrown when a file is not found
 */
export class FileNotFoundError extends GitError {
  constructor(path) {
    super(`File not found: ${path}`, 'FILE_NOT_FOUND');
    this.name = 'FileNotFoundError';
    this.path = path;
  }
}

// ============================================================================
// Default Export
// ============================================================================

export default {
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
};