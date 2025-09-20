/**
 * Type definitions for git-identify ESM module
 */

declare module '@thinkeloquent/git-identify-esm' {
  /**
   * Main class for Git repository operations
   */
  export class GitFileId {
    constructor();

    /**
     * Find and initialize the Git repository
     */
    findRepository(filePath: string): Promise<void>;

    /**
     * Generate a GitHub URL for a file
     */
    generateGitHubUrl(filePath: string): Promise<string>;

    /**
     * Get the commit hash for a file
     */
    getFileHash(filePath: string): Promise<string>;

    /**
     * Get Git status of a file
     */
    getFileStatus(filePath: string): Promise<'clean' | 'modified' | 'untracked' | 'added' | 'staged' | 'deleted' | 'unknown'>;

    /**
     * Get the current HEAD reference
     */
    getHeadRef(): Promise<string>;

    /**
     * List all Git references
     */
    listRefs(): Promise<string[]>;

    /**
     * Get a Git blob object
     */
    getBlob(hash: string): Promise<GitBlob>;

    /**
     * Get a Git tree object
     */
    getTree(hash: string): Promise<GitTree>;

    /**
     * Get a Git commit object
     */
    getCommit(hash: string): Promise<GitCommit>;

    /**
     * Get a Git tag object
     */
    getTag(hash: string): Promise<GitTag>;
  }

  /**
   * Git blob (file) object
   */
  export class GitBlob {
    readonly id: string;
    readonly size: number;
    readonly isBinary: boolean;
    toJSON(): {
      id: string;
      size: number;
      isBinary: boolean;
    };
  }

  /**
   * Git tree (directory) object
   */
  export class GitTree {
    readonly id: string;
    readonly length: number;
    toJSON(): {
      id: string;
      length: number;
    };
  }

  /**
   * Git commit object
   */
  export class GitCommit {
    readonly id: string;
    readonly message: string;
    readonly authorName: string;
    readonly authorEmail: string;
    readonly time: number;
    readonly date: Date;
    readonly treeId: string;
    readonly parentIds: string[];
    toJSON(): {
      id: string;
      message: string;
      authorName: string;
      authorEmail: string;
      time: number;
      date: string;
      treeId: string;
      parentIds: string[];
    };
  }

  /**
   * Git tag object
   */
  export class GitTag {
    readonly id: string;
    readonly name: string;
    readonly message: string;
    readonly targetId: string;
    toJSON(): {
      id: string;
      name: string;
      message: string;
      targetId: string;
    };
  }

  /**
   * Batch processor for multiple file operations
   */
  export class GitBatchProcessor {
    constructor();

    /**
     * Initialize with a repository path
     */
    initialize(repoPath: string): Promise<void>;

    /**
     * Generate URLs for multiple files
     */
    generateUrls(filePaths: string[]): Promise<Array<{
      filePath: string;
      url: string | null;
      error: string | null;
    }>>;

    /**
     * Get statuses for multiple files
     */
    getStatuses(filePaths: string[]): Promise<Array<{
      filePath: string;
      status: string | null;
      error: string | null;
    }>>;
  }

  /**
   * Custom error classes
   */
  export class GitError extends Error {
    constructor(message: string, code?: string);
    readonly code: string;
  }

  export class RepositoryNotFoundError extends GitError {
    constructor(path: string);
    readonly path: string;
  }

  export class FileNotFoundError extends GitError {
    constructor(path: string);
    readonly path: string;
  }

  /**
   * Utility functions
   */

  /**
   * Generate GitHub URL directly without creating an instance
   */
  export function generateGitHubUrlDirect(filePath: string): Promise<string>;

  /**
   * Parse a Git remote URL
   */
  export function parseGitHubUrl(remoteUrl: string): {
    owner: string;
    repo: string;
  };

  /**
   * Build a GitHub URL from components
   */
  export function buildGitHubUrl(
    owner: string,
    repo: string,
    commitHash: string,
    filePath: string
  ): string;

  /**
   * Validate a Git object hash
   */
  export function isValidGitHash(hash: string): boolean;

  /**
   * Normalize a file path
   */
  export function normalizeFilePath(filePath: string): string;

  /**
   * Get repository information for a file
   */
  export function getRepositoryInfo(filePath: string): Promise<{
    branch: string;
    fileStatus: string;
    commitHash: string | null;
    gitHubUrl: string | null;
  }>;

  /**
   * Check if a path is within a Git repository
   */
  export function isInGitRepository(path: string): Promise<boolean>;

  /**
   * Default export with all classes and functions
   */
  const gitIdentify: {
    GitFileId: typeof GitFileId;
    GitBlob: typeof GitBlob;
    GitTree: typeof GitTree;
    GitCommit: typeof GitCommit;
    GitTag: typeof GitTag;
    GitBatchProcessor: typeof GitBatchProcessor;
    GitError: typeof GitError;
    RepositoryNotFoundError: typeof RepositoryNotFoundError;
    FileNotFoundError: typeof FileNotFoundError;
    generateGitHubUrlDirect: typeof generateGitHubUrlDirect;
    parseGitHubUrl: typeof parseGitHubUrl;
    buildGitHubUrl: typeof buildGitHubUrl;
    isValidGitHash: typeof isValidGitHash;
    normalizeFilePath: typeof normalizeFilePath;
    getRepositoryInfo: typeof getRepositoryInfo;
    isInGitRepository: typeof isInGitRepository;
  };

  export default gitIdentify;
}