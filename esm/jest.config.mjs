/**
 * Jest configuration for ESM module testing
 */

export default {
  testEnvironment: 'node',
  transform: {},
  testMatch: [
    '**/*.test.mjs',
    '**/*.spec.mjs'
  ],
  collectCoverageFrom: [
    'git-identify.mjs',
    '!examples.mjs',
    '!*.test.mjs',
    '!*.spec.mjs'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  coverageReporters: [
    'text',
    'lcov',
    'html'
  ],
  verbose: true,
  testTimeout: 10000,
  moduleFileExtensions: ['mjs', 'js', 'json'],
  globals: {
    'NODE_ENV': 'test'
  }
};