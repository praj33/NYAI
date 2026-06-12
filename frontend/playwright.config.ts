/// <reference types="node" />
import { defineConfig, devices } from '@playwright/test';

/**
 * Gravitas Decision Engine - E2E Test Configuration
 * Validates end-to-end data flow: React UI → Raj's Backend API → Vedant's Formatter → React UI
 */
export default defineConfig({
  // Test directory
  testDir: './e2e',
  
  // Fully qualify all tests - no "only" in CI
  fullyParallel: true,
  
  // Retry failed tests in CI
  retries: process.env.CI ? 2 : 0,
  
  // Limit workers for consistency
  workers: process.env.CI ? 1 : undefined,
  
  // Reporter configuration
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list']
  ],
  
  // Timeout per test
  timeout: 60 * 1000,
  
  // Timeout for expect() assertions
  expect: {
    timeout: 10 * 1000
  },
  
  // Global setup
  use: {
    // Base URL for tests
    baseURL: process.env.FRONTEND_URL || 'http://localhost:3000',
    
    // Collect traces on failure
    trace: 'on-first-retry',
    
    // Collect screenshots on failure
    screenshot: 'only-on-failure',
    
    // Video on failure
    video: 'retain-on-failure',
    
    // Action timeout
    actionTimeout: 15 * 1000,
    
    // Locale
    locale: 'en-US',
    
    // Timezone
    timezoneId: 'Asia/Kolkata'
  },
  
  // Configure projects for different browsers
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    }
  ],
  
  // Local dev server
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    timeout: 120 * 1000,
    reuseExistingServer: !process.env.CI
  }
});