import { InvalidHashError } from '../errors.mjs';

/**
 * Validates that a string is a valid Git hash (40-character hexadecimal)
 * @param {string} hash - The hash to validate
 * @returns {boolean} True if valid Git hash format
 */
export function isValidGitHash(hash) {
  if (typeof hash !== 'string') {
    return false;
  }

  // Git hashes are 40-character hexadecimal strings (SHA-1)
  const gitHashPattern = /^[0-9a-f]{40}$/i;
  return gitHashPattern.test(hash);
}

/**
 * Validates and throws if hash is invalid
 * @param {string} hash - The hash to validate
 * @param {string} fieldName - Name of the field for error message
 * @throws {InvalidHashError} If hash is invalid
 */
export function validateGitHash(hash, fieldName = 'hash') {
  if (!isValidGitHash(hash)) {
    throw new InvalidHashError(
      `Invalid Git hash format for ${fieldName}: expected 40-character hex string, got "${hash}"`,
      {
        context: { hash, fieldName }
      }
    );
  }
}
