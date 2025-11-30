import { baseNodeConfig } from '../../eslint.config.js';

/**
 * ESLint configuration for Node.js/Lambda packages
 * Extends the shared base configuration from the monorepo root
 */

/** @type {import('eslint').Linter.Config[]} */
export default [
  ...baseNodeConfig,
  {
    languageOptions: {
      parserOptions: {
        // Point to the local tsconfig.json for type-aware linting
        tsconfigRootDir: import.meta.dirname,
      },
    },
  },
  // Add package-specific overrides here if needed
  // {
  //   rules: {
  //     // Example: disable a specific rule for this package only
  //     // '@typescript-eslint/no-explicit-any': 'error',
  //   },
  // },
];
