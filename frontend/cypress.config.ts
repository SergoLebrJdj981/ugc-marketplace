import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    specPattern: 'src/tests/e2e/**/*.cy.{ts,tsx}',
    supportFile: false
  }
});
