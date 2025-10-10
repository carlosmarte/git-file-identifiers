/**
 * Git Identifier Module - Main Entry Point
 *
 * Provides unified API for generating unique, deterministic file identifiers
 * from Git or GitHub metadata for file change detection without reading content.
 *
 * @module git-identify
 * @version 2.0.0
 */

// Metadata extractors
export { getGitHubMetadata } from './metadata/github.mjs';
export { getLocalMetadata, isFileInGit } from './metadata/local.mjs';
export { normalizeMetadata } from './metadata/normalizer.mjs';

// Identifier generation
export { generateIdentifier, generateIdentifiers } from './identifier.mjs';

// Batch processing
export { generateBatchIdentifiers, GitBatchProcessor } from './batch.mjs';

// Change detection helpers
export {
  hasFileChanged,
  compareIdentifier,
  generateChangeReport,
  createManifest,
  loadManifest,
  saveManifest
} from './change-detection.mjs';

// Utility functions
export { normalizeFilePath, resolveFilePath } from './utils/path.mjs';
export { parseGitHubUrl, buildGitHubUrl } from './utils/url.mjs';
export { isValidGitHash, validateGitHash } from './utils/hash.mjs';
export { executeGitCommand, isGitRepository, getRepositoryRoot } from './utils/git.mjs';

// Error classes
export {
  GitError,
  RepositoryNotFoundError,
  FileNotFoundError,
  InvalidHashError,
  RateLimitError,
  AuthenticationError,
  GitCommandError
} from './errors.mjs';

// Helper function for complete repository info
import { getLocalMetadata } from './metadata/local.mjs';
import { generateIdentifier } from './identifier.mjs';
import { getRepositoryRoot } from './utils/git.mjs';

/**
 * Gets complete repository information for a file
 * Convenience function that combines metadata extraction and identifier generation
 * @param {string} filePath - File path (relative or absolute)
 * @param {object} [options={}] - Options
 * @param {string} [options.repoPath=process.cwd()] - Repository path
 * @param {object} [options.identifierOptions] - Options for identifier generation
 * @returns {Promise<object>} Repository info with metadata and identifier
 */
export async function getRepositoryInfo(filePath, options = {}) {
  const {
    repoPath = process.cwd(),
    identifierOptions = {}
  } = options;

  // Get repository root
  const root = await getRepositoryRoot(repoPath);

  // Get metadata
  const metadata = await getLocalMetadata(root, filePath);

  // Generate identifier
  const identifier = generateIdentifier(metadata, identifierOptions);

  return {
    metadata,
    identifier: identifier.identifier,
    short: identifier.short,
    algorithm: identifier.algorithm,
    repository: {
      root,
      owner: metadata.owner,
      repo: metadata.repo,
      branch: metadata.branch
    }
  };
}

/**
 * Checks if a path is in a Git repository
 * @param {string} path - Path to check
 * @returns {Promise<boolean>} True if in Git repository
 */
export async function isInGitRepository(path) {
  const { isGitRepository } = await import('./utils/git.mjs');
  return isGitRepository(path);
}
