import { baseNodeConfig } from '../../eslint.config.js';

/** @type {import('eslint').Linter.Config[]} */
export default [
  ...baseNodeConfig,
  {
    languageOptions: {
      parserOptions: {
        tsconfigRootDir: import.meta.dirname,
      },
    },
  },
];
