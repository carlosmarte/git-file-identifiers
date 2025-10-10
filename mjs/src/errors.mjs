/**
 * Base error class for all Git-related errors
 */
export class GitError extends Error {
  constructor(message, options = {}) {
    super(message, { cause: options.cause });
    this.name = this.constructor.name;
    this.code = options.code || 'GIT_ERROR';
    this.context = options.context || {};

    // Maintains proper stack trace for where our error was thrown (only available on V8)
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, this.constructor);
    }
  }

  toJSON() {
    return {
      name: this.name,
      code: this.code,
      message: this.message,
      context: this.context,
      stack: this.stack
    };
  }
}

/**
 * Error thrown when a Git repository cannot be found
 */
export class RepositoryNotFoundError extends GitError {
  constructor(message, options = {}) {
    super(message, {
      ...options,
      code: options.code || 'REPOSITORY_NOT_FOUND'
    });
  }
}

/**
 * Error thrown when a file is not found in the repository
 */
export class FileNotFoundError extends GitError {
  constructor(message, options = {}) {
    super(message, {
      ...options,
      code: options.code || 'FILE_NOT_FOUND'
    });
  }
}

/**
 * Error thrown when an invalid Git hash is encountered
 */
export class InvalidHashError extends GitError {
  constructor(message, options = {}) {
    super(message, {
      ...options,
      code: options.code || 'INVALID_HASH'
    });
  }
}

/**
 * Error thrown when GitHub API rate limit is exceeded
 */
export class RateLimitError extends GitError {
  constructor(message, options = {}) {
    super(message, {
      ...options,
      code: options.code || 'RATE_LIMIT_EXCEEDED'
    });
    this.resetAt = options.resetAt || null;
  }

  toJSON() {
    return {
      ...super.toJSON(),
      resetAt: this.resetAt
    };
  }
}

/**
 * Error thrown when GitHub authentication fails
 */
export class AuthenticationError extends GitError {
  constructor(message, options = {}) {
    super(message, {
      ...options,
      code: options.code || 'AUTHENTICATION_ERROR'
    });
  }
}

/**
 * Error thrown when a Git command execution fails
 */
export class GitCommandError extends GitError {
  constructor(message, options = {}) {
    super(message, {
      ...options,
      code: options.code || 'GIT_COMMAND_ERROR'
    });
    this.command = options.command || null;
    this.exitCode = options.exitCode || null;
    this.stderr = options.stderr || null;
  }

  toJSON() {
    return {
      ...super.toJSON(),
      command: this.command,
      exitCode: this.exitCode,
      stderr: this.stderr
    };
  }
}
