import crypto from 'crypto';
import { canonicalizeMetadata, normalizeMetadata } from './metadata/normalizer.mjs';

/**
 * Generates a deterministic unique identifier from metadata
 * @param {object} meta - Normalized metadata object
 * @param {object} [options={}] - Generation options
 * @param {'sha256'|'sha1'} [options.algorithm='sha256'] - Hash algorithm
 * @param {'hex'|'base64'} [options.encoding='hex'] - Output encoding
 * @param {number|false} [options.truncate=false] - Truncate to N characters (or false for full hash)
 * @param {boolean} [options.includeMetadata=false] - Include metadata in result
 * @returns {object} Identifier result
 */
export function generateIdentifier(meta, options = {}) {
  const {
    algorithm = 'sha256',
    encoding = 'hex',
    truncate = false,
    includeMetadata = false
  } = options;

  // Validate algorithm
  if (!['sha256', 'sha1'].includes(algorithm)) {
    throw new TypeError(`Invalid algorithm: ${algorithm}. Must be 'sha256' or 'sha1'`);
  }

  // Validate encoding
  if (!['hex', 'base64'].includes(encoding)) {
    throw new TypeError(`Invalid encoding: ${encoding}. Must be 'hex' or 'base64'`);
  }

  // Normalize metadata to ensure consistency
  const normalized = normalizeMetadata(meta);

  // Create canonical JSON representation
  const canonical = canonicalizeMetadata(normalized);

  // Generate hash
  const hash = crypto
    .createHash(algorithm)
    .update(canonical, 'utf8')
    .digest(encoding);

  // Create full identifier with algorithm prefix
  const fullIdentifier = `${algorithm}:${hash}`;

  // Generate short version (first 8 characters of hash)
  const short = hash.substring(0, 8);

  // Optionally truncate
  const identifier = truncate && typeof truncate === 'number'
    ? `${algorithm}:${hash.substring(0, truncate)}`
    : fullIdentifier;

  const result = {
    identifier,
    short,
    algorithm
  };

  // Optionally include metadata
  if (includeMetadata) {
    result.metadata = normalized;
  }

  return result;
}

/**
 * Generates identifiers for multiple metadata objects
 * @param {object[]} metadataArray - Array of metadata objects
 * @param {object} [options={}] - Generation options (passed to generateIdentifier)
 * @returns {object[]} Array of identifier results
 */
export function generateIdentifiers(metadataArray, options = {}) {
  if (!Array.isArray(metadataArray)) {
    throw new TypeError('metadataArray must be an array');
  }

  return metadataArray.map(meta => generateIdentifier(meta, options));
}
