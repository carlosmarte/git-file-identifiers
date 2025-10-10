/**
 * Checks if a file has changed by comparing two metadata objects
 * @param {object} meta1 - First metadata object
 * @param {object} meta2 - Second metadata object
 * @returns {boolean} True if file content has changed
 */
export function hasFileChanged(meta1, meta2) {
  if (!meta1 || !meta2) {
    return true; // If we can't compare, assume changed
  }

  // Primary check: file hash (blob SHA)
  // This is the most reliable indicator of file content changes
  if (meta1.fileHash && meta2.fileHash) {
    return meta1.fileHash !== meta2.fileHash;
  }

  // Fallback: commit hash
  // If file hashes aren't available, compare commit hashes
  if (meta1.commitHash && meta2.commitHash) {
    return meta1.commitHash !== meta2.commitHash;
  }

  // If we can't determine, assume changed
  return true;
}

/**
 * Compares an identifier against a stored value
 * @param {string} current - Current identifier
 * @param {string} stored - Stored identifier
 * @returns {boolean} True if identifiers match (file unchanged)
 */
export function compareIdentifier(current, stored) {
  if (!current || !stored) {
    return false;
  }

  return current === stored;
}

/**
 * Generates a change report by comparing current and previous file states
 * @param {object[]} current - Array of current batch results
 * @param {object} previous - Map of previous identifiers (filePath -> identifier)
 * @returns {object} Change report
 */
export function generateChangeReport(current, previous = {}) {
  if (!Array.isArray(current)) {
    throw new TypeError('current must be an array');
  }

  if (typeof previous !== 'object' || previous === null) {
    throw new TypeError('previous must be an object');
  }

  const report = {
    added: [],
    modified: [],
    unchanged: [],
    removed: [],
    errors: []
  };

  // Track which files we've seen
  const seenFiles = new Set();

  // Process current files
  for (const result of current) {
    if (!result.filePath) {
      continue;
    }

    seenFiles.add(result.filePath);

    // Handle errors
    if (result.status === 'error') {
      report.errors.push({
        filePath: result.filePath,
        error: result.error
      });
      continue;
    }

    const previousId = previous[result.filePath];

    if (!previousId) {
      // New file (not in previous state)
      report.added.push(result.filePath);
    } else if (result.identifier !== previousId) {
      // Modified file (identifier changed)
      report.modified.push(result.filePath);
    } else {
      // Unchanged file (identifier matches)
      report.unchanged.push(result.filePath);
    }
  }

  // Find removed files (in previous but not in current)
  for (const filePath of Object.keys(previous)) {
    if (!seenFiles.has(filePath)) {
      report.removed.push(filePath);
    }
  }

  return report;
}

/**
 * Creates a manifest from batch results for storage
 * @param {object[]} results - Batch results
 * @returns {object} Manifest object (filePath -> identifier)
 */
export function createManifest(results) {
  if (!Array.isArray(results)) {
    throw new TypeError('results must be an array');
  }

  const manifest = {};

  for (const result of results) {
    if (result.status === 'success' && result.filePath && result.identifier) {
      manifest[result.filePath] = result.identifier;
    }
  }

  return manifest;
}

/**
 * Loads a manifest from JSON
 * @param {string} json - JSON string
 * @returns {object} Manifest object
 */
export function loadManifest(json) {
  try {
    return JSON.parse(json);
  } catch (error) {
    throw new Error(`Failed to parse manifest JSON: ${error.message}`, { cause: error });
  }
}

/**
 * Saves a manifest to JSON
 * @param {object} manifest - Manifest object
 * @param {boolean} [pretty=true] - Pretty-print JSON
 * @returns {string} JSON string
 */
export function saveManifest(manifest, pretty = true) {
  if (typeof manifest !== 'object' || manifest === null) {
    throw new TypeError('manifest must be an object');
  }

  return pretty
    ? JSON.stringify(manifest, null, 2)
    : JSON.stringify(manifest);
}
