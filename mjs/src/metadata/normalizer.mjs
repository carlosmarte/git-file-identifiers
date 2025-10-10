import { normalizeFilePath } from '../utils/path.mjs';
import { validateGitHash } from '../utils/hash.mjs';

/**
 * Normalizes metadata from different sources into a consistent format
 * @param {object} rawMeta - Raw metadata from GitHub API or local Git
 * @returns {object} Normalized metadata with consistent schema
 */
export function normalizeMetadata(rawMeta) {
  if (!rawMeta || typeof rawMeta !== 'object') {
    throw new TypeError('Metadata must be an object');
  }

  // Validate required fields
  const requiredFields = ['source', 'owner', 'repo', 'branch', 'commitHash', 'filePath', 'fileHash'];
  for (const field of requiredFields) {
    if (!rawMeta[field]) {
      throw new Error(`Missing required field: ${field}`);
    }
  }

  // Validate hash formats
  validateGitHash(rawMeta.commitHash, 'commitHash');
  validateGitHash(rawMeta.fileHash, 'fileHash');

  // Normalize file path to POSIX format
  const normalizedPath = normalizeFilePath(rawMeta.filePath);

  // Normalize timestamp to ISO 8601 UTC
  let lastModified = rawMeta.lastModified;
  if (lastModified) {
    const date = new Date(lastModified);
    if (isNaN(date.getTime())) {
      throw new Error(`Invalid timestamp: ${lastModified}`);
    }
    lastModified = date.toISOString();
  }

  // Build normalized metadata object
  // Fields are intentionally ordered alphabetically for deterministic serialization
  const normalized = {
    branch: rawMeta.branch,
    commitHash: rawMeta.commitHash.toLowerCase(), // Normalize to lowercase
    fileHash: rawMeta.fileHash.toLowerCase(),     // Normalize to lowercase
    filePath: normalizedPath,
    lastModified: lastModified,
    owner: rawMeta.owner,
    repo: rawMeta.repo,
    source: rawMeta.source
  };

  // Add optional fields if present
  if (rawMeta.htmlUrl) {
    normalized.htmlUrl = rawMeta.htmlUrl;
  }

  if (rawMeta.repoPath) {
    normalized.repoPath = rawMeta.repoPath;
  }

  // Remove null/undefined values
  Object.keys(normalized).forEach(key => {
    if (normalized[key] === null || normalized[key] === undefined) {
      delete normalized[key];
    }
  });

  return normalized;
}

/**
 * Sorts object keys alphabetically for canonical JSON serialization
 * @param {object} obj - Object to sort
 * @returns {object} New object with sorted keys
 */
export function sortObjectKeys(obj) {
  if (obj === null || typeof obj !== 'object' || Array.isArray(obj)) {
    return obj;
  }

  const sorted = {};
  const keys = Object.keys(obj).sort();

  for (const key of keys) {
    const value = obj[key];
    sorted[key] = typeof value === 'object' && value !== null && !Array.isArray(value)
      ? sortObjectKeys(value)
      : value;
  }

  return sorted;
}

/**
 * Creates canonical JSON representation for hashing
 * @param {object} metadata - Metadata object
 * @returns {string} Canonical JSON string (no whitespace, sorted keys)
 */
export function canonicalizeMetadata(metadata) {
  const sorted = sortObjectKeys(metadata);
  return JSON.stringify(sorted);
}
