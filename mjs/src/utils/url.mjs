/**
 * Parses a GitHub remote URL to extract owner and repository name
 * Supports both SSH and HTTPS formats
 * @param {string} remoteUrl - Git remote URL
 * @returns {{owner: string, repo: string} | null} Parsed owner and repo, or null if not a GitHub URL
 */
export function parseGitHubUrl(remoteUrl) {
  if (typeof remoteUrl !== 'string' || !remoteUrl) {
    return null;
  }

  // SSH format: git@github.com:owner/repo.git
  const sshPattern = /^git@github\.com:([^/]+)\/(.+?)(\.git)?$/;
  const sshMatch = remoteUrl.match(sshPattern);

  if (sshMatch) {
    return {
      owner: sshMatch[1],
      repo: sshMatch[2]
    };
  }

  // HTTPS format: https://github.com/owner/repo.git
  const httpsPattern = /^https:\/\/github\.com\/([^/]+)\/(.+?)(\.git)?$/;
  const httpsMatch = remoteUrl.match(httpsPattern);

  if (httpsMatch) {
    return {
      owner: httpsMatch[1],
      repo: httpsMatch[2]
    };
  }

  // Also support GitLab and Bitbucket patterns
  // GitLab SSH: git@gitlab.com:owner/repo.git
  const gitlabSshPattern = /^git@gitlab\.com:([^/]+)\/(.+?)(\.git)?$/;
  const gitlabSshMatch = remoteUrl.match(gitlabSshPattern);

  if (gitlabSshMatch) {
    return {
      owner: gitlabSshMatch[1],
      repo: gitlabSshMatch[2],
      host: 'gitlab'
    };
  }

  // GitLab HTTPS: https://gitlab.com/owner/repo.git
  const gitlabHttpsPattern = /^https:\/\/gitlab\.com\/([^/]+)\/(.+?)(\.git)?$/;
  const gitlabHttpsMatch = remoteUrl.match(gitlabHttpsPattern);

  if (gitlabHttpsMatch) {
    return {
      owner: gitlabHttpsMatch[1],
      repo: gitlabHttpsMatch[2],
      host: 'gitlab'
    };
  }

  // Bitbucket SSH: git@bitbucket.org:owner/repo.git
  const bitbucketSshPattern = /^git@bitbucket\.org:([^/]+)\/(.+?)(\.git)?$/;
  const bitbucketSshMatch = remoteUrl.match(bitbucketSshPattern);

  if (bitbucketSshMatch) {
    return {
      owner: bitbucketSshMatch[1],
      repo: bitbucketSshMatch[2],
      host: 'bitbucket'
    };
  }

  // Bitbucket HTTPS: https://bitbucket.org/owner/repo.git
  const bitbucketHttpsPattern = /^https:\/\/bitbucket\.org\/([^/]+)\/(.+?)(\.git)?$/;
  const bitbucketHttpsMatch = remoteUrl.match(bitbucketHttpsPattern);

  if (bitbucketHttpsMatch) {
    return {
      owner: bitbucketHttpsMatch[1],
      repo: bitbucketHttpsMatch[2],
      host: 'bitbucket'
    };
  }

  return null;
}

/**
 * Builds a GitHub permalink URL for a file at a specific commit
 * @param {string} owner - Repository owner
 * @param {string} repo - Repository name
 * @param {string} commitHash - Commit hash
 * @param {string} filePath - File path (POSIX format)
 * @returns {string} GitHub permalink URL
 */
export function buildGitHubUrl(owner, repo, commitHash, filePath) {
  if (!owner || !repo || !commitHash || !filePath) {
    throw new TypeError('All parameters (owner, repo, commitHash, filePath) are required');
  }

  // Ensure file path starts without leading slash
  const normalizedPath = filePath.replace(/^\/+/, '');

  // Build permalink: https://github.com/owner/repo/blob/commitHash/path
  return `https://github.com/${owner}/${repo}/blob/${commitHash}/${normalizedPath}`;
}
