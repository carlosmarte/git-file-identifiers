import path from 'path';

/**
 * Normalizes a file path to POSIX format (forward slashes)
 * Ensures cross-platform consistency
 * @param {string} filePath - The file path to normalize
 * @returns {string} Normalized POSIX path
 */
export function normalizeFilePath(filePath) {
  if (typeof filePath !== 'string') {
    throw new TypeError(`Expected string, got ${typeof filePath}`);
  }

  // Convert to POSIX format (forward slashes)
  // Handle both Windows (backslash) and Unix (forward slash) paths
  let normalized = filePath.replace(/\\/g, '/');

  // Remove leading './' if present
  normalized = normalized.replace(/^\.\//, '');

  // Remove trailing slashes
  normalized = normalized.replace(/\/+$/, '');

  // Normalize multiple slashes to single slash
  normalized = normalized.replace(/\/+/g, '/');

  return normalized;
}

/**
 * Resolves a file path relative to a repository root
 * @param {string} repoPath - Absolute path to repository root
 * @param {string} filePath - File path (absolute or relative)
 * @returns {string} Normalized relative path from repo root
 */
export function resolveFilePath(repoPath, filePath) {
  const absoluteRepoPath = path.resolve(repoPath);
  const absoluteFilePath = path.isAbsolute(filePath)
    ? filePath
    : path.resolve(repoPath, filePath);

  const relativePath = path.relative(absoluteRepoPath, absoluteFilePath);

  return normalizeFilePath(relativePath);
}
