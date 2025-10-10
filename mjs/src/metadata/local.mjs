import path from 'path';
import { executeGitCommand, getRepositoryRoot } from '../utils/git.mjs';
import { normalizeFilePath, resolveFilePath } from '../utils/path.mjs';
import { parseGitHubUrl, buildGitHubUrl } from '../utils/url.mjs';
import { FileNotFoundError } from '../errors.mjs';

/**
 * Retrieves file metadata from a local Git repository
 * @param {string} repoPath - Absolute path to repository (or any directory within it)
 * @param {string} filePath - File path (absolute or relative to repo root)
 * @returns {Promise<object>} Normalized metadata object
 */
export async function getLocalMetadata(repoPath, filePath) {
  if (!repoPath || !filePath) {
    throw new TypeError('repoPath and filePath are required');
  }

  // Get repository root
  const repoRoot = await getRepositoryRoot(repoPath);

  // Resolve file path relative to repo root
  const relativePath = resolveFilePath(repoRoot, filePath);
  const absoluteFilePath = path.join(repoRoot, relativePath);

  try {
    // Get last commit hash for this file
    // git log -1 --pretty=format:%H -- <file>
    const commitHash = await executeGitCommand(
      `git log -1 --pretty=format:%H -- "${relativePath}"`,
      repoRoot
    );

    if (!commitHash) {
      throw new FileNotFoundError(
        `File "${relativePath}" has no Git history (not tracked or never committed)`,
        {
          context: { repoPath: repoRoot, filePath: relativePath }
        }
      );
    }

    // Get commit timestamp
    // git log -1 --pretty=format:%cI -- <file>
    const lastModified = await executeGitCommand(
      `git log -1 --pretty=format:%cI -- "${relativePath}"`,
      repoRoot
    );

    // Get current branch
    // git rev-parse --abbrev-ref HEAD
    let branch;
    try {
      branch = await executeGitCommand('git rev-parse --abbrev-ref HEAD', repoRoot);
    } catch {
      // Fallback for detached HEAD
      branch = 'HEAD';
    }

    // Get file blob hash
    // git ls-tree HEAD <file>
    const lsTreeOutput = await executeGitCommand(
      `git ls-tree HEAD "${relativePath}"`,
      repoRoot
    );

    if (!lsTreeOutput) {
      throw new FileNotFoundError(
        `File "${relativePath}" not found in current commit`,
        {
          context: { repoPath: repoRoot, filePath: relativePath }
        }
      );
    }

    // Parse ls-tree output: "100644 blob <hash>\t<path>"
    const match = lsTreeOutput.match(/^\d+ blob ([0-9a-f]{40})\t/);
    if (!match) {
      throw new Error(`Failed to parse git ls-tree output: ${lsTreeOutput}`);
    }
    const fileHash = match[1];

    // Get remote URL (optional)
    let remoteUrl = null;
    try {
      remoteUrl = await executeGitCommand('git config --get remote.origin.url', repoRoot);
    } catch {
      // No remote configured - that's OK
    }

    // Parse owner/repo from remote URL
    let owner = null;
    let repo = null;
    let htmlUrl = null;

    if (remoteUrl) {
      const parsed = parseGitHubUrl(remoteUrl);
      if (parsed) {
        owner = parsed.owner;
        repo = parsed.repo;

        // Only build GitHub URL if it's actually a GitHub remote
        if (!parsed.host || parsed.host === 'github') {
          htmlUrl = buildGitHubUrl(owner, repo, commitHash, relativePath);
        }
      }
    }

    // If we couldn't parse owner/repo from remote, use placeholder
    if (!owner || !repo) {
      owner = 'local';
      repo = path.basename(repoRoot);
    }

    // Return normalized metadata
    const metadata = {
      source: 'local-git',
      owner,
      repo,
      repoPath: repoRoot,
      branch,
      filePath: relativePath,
      commitHash,
      fileHash,
      lastModified
    };

    if (htmlUrl) {
      metadata.htmlUrl = htmlUrl;
    }

    return metadata;
  } catch (error) {
    // Re-throw known errors
    if (error instanceof FileNotFoundError) {
      throw error;
    }

    // Wrap unknown errors
    throw new Error(
      `Failed to retrieve local Git metadata for ${relativePath}: ${error.message}`,
      { cause: error }
    );
  }
}

/**
 * Checks if a file exists in a Git repository
 * @param {string} repoPath - Repository path
 * @param {string} filePath - File path
 * @returns {Promise<boolean>} True if file is tracked in Git
 */
export async function isFileInGit(repoPath, filePath) {
  try {
    await getLocalMetadata(repoPath, filePath);
    return true;
  } catch {
    return false;
  }
}
