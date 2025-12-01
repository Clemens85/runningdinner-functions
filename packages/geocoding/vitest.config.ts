import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    reporters: process.env.CI ? ['default', 'junit'] : ['default'],
    outputFile: {
      junit: './reports/junit.xml',
    },
  },
});
