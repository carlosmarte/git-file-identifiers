/**
 * Git File Identifiers - Usage Examples
 *
 * This file demonstrates all the functionality available in the git-identify ESM module.
 * Run with: node esm/examples.mjs
 */

import {
  GitFileId,
  generateGitHubUrlDirect,
  parseGitHubUrl,
  buildGitHubUrl,
  isValidGitHash,
  normalizeFilePath,
  getRepositoryInfo,
  isInGitRepository,
  GitBatchProcessor
} from './git-identify.mjs';

// ============================================================================
// Example 1: Quick GitHub URL Generation
// ============================================================================

async function example1_quickUrlGeneration() {
  console.log('\n=== Example 1: Quick GitHub URL Generation ===');

  try {
    // Generate URL directly without creating an instance
    const url = await generateGitHubUrlDirect('./README.md');
    console.log('GitHub URL for README.md:', url);
  } catch (error) {
    console.error('Error:', error.message);
  }
}

// ============================================================================
// Example 2: Repository Operations with GitFileId Class
// ============================================================================

async function example2_repositoryOperations() {
  console.log('\n=== Example 2: Repository Operations ===');

  const git = new GitFileId();

  try {
    // Initialize repository
    await git.findRepository('.');
    console.log('Repository initialized successfully');

    // Get HEAD reference
    const headRef = await git.getHeadRef();
    console.log('Current branch/HEAD:', headRef);

    // List all references
    const refs = await git.listRefs();
    console.log('Repository references:');
    refs.slice(0, 5).forEach(ref => console.log('  -', ref));
    if (refs.length > 5) {
      console.log(`  ... and ${refs.length - 5} more`);
    }

  } catch (error) {
    console.error('Error:', error.message);
  }
}

// ============================================================================
// Example 3: File Operations
// ============================================================================

async function example3_fileOperations() {
  console.log('\n=== Example 3: File Operations ===');

  const git = new GitFileId();

  try {
    await git.findRepository('.');

    // Check file status
    const status = await git.getFileStatus('package.json');
    console.log('package.json status:', status);

    // Get file hash
    try {
      const hash = await git.getFileHash('package.json');
      console.log('package.json commit hash:', hash);

      // Generate GitHub URL
      const url = await git.generateGitHubUrl('package.json');
      console.log('package.json GitHub URL:', url);
    } catch (error) {
      console.log('Could not get hash (file may be untracked or modified)');
    }

  } catch (error) {
    console.error('Error:', error.message);
  }
}

// ============================================================================
// Example 4: Git Objects Access
// ============================================================================

async function example4_gitObjects() {
  console.log('\n=== Example 4: Git Objects Access ===');

  const git = new GitFileId();

  try {
    await git.findRepository('.');

    // Get HEAD commit
    const headRef = await git.getHeadRef();
    console.log('Getting commit information for HEAD:', headRef);

    // Note: To get actual commit hash, you'd need to resolve the ref
    // This is a demonstration of the API pattern

    // Example with a known commit hash (replace with actual hash)
    // const commit = await git.getCommit('abc123...');
    // console.log('Commit message:', commit.message);
    // console.log('Author:', commit.authorName, '<' + commit.authorEmail + '>');
    // console.log('Date:', commit.date);

  } catch (error) {
    console.error('Error:', error.message);
  }
}

// ============================================================================
// Example 5: URL Parsing and Building
// ============================================================================

function example5_urlUtilities() {
  console.log('\n=== Example 5: URL Utilities ===');

  // Parse SSH URL
  try {
    const sshUrl = 'git@github.com:nodejs/node.git';
    const sshInfo = parseGitHubUrl(sshUrl);
    console.log('Parsed SSH URL:', sshInfo);
  } catch (error) {
    console.error('SSH parse error:', error.message);
  }

  // Parse HTTPS URL
  try {
    const httpsUrl = 'https://github.com/microsoft/vscode.git';
    const httpsInfo = parseGitHubUrl(httpsUrl);
    console.log('Parsed HTTPS URL:', httpsInfo);
  } catch (error) {
    console.error('HTTPS parse error:', error.message);
  }

  // Build GitHub URL
  const url = buildGitHubUrl(
    'rust-lang',
    'rust',
    'a1b2c3d4e5f6789012345678901234567890abcd',
    'src/main.rs'
  );
  console.log('Built URL:', url);

  // Validate Git hash
  console.log('Valid hash "abc123":', isValidGitHash('abc123'));
  console.log('Valid hash (40 chars):', isValidGitHash('a'.repeat(40)));

  // Normalize file paths
  console.log('Normalized "/src/main.rs":', normalizeFilePath('/src/main.rs'));
  console.log('Normalized "src\\\\lib\\\\mod.rs":', normalizeFilePath('src\\lib\\mod.rs'));
}

// ============================================================================
// Example 6: Repository Information Helper
// ============================================================================

async function example6_repositoryInfo() {
  console.log('\n=== Example 6: Repository Information ===');

  try {
    const info = await getRepositoryInfo('package.json');
    console.log('Repository info for package.json:');
    console.log('  Branch:', info.branch);
    console.log('  Status:', info.fileStatus);
    console.log('  Commit:', info.commitHash || 'N/A');
    console.log('  URL:', info.gitHubUrl || 'N/A');
  } catch (error) {
    console.error('Error:', error.message);
  }
}

// ============================================================================
// Example 7: Check if Path is in Git Repository
// ============================================================================

async function example7_checkRepository() {
  console.log('\n=== Example 7: Check Repository ===');

  const currentDir = await isInGitRepository('.');
  console.log('Current directory is in Git repo:', currentDir);

  const tempDir = await isInGitRepository('/tmp');
  console.log('/tmp is in Git repo:', tempDir);
}

// ============================================================================
// Example 8: Batch Processing
// ============================================================================

async function example8_batchProcessing() {
  console.log('\n=== Example 8: Batch Processing ===');

  const batch = new GitBatchProcessor();

  try {
    await batch.initialize('.');

    // Generate URLs for multiple files
    const files = ['package.json', 'README.md', 'nonexistent.txt'];
    const urls = await batch.generateUrls(files);

    console.log('Batch URL generation:');
    urls.forEach(result => {
      if (result.error) {
        console.log(`  ${result.filePath}: ERROR - ${result.error}`);
      } else {
        console.log(`  ${result.filePath}: ${result.url}`);
      }
    });

    // Get statuses for multiple files
    const statuses = await batch.getStatuses(files);

    console.log('\nBatch status check:');
    statuses.forEach(result => {
      if (result.error) {
        console.log(`  ${result.filePath}: ERROR - ${result.error}`);
      } else {
        console.log(`  ${result.filePath}: ${result.status}`);
      }
    });

  } catch (error) {
    console.error('Error:', error.message);
  }
}

// ============================================================================
// Example 9: Error Handling
// ============================================================================

async function example9_errorHandling() {
  console.log('\n=== Example 9: Error Handling ===');

  const git = new GitFileId();

  // Try to use without initialization
  try {
    await git.generateGitHubUrl('README.md');
  } catch (error) {
    console.log('Expected error (not initialized):', error.message);
  }

  // Try with non-existent repository
  try {
    await git.findRepository('/tmp/nonexistent');
  } catch (error) {
    console.log('Expected error (no repository):', error.message);
  }

  // Initialize properly and try non-existent file
  try {
    await git.findRepository('.');
    await git.getFileHash('/nonexistent/file.txt');
  } catch (error) {
    console.log('Expected error (file not found):', error.message);
  }
}

// ============================================================================
// Example 10: Advanced Git Object Operations
// ============================================================================

async function example10_advancedGitObjects() {
  console.log('\n=== Example 10: Advanced Git Object Operations ===');

  const git = new GitFileId();

  try {
    await git.findRepository('.');

    // This example shows the API pattern for working with Git objects
    // In practice, you would get these hashes from actual Git operations

    console.log('Git object API demonstration:');
    console.log('- getBlob(hash) returns GitBlob with id, size, isBinary');
    console.log('- getTree(hash) returns GitTree with id, length');
    console.log('- getCommit(hash) returns GitCommit with full commit info');
    console.log('- getTag(hash) returns GitTag with tag details');

    // Example of how you might use these APIs:
    /*
    const fileHash = await git.getFileHash('src/main.rs');
    const commit = await git.getCommit(fileHash);
    const tree = await git.getTree(commit.treeId);
    console.log(`Commit ${commit.id} has tree with ${tree.length} entries`);
    */

  } catch (error) {
    console.error('Error:', error.message);
  }
}

// ============================================================================
// Main Runner
// ============================================================================

async function main() {
  console.log('Git File Identifiers - ESM Module Examples');
  console.log('==========================================');

  // Run all examples
  await example1_quickUrlGeneration();
  await example2_repositoryOperations();
  await example3_fileOperations();
  await example4_gitObjects();
  example5_urlUtilities();
  await example6_repositoryInfo();
  await example7_checkRepository();
  await example8_batchProcessing();
  await example9_errorHandling();
  await example10_advancedGitObjects();

  console.log('\n==========================================');
  console.log('All examples completed!');
}

// Run examples if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}

// Export individual examples for testing
export {
  example1_quickUrlGeneration,
  example2_repositoryOperations,
  example3_fileOperations,
  example4_gitObjects,
  example5_urlUtilities,
  example6_repositoryInfo,
  example7_checkRepository,
  example8_batchProcessing,
  example9_errorHandling,
  example10_advancedGitObjects
};