# Gravitas Decision Engine - E2E Test Suite Setup Guide

## Overview

This document provides complete setup and execution instructions for the End-to-End (E2E) validation suite for the Gravitas Decision Engine. The suite validates the complete data flow:

```
User Input → Raj's Backend API → Vedant's Formatter → React UI Rendering
```

## Prerequisites

1. **Node.js** (v18+)
2. **npm** or **yarn**
3. **Git** (for version control)
4. **Chrome/Firefox/Safari** browsers for cross-browser testing

## Installation Steps

### Step 1: Navigate to Frontend Directory

```bash
cd frontend
```

### Step 2: Install Playwright and Dependencies

```bash
# Install Playwright and its test runner
npm install -D @playwright/test

# Install browser binaries (Chromium, Firefox, WebKit)
npx playwright install chromium
npx playwright install firefox
npx playwright install webkit

# Install TypeScript type definitions
npm install -D @types/node typescript
```

**Alternative: Install all browsers at once**
```bash
npx playwright install --with-deps
```

### Step 3: Verify Installation

```bash
# Check Playwright version
npx playwright --version

# Run a quick test to verify browsers work
npx playwright install-deps
```

## Configuration

### Environment Variables (Optional)

Create a `.env` file in the `frontend` directory:

```env
# Backend API URL (default: https://nyaya-ai-0f02.onrender.com)
BACKEND_URL=https://nyaya-ai-0f02.onrender.com

# Frontend URL (default: http://localhost:5173)
FRONTEND_URL=http://localhost:5173

# Run in CI mode (enables retries, limits workers)
CI=true
```

### Playwright Configuration

The configuration is stored in [`playwright.config.ts`](playwright.config.ts). Key settings:

- **Test Directory**: `./e2e`
- **Base URL**: `http://localhost:5173`
- **Browsers**: Chrome, Firefox, WebKit, Mobile
- **Retries**: 2 in CI, 0 locally
- **Timeout**: 60 seconds per test
- **Reporter**: HTML + List

## Running the Tests

### Start the Frontend Development Server

```bash
# Terminal 1: Start frontend
cd frontend
npm run dev
```

### Run E2E Tests

```bash
# Terminal 2: Run tests
cd frontend
npx playwright test
```

### Run Specific Test Groups

```bash
# Continuity Test only
npx playwright test --grep "Continuity Test"

# Enforcement Gatekeeper Test only
npx playwright test --grep "Enforcement Gatekeeper Test"

# Rendering Fidelity Test only
npx playwright test --grep "Rendering Fidelity Test"

# Resiliency Test only
npx playwright test --grep "Resiliency Test"
```

### Run with UI Mode (Interactive)

```bash
npx playwright test --ui
```

### Run in Headless Mode (CI)

```bash
npx playwright test --project=chromium
```

### Generate HTML Report

```bash
npx playwright show-report
```

## Test Scenarios Explained

### 1. Continuity Test (trace_id Integrity)

**Purpose**: Verify that the `trace_id` returned in the API response is physically rendered in the DOM.

**Flow**:
1. Submit a legal query
2. Intercept the API response and capture `trace_id`
3. Verify `trace_id` appears in the UI (footer, meta-tag, or data-testid element)

**Expected Result**: Exact `trace_id` from API is visible in the rendered page.

### 2. Enforcement Gatekeeper Test (State Accuracy)

**Purpose**: Verify Phase 4 logic - the UI strictly adheres to enforcement states.

**Scenarios**:
- **ALLOW**: Decision content is rendered
- **BLOCK**: Decision string is NOT present in DOM when state is BLOCK
- **ESCALATE**: Escalation UI is displayed

**Expected Result**: UI behavior matches enforcement state rules.

### 3. Rendering Fidelity Test (Data Matching)

**Purpose**: Verify JSON response keys exactly match UI selectors.

**Flow**:
1. Submit complex case with known mock payload
2. Verify `casePayload.decision` matches `<div data-testid="final-decision">`
3. Verify timeline and procedural steps arrays render correctly
4. Verify enforcement decision matches UI

**Expected Result**: 100% data fidelity between API response and UI rendering.

### 4. Resiliency Test (Backend Failure)

**Purpose**: Verify Phase 5 Error Boundary triggers correctly on failures.

**Scenarios**:
- **500 Internal Server Error**: Error boundary displays, no unhandled React exceptions
- **Network Timeout**: Graceful timeout handling with retry option
- **ECONNREFUSED**: Backend down handling

**Expected Result**: Proper error UI without crashing the application.

## Project Structure

```
frontend/
├── e2e/
│   └── gravitas.spec.ts      # Main test suite
├── playwright.config.ts      # Playwright configuration
├── package.json              # Dependencies
├── src/
│   ├── components/          # React components
│   │   ├── ErrorBoundary.jsx
│   │   ├── EnforcementStatusCard.jsx
│   │   └── ...
│   ├── services/
│   │   └── nyayaApi.js       # API service
│   └── ...
└── ...
```

## Troubleshooting

### Common Issues

**1. Playwright not found**
```bash
npm install -D @playwright/test
```

**2. Browser installation fails**
```bash
# Linux (Debian/Ubuntu)
npx playwright install-deps

# macOS
brew install playwright
```

**3. Frontend not running**
```bash
# Ensure dev server is running
npm run dev
```

**4. Tests timeout**
```bash
# Increase timeout
npx playwright test --timeout=120000
```

**5. Port already in use**
```bash
# Kill existing process
lsof -i :5173
kill <PID>
```

### Debug Mode

```bash
# Run with debugging
npx playwright test --debug

# Show browser
npx playwright test --headed

# Generate trace on failure
npx playwright test --trace on
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm install
        working-directory: ./frontend
      - run: npx playwright install --with-deps
        working-directory: ./frontend
      - run: npm run dev &
        working-directory: ./frontend
      - run: npx playwright test
        working-directory: ./frontend
        env:
          CI: true
```

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any
    stages {
        stage('Install') {
            steps {
                dir('frontend') {
                    sh 'npm install'
                    sh 'npx playwright install chromium'
                }
            }
        }
        stage('Start Frontend') {
            steps {
                dir('frontend') {
                    sh 'npm run dev &'
                }
            }
        }
        stage('E2E Tests') {
            steps {
                dir('frontend') {
                    sh 'npx playwright test'
                }
            }
        }
    }
}
```

## Maintenance

### Updating Tests

1. Edit [`gravitas.spec.ts`](e2e/gravitas.spec.ts)
2. Run tests locally to verify
3. Commit changes

### Adding New Tests

```typescript
test.describe('New Test Suite', () => {
  test('should...', async ({ page }) => {
    // Test implementation
  });
});
```

### Updating Playwright

```bash
npm update @playwright/test
npx playwright install
```

## Support

For issues or questions:
- Check [Playwright Documentation](https://playwright.dev/docs/intro)
- Review existing tests in [`gravitas.spec.ts`](e2e/gravitas.spec.ts)
- Check frontend logs in browser console

---

**Version**: 1.0.0  
**Last Updated**: 2026-03-28  
**Author**: Lead QA Automation Engineer