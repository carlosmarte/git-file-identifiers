import { getGitHubMetadata } from './metadata/github.mjs';
import { getLocalMetadata } from './metadata/local.mjs';
import { generateIdentifier } from './identifier.mjs';

/**
 * Processes multiple file identifiers in batch with concurrency control
 * @param {object[]} inputs - Array of input objects
 * @param {object} [options={}] - Batch options
 * @param {number} [options.concurrency=10] - Maximum concurrent operations
 * @param {boolean} [options.continueOnError=true] - Continue processing on individual errors
 * @param {Function} [options.progressCallback] - Progress callback(done, total)
 * @param {object} [options.identifierOptions] - Options passed to generateIdentifier
 * @returns {Promise<object[]>} Array of results
 */
export async function generateBatchIdentifiers(inputs, options = {}) {
  const {
    concurrency = 10,
    continueOnError = true,
    progressCallback = null,
    identifierOptions = {}
  } = options;

  if (!Array.isArray(inputs)) {
    throw new TypeError('inputs must be an array');
  }

  if (inputs.length === 0) {
    return [];
  }

  // Track progress
  let completed = 0;
  const total = inputs.length;

  /**
   * Process a single input
   * @param {object} input - Input object
   * @returns {Promise<object>} Result object
   */
  async function processOne(input) {
    const result = {
      filePath: input.filePath,
      identifier: null,
      status: 'error',
      error: null,
      metadata: null
    };

    try {
      // Validate input
      if (!input.type || !['github', 'local'].includes(input.type)) {
        throw new TypeError(`Invalid input type: ${input.type}. Must be 'github' or 'local'`);
      }

      // Get metadata based on type
      let metadata;
      if (input.type === 'github') {
        const { owner, repo, filePath, branch = 'main' } = input;
        if (!owner || !repo || !filePath) {
          throw new TypeError('GitHub input requires: owner, repo, filePath');
        }
        metadata = await getGitHubMetadata(owner, repo, filePath, branch);
      } else {
        // local
        const { repoPath, filePath } = input;
        if (!repoPath || !filePath) {
          throw new TypeError('Local input requires: repoPath, filePath');
        }
        metadata = await getLocalMetadata(repoPath, filePath);
      }

      // Generate identifier
      const idResult = generateIdentifier(metadata, identifierOptions);

      result.identifier = idResult.identifier;
      result.status = 'success';
      result.metadata = metadata;
      result.short = idResult.short;
    } catch (error) {
      result.error = error.message;

      if (!continueOnError) {
        throw error;
      }
    } finally {
      // Update progress
      completed++;
      if (progressCallback && typeof progressCallback === 'function') {
        progressCallback(completed, total);
      }
    }

    return result;
  }

  // Process with concurrency control
  // Use Promise.allSettled for error resilience
  const results = [];
  const processing = [];

  for (let i = 0; i < inputs.length; i++) {
    // Start processing
    const promise = processOne(inputs[i]);
    processing.push(promise);

    // Wait if we've reached concurrency limit
    if (processing.length >= concurrency) {
      const settled = await Promise.race(processing);
      results.push(settled);

      // Remove completed promise
      const index = processing.indexOf(settled);
      if (index > -1) {
        processing.splice(index, 1);
      }
    }
  }

  // Wait for remaining promises
  const remaining = await Promise.allSettled(processing);
  results.push(...remaining.map(r => r.value || { status: 'error', error: r.reason?.message }));

  return results;
}

/**
 * Batch processor class for reusable batch operations
 */
export class GitBatchProcessor {
  constructor(options = {}) {
    this.options = {
      concurrency: options.concurrency || 10,
      continueOnError: options.continueOnError !== false,
      identifierOptions: options.identifierOptions || {}
    };
    this.progressCallbacks = [];
  }

  /**
   * Adds a progress callback
   * @param {Function} callback - Progress callback
   */
  onProgress(callback) {
    if (typeof callback === 'function') {
      this.progressCallbacks.push(callback);
    }
    return this;
  }

  /**
   * Processes batch inputs
   * @param {object[]} inputs - Array of inputs
   * @returns {Promise<object[]>} Results
   */
  async process(inputs) {
    const progressCallback = (done, total) => {
      this.progressCallbacks.forEach(cb => cb(done, total));
    };

    return generateBatchIdentifiers(inputs, {
      ...this.options,
      progressCallback
    });
  }
}
