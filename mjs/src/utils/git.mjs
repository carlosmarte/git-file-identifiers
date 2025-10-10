import { exec } from 'child_process';
import { promisify } from 'util';
import { GitCommandError } from '../errors.mjs';

const execAsync = promisify(exec);

/**
 * Executes a Git command and returns the output
 * @param {string} command - Git command to execute
 * @param {string} cwd - Working directory
 * @returns {Promise<string>} Command output (trimmed)
 * @throws {GitCommandError} If command fails
 */
export async function executeGitCommand(command, cwd = process.cwd()) {
  try {
    const { stdout, stderr } = await execAsync(command, {
      cwd,
      maxBuffer: 10 * 1024 * 1024, // 10MB buffer
      env: { ...process.env, LC_ALL: 'C' } // Force English output
    });

    // Git sometimes writes to stderr even on success
    // Only throw if the command actually failed (caught in catch block)
    return stdout.trim();
  } catch (error) {
    throw new GitCommandError(
      `Git command failed: ${command}`,
      {
        command,
        exitCode: error.code,
        stderr: error.stderr?.trim(),
        cause: error,
        context: { cwd }
      }
    );
  }
}

/**
 * Checks if a directory is a Git repository
 * @param {string} repoPath - Path to check
 * @returns {Promise<boolean>} True if directory is a Git repository
 */
export async function isGitRepository(repoPath) {
  try {
    await executeGitCommand('git rev-parse --git-dir', repoPath);
    return true;
  } catch {
    return false;
  }
}

/**
 * Gets the repository root directory
 * @param {string} path - Path within repository
 * @returns {Promise<string>} Absolute path to repository root
 * @throws {RepositoryNotFoundError} If not in a Git repository
 */
export async function getRepositoryRoot(path) {
  const { RepositoryNotFoundError } = await import('../errors.mjs');

  try {
    const root = await executeGitCommand('git rev-parse --show-toplevel', path);
    return root;
  } catch (error) {
    throw new RepositoryNotFoundError(
      `No Git repository found at path: ${path}`,
      {
        cause: error,
        context: { path }
      }
    );
  }
}
