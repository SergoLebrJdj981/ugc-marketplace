import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { FlatCompat } from '@eslint/eslintrc';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const frontendDir = path.join(__dirname, 'frontend');

const compat = new FlatCompat({
  baseDirectory: frontendDir,
  resolvePluginsRelativeTo: frontendDir
});

export default [
  {
    ignores: [
      '**/node_modules/**',
      'backend/**',
      'notes/**',
      'assets/**',
      'scripts/**',
      'frontend/.next/**'
    ]
  },
  ...compat
    .config({
      extends: ['next/core-web-vitals', 'plugin:@typescript-eslint/recommended', 'prettier'],
      parser: '@typescript-eslint/parser',
      parserOptions: {
        project: ['./frontend/tsconfig.json'],
        tsconfigRootDir: __dirname,
        sourceType: 'module',
        ecmaVersion: 2020
      },
      plugins: ['@typescript-eslint', 'testing-library'],
      rules: {
        '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }],
        '@typescript-eslint/explicit-module-boundary-types': 'off'
      },
      overrides: [
        {
          files: ['**/*.test.{ts,tsx}', '**/__tests__/**/*.{ts,tsx}'],
          extends: ['plugin:testing-library/react'],
          env: { jest: true }
        },
        {
          files: ['src/tests/e2e/**/*'],
          env: { 'cypress/globals': true },
          plugins: ['cypress'],
          rules: {}
        }
      ]
    })
    .map((config) => ({
      ...config,
      files: config.files ? config.files.map((pattern) => `frontend/${pattern}`) : ['frontend/**/*.{ts,tsx,js,jsx}']
    }))
];
