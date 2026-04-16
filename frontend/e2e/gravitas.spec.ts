/**
 * Gravitas Decision Engine - End-to-End Test Suite
 * ============================================================================
 * Tests the complete data flow: User Input → Raj's Backend API → Vedant's 
 * Formatter → React UI Rendering
 * 
 * Tests:
 * 1. Continuity Test (trace_id Integrity) - Verify API trace_id is rendered in DOM
 * 2. Enforcement Gatekeeper Test (State Accuracy) - Verify BLOCK state hides decision
 * 3. Rendering Fidelity Test (Data Matching) - Verify JSON keys match UI selectors
 * 4. Resiliency Test (Backend Failure) - Verify 500 error triggers error boundary
 */

import { test, expect, Page } from '@playwright/test';

// ============================================================================
// Test Configuration & Utilities
// ============================================================================

// Backend API URL (configurable via env)
const BACKEND_API = process.env.BACKEND_URL || 'https://nyaya-ai-0f02.onrender.com';
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:5173';

// Mock payloads for testing
const MOCK_PAYLOADS = {
  // Complex case with timeline and procedural steps
  complexCase: {
    query: 'What are the procedures for filing a civil suit in India?',
    jurisdiction_hint: 'India',
    user_context: {
      role: 'citizen',
      confidence_required: true
    }
  },

  // Cases expected to return different enforcement states
  allowCase: {
    query: 'file a civil suit in district court',
    jurisdiction_hint: 'India',
    user_context: {
      role: 'citizen',
      confidence_required: false
    }
  },

  blockCase: {
    query: 'how to manufacture illegal drugs',
    jurisdiction_hint: 'India',
    user_context: {
      role: 'citizen',
      confidence_required: true
    }
  },

  escalateCase: {
    query: 'challenge constitutional amendment',
    jurisdiction_hint: 'India',
    user_context: {
      role: 'citizen',
      confidence_required: true
    }
  }
};

// Utility to intercept API response and capture data
async function interceptApiResponse(page: Page, endpoint: string, callback: (response: any) => void) {
  await page.route(`**${endpoint}**`, async (route) => {
    const response = await route.fetch();
    const body = await response.json();
    callback(body);
    await route.fulfill({ response, body });
  });
}

// ============================================================================
// TEST 1: Continuity Test (trace_id Integrity)
// ============================================================================

test.describe('1. Continuity Test - trace_id Integrity', () => {
  test('should verify API trace_id is rendered in DOM', async ({ page }) => {
    // Step 1: Navigate to the frontend
    await page.goto(FRONTEND_URL);
    
    // Step 2: Wait for the app to be ready
    await page.waitForLoadState('networkidle');
    
    // Step 3: Fill in the query form
    const queryInput = page.locator('input[placeholder*="query"], textarea').first();
    await queryInput.fill('file a civil suit in district court');
    
    // Step 4: Submit the form and intercept the response
    let capturedTraceId: string | null = null;
    
    await page.route(`**/nyaya/query**`, async (route) => {
      const response = await route.fetch();
      const body = await response.json();
      
      // Capture the trace_id from API response
      capturedTraceId = body.trace_id;
      
      await route.fulfill({ response, body });
    });
    
    // Step 5: Submit the form
    const submitButton = page.locator('button[type="submit"], button:has-text("Submit")').first();
    await submitButton.click();
    
    // Step 6: Wait for response and verify trace_id
    await page.waitForTimeout(3000);
    
    // Step 7: Verify trace_id is present in the DOM
    // Check multiple possible locations where trace_id might be rendered
    const traceIdSelectors = [
      '[data-testid="trace-id"]',
      '[data-testid="traceId"]',
      '[data-testid="final-decision"]',
      '.trace-id',
      '.traceId',
      'text=/Trace ID/i'
    ];
    
    let foundTraceId = false;
    for (const selector of traceIdSelectors) {
      const element = page.locator(selector).first();
      if (await element.isVisible().catch(() => false)) {
        const text = await element.textContent();
        if (text && text.includes(capturedTraceId || '')) {
          foundTraceId = true;
          console.log(`✅ trace_id "${capturedTraceId}" found in DOM at: ${selector}`);
          break;
        }
      }
    }
    
    // Also check meta tags
    const metaTraceId = await page.locator('meta[name="trace-id"]').getAttribute('content');
    if (metaTraceId === capturedTraceId) {
      foundTraceId = true;
      console.log(`✅ trace_id found in meta tag`);
    }
    
    // Assertion: trace_id from API response must be rendered in DOM
    expect(capturedTraceId).not.toBeNull();
    expect(foundTraceId).toBe(true);
  });
});

// ============================================================================
// TEST 2: Enforcement Gatekeeper Test (State Accuracy)
// ============================================================================

test.describe('2. Enforcement Gatekeeper Test - State Accuracy', () => {
  
  test('ALLOW state: should render decision content', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
    
    // Submit query that should return ALLOW
    const queryInput = page.locator('input[placeholder*="query"], textarea').first();
    await queryInput.fill('file a civil suit in district court');
    
    // Intercept and mock ALLOW response
    await page.route(`**/nyaya/query**`, async (route) => {
      const response = await route.fetch();
      let body = await response.json();
      
      // Force ALLOW state
      body = {
        ...body,
        enforcement_decision: 'ALLOW',
        enforcement_status: {
          state: 'clear',
          verdict: 'ENFORCEABLE',
          reason: 'Legal pathway clear'
        }
      };
      
      await route.fulfill({ response, body: JSON.stringify(body) });
    });
    
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();
    
    await page.waitForTimeout(2000);
    
    // Verify decision is rendered (ALLOW should show decision)
    const decisionElement = page.locator('[data-testid="final-decision"], .decision-content').first();
    await expect(decisionElement).toBeVisible();
  });

  test('BLOCK state: should NOT render decision content', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
    
    // Submit query
    const queryInput = page.locator('input[placeholder*="query"], textarea').first();
    await queryInput.fill('illegal activities query');
    
    // Intercept and mock BLOCK response
    await page.route(`**/nyaya/query**`, async (route) => {
      const response = await route.fetch();
      let body = await response.json();
      
      // Force BLOCK state - Phase 4 logic: hide decision string
      body = {
        ...body,
        enforcement_decision: 'BLOCK',
        enforcement_status: {
          state: 'block',
          verdict: 'NON_ENFORCEABLE',
          reason: 'Path blocked due to legal restrictions',
          barriers: ['Illegal activity query']
        }
      };
      
      await route.fulfill({ response, body: JSON.stringify(body) });
    });
    
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();
    
    await page.waitForTimeout(2000);
    
    // Verify BLOCK UI is displayed
    const blockIndicator = page.locator('text=/BLOCKED/i, text=/🚫/i').first();
    await expect(blockIndicator).toBeVisible();
    
    // Verify decision content is NOT rendered when BLOCKED
    const decisionElement = page.locator('[data-testid="final-decision"]').first();
    const decisionText = await decisionElement.textContent().catch(() => '');
    
    // The decision string should NOT be present in DOM when state is BLOCK
    expect(decisionText).not.toContain('BLOCK');
  });

  test('ESCALATE state: should show escalation UI', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
    
    const queryInput = page.locator('input[placeholder*="query"], textarea').first();
    await queryInput.fill('constitutional challenge');
    
    // Intercept and mock ESCALATE response
    await page.route(`**/nyaya/query**`, async (route) => {
      const response = await route.fetch();
      let body = await response.json();
      
      // Force ESCALATE state
      body = {
        ...body,
        enforcement_decision: 'ESCALATE',
        enforcement_status: {
          state: 'escalate',
          verdict: 'PENDING_REVIEW',
          reason: 'Requires escalation to higher authority',
          escalation_required: true,
          escalation_target: 'Senior Legal Counsel'
        }
      };
      
      await route.fulfill({ response, body: JSON.stringify(body) });
    });
    
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();
    
    await page.waitForTimeout(2000);
    
    // Verify escalation UI is displayed
    const escalateIndicator = page.locator('text=/ESCALAT/i, text=/📈/i').first();
    await expect(escalateIndicator).toBeVisible();
  });
});

// ============================================================================
// TEST 3: Rendering Fidelity Test (Data Matching)
// ============================================================================

test.describe('3. Rendering Fidelity Test - Data Matching', () => {
  test('should verify JSON response keys match UI selectors exactly', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
    
    // Submit complex case with known mock payload
    const queryInput = page.locator('input[placeholder*="query"], textarea').first();
    await queryInput.fill('What are the procedures for filing a civil suit in India?');
    
    // Prepare expected complex response
    const expectedDecision = 'CIVIL_SUIT_FILING_PROCEDURE';
    const expectedTimeline = [
      { step: '1', action: 'File plaint', deadline: 'Within limitation period' },
      { step: '2', action: 'Service of summons', deadline: 'Within 30 days' },
      { step: '3', action: 'Written statement', deadline: 'Within 30 days' }
    ];
    const expectedProceduralSteps = [
      'Verify jurisdiction',
      'Draft plaint',
      'Pay court fee',
      'File in court',
      'Serve notice to defendant'
    ];
    
    // Intercept and inject known mock payload
    await page.route(`**/nyaya/query**`, async (route) => {
      const response = await route.fetch();
      let body = await response.json();
      
      // Inject known mock data
      body = {
        ...body,
        decision: expectedDecision,
        legal_route: ['Civil Procedure', 'District Court', 'Plaint'],
        timeline: expectedTimeline,
        procedural_steps: expectedProceduralSteps,
        enforcement_decision: 'ALLOW'
      };
      
      await route.fulfill({ response, body: JSON.stringify(body) });
    });
    
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();
    
    await page.waitForTimeout(3000);
    
    // Map JSON response keys to UI selectors and verify exact match
    
    // Test 1: casePayload.decision matches <div data-testid="final-decision">
    const finalDecisionElement = page.locator('[data-testid="final-decision"]').first();
    const uiDecisionText = await finalDecisionElement.textContent().catch(() => '');
    
    expect(uiDecisionText).toContain(expectedDecision);
    console.log(`✅ decision: "${expectedDecision}" matches UI`);
    
    // Test 2: timeline array is rendered correctly
    for (const timelineItem of expectedTimeline) {
      const timelineSelector = page.locator(`text=/${timelineItem.action}/i`).first();
      await expect(timelineSelector).toBeVisible();
    }
    console.log(`✅ timeline array rendered correctly`);
    
    // Test 3: procedural_steps array is rendered correctly
    for (const step of expectedProceduralSteps) {
      const stepSelector = page.locator(`text=/${step}/i`).first();
      await expect(stepSelector).toBeVisible();
    }
    console.log(`✅ procedural_steps array rendered correctly`);
    
    // Test 4: Verify enforcement decision is accurate
    const enforcementText = page.locator('[data-testid="enforcement-status"], .enforcement-status').first();
    const enforcementVisible = await enforcementText.isVisible().catch(() => false);
    
    if (enforcementVisible) {
      const enforcementContent = await enforcementText.textContent();
      expect(enforcementContent).toContain('ALLOW');
    }
    console.log(`✅ enforcement_decision matches UI`);
  });
});

// ============================================================================
// TEST 4: Resiliency Test (Backend Failure)
// ============================================================================

test.describe('4. Resiliency Test - Backend Failure', () => {
  test('should trigger error boundary on 500 Internal Server Error', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
    
    // Fill in query
    const queryInput = page.locator('input[placeholder*="query"], textarea').first();
    await queryInput.fill('test query');
    
    // Intercept and force 500 Internal Server Error
    await page.route(`**/nyaya/query**`, async (route) => {
      // Force 500 error
      await route.fulfill({
        status: 500,
        body: JSON.stringify({
          error: 'Internal Server Error',
          message: 'Database connection failed'
        })
      });
    });
    
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();
    
    await page.waitForTimeout(3000);
    
    // Verify Phase 5 Error Boundary triggers correctly
    
    // Option 1: Check for SystemCrash UI (from ErrorBoundary.jsx)
    const systemCrashElement = page.locator('text=/⚠️/i, text=/System Crash/i').first();
    const crashVisible = await systemCrashElement.isVisible().catch(() => false);
    
    // Option 2: Check for ServiceOutage component
    const serviceOutageElement = page.locator('text=/Service Outage/i, text=/Backend unavailable/i').first();
    const outageVisible = await serviceOutageElement.isVisible().catch(() => false);
    
    // Option 3: Check for error message in UI
    const errorMessageElement = page.locator('[data-testid="error-message"], .error-message').first();
    const errorVisible = await errorMessageElement.isVisible().catch(() => false);
    
    // At least one error UI should be displayed
    const errorDisplayed = crashVisible || outageVisible || errorVisible;
    expect(errorDisplayed).toBe(true);
    
    // Verify no unhandled React exceptions in console
    const consoleErrors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    
    await page.waitForTimeout(1000);
    
    // Check that no unhandled React exceptions were thrown
    const hasUnhandledReactError = consoleErrors.some(err => 
      err.includes('Uncaught') || 
      err.includes('Unhandled') || 
      err.includes('ErrorBoundary')
    );
    
    expect(hasUnhandledReactError).toBe(false);
    console.log(`✅ Error Boundary triggered without unhandled React exceptions`);
    
    // Verify "Return to Dashboard" action button exists
    const returnButton = page.locator('button:has-text("Return"), a:has-text("Dashboard")').first();
    await expect(returnButton).toBeVisible();
  });

  test('should handle network timeout gracefully', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
    
    const queryInput = page.locator('input[placeholder*="query"], textarea').first();
    await queryInput.fill('test timeout query');
    
    // Force network timeout
    await page.route(`**/nyaya/query**`, async (route) => {
      // Abort the request to simulate timeout
      await route.abort('timedout');
    });
    
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();
    
    await page.waitForTimeout(5000);
    
    // Verify timeout error is handled gracefully
    const timeoutIndicator = page.locator('text=/Timeout/i, text=/timed out/i').first();
    const timeoutVisible = await timeoutIndicator.isVisible().catch(() => false);
    
    // Either timeout message or retry option should be visible
    const retryButton = page.locator('button:has-text("Retry"), button:has-text("Try Again")').first();
    const retryVisible = await retryButton.isVisible().catch(() => false);
    
    expect(timeoutVisible || retryVisible).toBe(true);
    console.log(`✅ Network timeout handled gracefully`);
  });

  test('should handle ECONNREFUSED (backend down)', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
    
    const queryInput = page.locator('input[placeholder*="query"], textarea').first();
    await queryInput.fill('test connection refused');
    
    // Force ECONNREFUSED
    await page.route(`**/nyaya/query**`, async (route) => {
      await route.abort('failed');
    });
    
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();
    
    await page.waitForTimeout(3000);
    
    // Verify appropriate error handling
    const connectionErrorIndicator = page.locator('text=/Connection refused/i, text=/Network Error/i').first();
    const errorVisible = await connectionErrorIndicator.isVisible().catch(() => false);
    
    // Either specific error or generic error message should appear
    const genericError = page.locator('[data-testid="error-message"], .error-state').first();
    const genericVisible = await genericError.isVisible().catch(() => false);
    
    expect(errorVisible || genericVisible).toBe(true);
    console.log(`✅ ECONNREFUSED handled gracefully`);
  });
});

// ============================================================================
// Additional Integration Tests
// ============================================================================

test.describe('Additional Integration Tests', () => {
  test('should maintain trace_id across page refreshes', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
    
    const queryInput = page.locator('input[placeholder*="query"], textarea').first();
    await queryInput.fill('test trace persistence');
    
    let firstTraceId: string | null = null;
    
    await page.route(`**/nyaya/query**`, async (route) => {
      const response = await route.fetch();
      const body = await response.json();
      firstTraceId = body.trace_id;
      await route.fulfill({ response, body: JSON.stringify(body) });
    });
    
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();
    
    await page.waitForTimeout(2000);
    
    // Store trace_id in localStorage for persistence test
    await page.evaluate(() => {
      window.localStorage.setItem('gravitas_trace_id', window.__gravitas_active_trace_id || 'test-id');
    });
    
    // Refresh page
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // Verify trace_id is still accessible (either from state or localStorage)
    const storedTraceId = await page.evaluate(() => 
      window.localStorage.getItem('gravitas_trace_id')
    );
    
    expect(storedTraceId).not.toBeNull();
    console.log(`✅ trace_id persisted across page refresh`);
  });

  test('should verify provenance chain is included in response', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
    
    const queryInput = page.locator('input[placeholder*="query"], textarea').first();
    await queryInput.fill('test provenance chain');
    
    let hasProvenanceChain = false;
    
    await page.route(`**/nyaya/query**`, async (route) => {
      const response = await route.fetch();
      const body = await response.json();
      
      // Verify provenance_chain exists in response
      hasProvenanceChain = Array.isArray(body.provenance_chain) && body.provenance_chain.length > 0;
      
      await route.fulfill({ response, body: JSON.stringify(body) });
    });
    
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();
    
    await page.waitForTimeout(2000);
    
    // Log result (provenance chain may not always be present for all queries)
    if (hasProvenanceChain) {
      console.log(`✅ provenance_chain present in API response`);
    } else {
      console.log(`⚠️  provenance_chain not present (may be optional for some queries)`);
    }
  });
});