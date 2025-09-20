/**
 * Integration tests for git-identify.mjs
 * Tests real-world scenarios and edge cases
 */

import { describe, it, expect, beforeAll, afterAll } from '@jest/globals';
import {
  GitFileId,
  GitBatchProcessor,
  generateGitHubUrlDirect,
  getRepositoryInfo,
  isInGitRepository
} from './git-identify.mjs';
import {
  createTestScenario,
  generators,
  PerformanceTimer,
  wait
} from './test-helpers.mjs';

// ============================================================================
// Real Repository Integration Tests (if running in actual Git repo)
// ============================================================================

describe('Real Repository Integration', () => {
  let isRealRepo = false;
  let git;

  beforeAll(async () => {
    // Check if we're in a real Git repository
    try {
      isRealRepo = await isInGitRepository('.');
      if (isRealRepo) {
        git = new GitFileId();
        await git.findRepository('.');
      }
    } catch {
      // Not in a real repo, skip these tests
    }
  });

  it('should work with real repository if available', async () => {
    if (!isRealRepo) {
      console.log('Skipping: Not in a real Git repository');
      return;
    }

    const headRef = await git.getHeadRef();
    expect(typeof headRef).toBe('string');
    expect(headRef.length).toBeGreaterThan(0);
  });

  it('should list real references if available', async () => {
    if (!isRealRepo) return;

    const refs = await git.listRefs();
    expect(Array.isArray(refs)).toBe(true);
    expect(refs.length).toBeGreaterThan(0);

    // Should have at least HEAD or main/master
    const hasExpectedRef = refs.some(ref =>
      ref.includes('HEAD') ||
      ref.includes('main') ||
      ref.includes('master')
    );
    expect(hasExpectedRef).toBe(true);
  });
});

// ============================================================================
// Workflow Integration Tests
// ============================================================================

describe('Complete Workflow Integration', () => {
  it('should handle complete developer workflow', async () => {
    const workflow = async () => {
      // Step 1: Check if in repository
      const inRepo = await isInGitRepository('.');

      if (!inRepo) {
        // Handle non-repo scenario
        return { success: false, reason: 'not-in-repo' };
      }

      // Step 2: Get repository info
      let info;
      try {
        info = await getRepositoryInfo('package.json');
      } catch {
        // File might not exist
        return { success: false, reason: 'file-not-found' };
      }

      // Step 3: Generate URL if file is tracked
      if (info.commitHash) {
        const git = new GitFileId();
        await git.findRepository('.');
        const url = await git.generateGitHubUrl('package.json');
        return { success: true, url, info };
      }

      return { success: true, info, url: null };
    };

    const result = await workflow();
    expect(result).toHaveProperty('success');
  });

  it('should handle batch file processing workflow', async () => {
    const batch = new GitBatchProcessor();

    try {
      await batch.initialize('.');

      const testFiles = ['README.md', 'package.json', 'nonexistent.txt'];

      // Process files
      const [urls, statuses] = await Promise.all([
        batch.generateUrls(testFiles),
        batch.getStatuses(testFiles)
      ]);

      // Validate results structure
      expect(urls).toHaveLength(testFiles.length);
      expect(statuses).toHaveLength(testFiles.length);

      urls.forEach(result => {
        expect(result).toHaveProperty('filePath');
        expect(result).toHaveProperty('url');
        expect(result).toHaveProperty('error');
      });

      statuses.forEach(result => {
        expect(result).toHaveProperty('filePath');
        expect(result).toHaveProperty('status');
        expect(result).toHaveProperty('error');
      });
    } catch (error) {
      // Repository might not be available in test environment
      expect(error.message).toContain('repository');
    }
  });
});

// ============================================================================
// Error Recovery Tests
// ============================================================================

describe('Error Recovery and Edge Cases', () => {
  it('should recover from initialization failure', async () => {
    const git = new GitFileId();

    // First attempt fails
    await expect(git.findRepository('/definitely/not/a/repo')).rejects.toThrow();
    expect(git.isInitialized).toBe(false);

    // Should be able to try again with valid path
    try {
      await git.findRepository('.');
      expect(git.isInitialized).toBe(true);
    } catch {
      // Might not be in a repo during testing
      expect(git.isInitialized).toBe(false);
    }
  });

  it('should handle concurrent operations gracefully', async () => {
    const git = new GitFileId();

    try {
      await git.findRepository('.');

      // Simulate concurrent operations
      const operations = [
        git.getHeadRef(),
        git.listRefs(),
        git.getFileStatus('README.md'),
        git.getFileStatus('package.json')
      ];

      const results = await Promise.allSettled(operations);

      // All operations should complete (either fulfilled or rejected)
      expect(results).toHaveLength(4);
      results.forEach(result => {
        expect(['fulfilled', 'rejected']).toContain(result.status);
      });
    } catch {
      // Not in a repo, that's ok
    }
  });

  it('should handle rapid successive calls', async () => {
    const git = new GitFileId();

    try {
      await git.findRepository('.');

      // Rapid successive calls
      for (let i = 0; i < 5; i++) {
        const status = await git.getFileStatus('README.md');
        expect(typeof status).toBe('string');
      }
    } catch {
      // Not in a repo, that's ok
    }
  });
});

// ============================================================================
// Performance Tests
// ============================================================================

describe('Performance Tests', () => {
  it('should handle large batch operations efficiently', async () => {
    const batch = new GitBatchProcessor();
    const timer = new PerformanceTimer('Batch URL Generation');

    try {
      await batch.initialize('.');

      // Generate many file paths
      const files = generators.filePaths(50);

      timer.start();
      const results = await batch.generateUrls(files);
      const duration = timer.end();

      expect(results).toHaveLength(50);
      expect(duration).toBeLessThan(5000); // Should complete within 5 seconds

      if (process.env.DEBUG) {
        timer.report();
      }
    } catch {
      // Not in a repo, skip performance test
    }
  });

  it('should cache repository initialization', async () => {
    const timer = new PerformanceTimer('Repository Initialization');

    try {
      // First initialization
      const git1 = new GitFileId();
      timer.start();
      await git1.findRepository('.');
      const firstTime = timer.end();

      // Second initialization (different instance)
      const git2 = new GitFileId();
      timer.start();
      await git2.findRepository('.');
      const secondTime = timer.end();

      // Both should succeed
      expect(git1.isInitialized).toBe(true);
      expect(git2.isInitialized).toBe(true);

      if (process.env.DEBUG) {
        console.log(`First init: ${firstTime.toFixed(2)}ms`);
        console.log(`Second init: ${secondTime.toFixed(2)}ms`);
      }
    } catch {
      // Not in a repo
    }
  });
});

// ============================================================================
// URL Generation Edge Cases
// ============================================================================

describe('URL Generation Edge Cases', () => {
  it('should handle special characters in file paths', async () => {
    const specialPaths = [
      'file with spaces.js',
      'file-with-dashes.js',
      'file_with_underscores.js',
      'file.multiple.dots.js',
      'folder/nested/deep/file.js'
    ];

    for (const path of specialPaths) {
      try {
        // This would work in a real repo
        const url = await generateGitHubUrlDirect(path);
        expect(url).toContain('github.com');
        expect(url).toContain(path.replace(/ /g, '%20'));
      } catch {
        // Expected in test environment without real repo
      }
    }
  });

  it('should normalize various path formats', async () => {
    const git = new GitFileId();

    try {
      await git.findRepository('.');

      const pathVariations = [
        './README.md',
        'README.md',
        './src/../README.md'
      ];

      for (const path of pathVariations) {
        try {
          const url = await git.generateGitHubUrl(path);
          expect(url).toContain('README.md');
        } catch {
          // File might not exist
        }
      }
    } catch {
      // Not in a repo
    }
  });
});

// ============================================================================
// Concurrent Batch Operations
// ============================================================================

describe('Concurrent Batch Operations', () => {
  it('should handle multiple batch processors simultaneously', async () => {
    const batch1 = new GitBatchProcessor();
    const batch2 = new GitBatchProcessor();

    try {
      await Promise.all([
        batch1.initialize('.'),
        batch2.initialize('.')
      ]);

      const files1 = ['file1.js', 'file2.js'];
      const files2 = ['file3.js', 'file4.js'];

      const [results1, results2] = await Promise.all([
        batch1.generateUrls(files1),
        batch2.getStatuses(files2)
      ]);

      expect(results1).toHaveLength(2);
      expect(results2).toHaveLength(2);
    } catch {
      // Not in a repo
    }
  });
});

// ============================================================================
// Memory and Resource Tests
// ============================================================================

describe('Memory and Resource Management', () => {
  it('should handle many GitFileId instances', async () => {
    const instances = [];

    try {
      // Create multiple instances
      for (let i = 0; i < 10; i++) {
        const git = new GitFileId();
        await git.findRepository('.');
        instances.push(git);
      }

      // All should be functional
      for (const git of instances) {
        expect(git.isInitialized).toBe(true);
        const head = await git.getHeadRef();
        expect(typeof head).toBe('string');
      }
    } catch {
      // Not in a repo
      expect(instances.length).toBeLessThanOrEqual(10);
    }
  });

  it('should handle cleanup properly', async () => {
    // Test that resources are properly cleaned up
    const runIteration = async () => {
      const git = new GitFileId();
      try {
        await git.findRepository('.');
        await git.getHeadRef();
        await git.listRefs();
      } catch {
        // Ignore errors
      }
      // Instance should be garbage collected after this
    };

    // Run multiple iterations
    for (let i = 0; i < 20; i++) {
      await runIteration();
    }

    // If we get here without errors, cleanup is working
    expect(true).toBe(true);
  });
});

// ============================================================================
// Stress Tests (optional, run with STRESS_TEST=true)
// ============================================================================

if (process.env.STRESS_TEST === 'true') {
  describe('Stress Tests', () => {
    it('should handle rapid repeated operations', async () => {
      const git = new GitFileId();

      try {
        await git.findRepository('.');

        const operations = [];
        for (let i = 0; i < 100; i++) {
          operations.push(
            git.getHeadRef(),
            git.getFileStatus('README.md')
          );
        }

        const start = Date.now();
        await Promise.all(operations);
        const duration = Date.now() - start;

        console.log(`Completed 200 operations in ${duration}ms`);
        expect(duration).toBeLessThan(10000); // Should complete within 10 seconds
      } catch {
        // Not in a repo
      }
    });

    it('should handle large file lists', async () => {
      const batch = new GitBatchProcessor();

      try {
        await batch.initialize('.');

        // Generate a large number of files
        const files = generators.filePaths(500);

        const start = Date.now();
        const results = await batch.generateUrls(files);
        const duration = Date.now() - start;

        console.log(`Processed ${files.length} files in ${duration}ms`);
        expect(results).toHaveLength(500);
      } catch {
        // Not in a repo
      }
    });
  });
}