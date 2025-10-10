import { normalizeFilePath } from '../utils/path.mjs';
import { buildGitHubUrl } from '../utils/url.mjs';
import {
  FileNotFoundError,
  RepositoryNotFoundError,
  RateLimitError,
  AuthenticationError
} from '../errors.mjs';

/**
 * Gets GitHub API token from environment variable
 * @returns {string | null} GitHub token or null
 */
function getGitHubToken() {
  return process.env.GITHUB_TOKEN || process.env.GH_TOKEN || null;
}

/**
 * Makes a request to GitHub API with authentication and error handling
 * @param {string} url - API endpoint URL
 * @returns {Promise<object>} Response data
 * @throws {Error} Various GitHub API errors
 */
async function githubApiRequest(url) {
  const token = getGitHubToken();
  const headers = {
    'Accept': 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
    'User-Agent': 'git-identify/2.0.0'
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, { headers });

  // Handle rate limiting
  if (response.status === 403) {
    const rateLimitRemaining = response.headers.get('x-ratelimit-remaining');
    if (rateLimitRemaining === '0') {
      const resetTime = response.headers.get('x-ratelimit-reset');
      const resetAt = resetTime ? new Date(parseInt(resetTime) * 1000).toISOString() : null;

      throw new RateLimitError(
        'GitHub API rate limit exceeded',
        {
          resetAt,
          context: { url }
        }
      );
    }
  }

  // Handle authentication errors
  if (response.status === 401) {
    throw new AuthenticationError(
      'GitHub API authentication failed. Please set GITHUB_TOKEN environment variable.',
      {
        context: { url }
      }
    );
  }

  // Handle not found
  if (response.status === 404) {
    const data = await response.json().catch(() => ({}));
    throw new FileNotFoundError(
      data.message || 'Resource not found',
      {
        context: { url }
      }
    );
  }

  // Handle other errors
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(
      `GitHub API request failed: ${response.status} ${response.statusText}${data.message ? ` - ${data.message}` : ''}`,
    );
  }

  return response.json();
}

/**
 * Retrieves file metadata from GitHub API
 * @param {string} owner - Repository owner
 * @param {string} repo - Repository name
 * @param {string} filePath - File path relative to repository root
 * @param {string} [branch='main'] - Branch name
 * @returns {Promise<object>} Normalized metadata object
 */
export async function getGitHubMetadata(owner, repo, filePath, branch = 'main') {
  if (!owner || !repo || !filePath) {
    throw new TypeError('owner, repo, and filePath are required');
  }

  // Normalize file path
  const normalizedPath = normalizeFilePath(filePath);

  try {
    // Get file contents to retrieve file SHA
    // API: GET /repos/:owner/:repo/contents/:path
    const contentsUrl = `https://api.github.com/repos/${owner}/${repo}/contents/${normalizedPath}?ref=${branch}`;
    const contentsData = await githubApiRequest(contentsUrl);

    // Get commit information for this file
    // API: GET /repos/:owner/:repo/commits
    const commitsUrl = `https://api.github.com/repos/${owner}/${repo}/commits?path=${normalizedPath}&sha=${branch}&per_page=1`;
    const commitsData = await githubApiRequest(commitsUrl);

    if (!commitsData || commitsData.length === 0) {
      throw new FileNotFoundError(
        `No commits found for file "${normalizedPath}" on branch "${branch}"`,
        {
          context: { owner, repo, filePath: normalizedPath, branch }
        }
      );
    }

    const latestCommit = commitsData[0];

    // Build GitHub permalink URL
    const htmlUrl = buildGitHubUrl(owner, repo, latestCommit.sha, normalizedPath);

    // Return normalized metadata
    return {
      source: 'github-api',
      owner,
      repo,
      branch,
      filePath: normalizedPath,
      commitHash: latestCommit.sha,
      fileHash: contentsData.sha,
      lastModified: latestCommit.commit.committer.date,
      htmlUrl
    };
  } catch (error) {
    // Re-throw known errors
    if (error instanceof FileNotFoundError ||
        error instanceof RepositoryNotFoundError ||
        error instanceof RateLimitError ||
        error instanceof AuthenticationError) {
      throw error;
    }

    // Wrap unknown errors
    throw new Error(
      `Failed to retrieve GitHub metadata for ${owner}/${repo}/${normalizedPath}: ${error.message}`,
      { cause: error }
    );
  }
}
