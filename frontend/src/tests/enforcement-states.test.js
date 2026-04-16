/**
 * Enforcement States Test Suite - DAY 2
 * 
 * Tests all enforcement states:
 * - ALLOW (green, #28a745) - ✅ Decision allowed
 * - BLOCK (red, #dc3545) - 🚫 Pathway blocked
 * - ESCALATE (orange, #fd7e14) - 📈 Escalation required
 * - SAFE_REDIRECT (purple, #6f42c1) - ↩️ Suggested redirect
 * 
 * Ensures proper rendering of each state with correct colors, labels, and UI behavior
 */

// Mock decision data for each enforcement state
export const MOCK_DECISIONS = {
  ALLOW: {
    domain: 'civil_litigation',
    jurisdiction: 'IN',
    jurisdiction_detected: 'India',
    confidence: {
      overall: 0.95,
      legal: 0.92,
      procedural: 0.97,
      evidential: 0.90
    },
    enforcement_decision: 'ALLOW',
    reasoning_trace: {
      legal_analysis: 'The pathway for civil litigation is clearly established under Indian law. All procedural requirements are met.',
      procedural_steps: ['File claim at district court', 'Pay court fees', 'Serve notice to defendant', 'Wait for response', 'Proceed to trial']
    },
    legal_route: ['File at District Court', 'Prepare case', 'Present evidence', 'Await judgment'],
    procedural_steps: 'File claim at district court | Pay court fees | Serve notice to defendant | Wait for response | Proceed to trial',
    timeline: [
      { step: 'Filing Stage', eta: '1-2 weeks' },
      { step: 'Court Assignment', eta: '2-4 weeks' },
      { step: 'Pre-trial', eta: '1-3 months' },
      { step: 'Trial', eta: '6-12 months' }
    ],
    evidence_requirements: [
      'Original contract or agreement',
      'Correspondence with opposing party',
      'Legal documents related to dispute',
      'Witness statements'
    ],
    remedies: ['Monetary compensation', 'Specific performance', 'Injunction'],
    provenance_chain: [
      {
        timestamp: '2026-03-04T10:00:00Z',
        action: 'Legal domain detection',
        confidence: 0.98
      },
      {
        timestamp: '2026-03-04T10:00:01Z',
        action: 'Jurisdiction verification',
        confidence: 0.96
      },
      {
        timestamp: '2026-03-04T10:00:02Z',
        action: 'Enforcement state determination',
        confidence: 0.95
      }
    ],
    trace_id: 'ALLOW-001-2026-03-04'
  },

  BLOCK: {
    domain: 'criminal_matter',
    jurisdiction: 'IN',
    jurisdiction_detected: 'India',
    confidence: {
      overall: 0.88,
      legal: 0.90,
      procedural: 0.85,
      evidential: 0.88
    },
    enforcement_decision: 'BLOCK',
    reasoning_trace: {
      legal_analysis: 'This matter falls under criminal jurisdiction and cannot be pursued through civil courts. Referral to law enforcement is required.',
      procedural_steps: ['Contact local police', 'File FIR (First Information Report)', 'Provide evidence to investigating officer', 'Cooperate with investigation']
    },
    legal_route: ['Approach Police Station', 'File FIR', 'Investigation', 'Prosecution'],
    procedural_steps: 'Contact local police | File FIR (First Information Report) | Provide evidence to investigating officer | Cooperate with investigation',
    timeline: [
      { step: 'Police Registration', eta: '1-3 days' },
      { step: 'Investigation Phase', eta: '1-3 months' },
      { step: 'Chargesheet Filing', eta: '90 days to 6 months' }
    ],
    evidence_requirements: [
      'Police FIR',
      'Medical/forensic reports',
      'Witness statements',
      'Documentary evidence'
    ],
    remedies: ['Criminal prosecution', 'Restitution if convicted'],
    provenance_chain: [
      {
        timestamp: '2026-03-04T10:05:00Z',
        action: 'Matter type classification',
        confidence: 0.92
      },
      {
        timestamp: '2026-03-04T10:05:01Z',
        action: 'Criminal domain detection',
        confidence: 0.90
      }
    ],
    trace_id: 'BLOCK-001-2026-03-04'
  },

  ESCALATE: {
    domain: 'complex_commercial',
    jurisdiction: 'UAE',
    jurisdiction_detected: 'United Arab Emirates',
    confidence: {
      overall: 0.72,
      legal: 0.75,
      procedural: 0.70,
      evidential: 0.68
    },
    enforcement_decision: 'ESCALATE',
    reasoning_trace: {
      legal_analysis: 'This complex multinational commercial dispute requires expert legal review and potentially international arbitration. Escalation to senior legal counsel recommended.',
      procedural_steps: ['Consult international trade lawyer', 'Review arbitration clauses', 'Notify dispute resolution provider', 'Initiate arbitration proceedings']
    },
    legal_route: ['Legal Consultation', 'Arbitration', 'Expert Review', 'International Proceedings'],
    procedural_steps: 'Consult international trade lawyer | Review arbitration clauses | Notify dispute resolution provider | Initiate arbitration proceedings',
    timeline: [
      { step: 'Expert Consultation', eta: '1-2 weeks' },
      { step: 'Arbitration Initiation', eta: '2-4 weeks' },
      { step: 'Hearing Phase', eta: '2-6 months' },
      { step: 'Award', eta: '1-3 months' }
    ],
    evidence_requirements: [
      'International contracts',
      'Trade documentation',
      'Financial records',
      'Expert reports'
    ],
    remedies: ['Arbitration award', 'Damages', 'Specific performance'],
    provenance_chain: [
      {
        timestamp: '2026-03-04T10:10:00Z',
        action: 'Matter complexity assessment',
        confidence: 0.80
      },
      {
        timestamp: '2026-03-04T10:10:02Z',
        action: 'Escalation criteria met',
        confidence: 0.72
      }
    ],
    trace_id: 'ESCALATE-001-2026-03-04'
  },

  SAFE_REDIRECT: {
    domain: 'administrative_appeal',
    jurisdiction: 'UK',
    jurisdiction_detected: 'United Kingdom',
    confidence: {
      overall: 0.85,
      legal: 0.87,
      procedural: 0.83,
      evidential: 0.85
    },
    enforcement_decision: 'SAFE_REDIRECT',
    reasoning_trace: {
      legal_analysis: 'This matter should be redirected to the appropriate administrative tribunal for more efficient resolution. However, civil courts can also handle it if preferred.',
      procedural_steps: ['Apply to administrative tribunal', 'Gather administrative documents', 'Prepare written submissions', 'Attend tribunal hearing']
    },
    legal_route: ['Administrative Tribunal', 'Judicial Review', 'Appeal', 'Resolution'],
    procedural_steps: 'Apply to administrative tribunal | Gather administrative documents | Prepare written submissions | Attend tribunal hearing',
    timeline: [
      { step: 'Application Stage', eta: '2-4 weeks' },
      { step: 'Tribunal Review', eta: '3-6 months' },
      { step: 'Hearing', eta: '1-2 months' },
      { step: 'Decision', eta: '2-4 weeks' }
    ],
    evidence_requirements: [
      'Administrative decision records',
      'Correspondence with authority',
      'Supporting documentation',
      'Legal authority references'
    ],
    remedies: ['Decision reversal', 'Mandatory order', 'Damages for procedural unfairness'],
    provenance_chain: [
      {
        timestamp: '2026-03-04T10:15:00Z',
        action: 'Jurisdiction analysis',
        confidence: 0.91
      },
      {
        timestamp: '2026-03-04T10:15:01Z',
        action: 'Optimal pathway determination',
        confidence: 0.85
      }
    ],
    trace_id: 'SAFE_REDIRECT-001-2026-03-04'
  }
}

/**
 * Test Suite 1: Enforcement Color Mapping
 */
export const TEST_ENFORCEMENT_COLORS = {
  test1: {
    name: 'ALLOW state returns green (#28a745)',
    state: 'ALLOW',
    expectedColor: '#28a745',
    description: 'User sees green color for allowed pathways'
  },
  test2: {
    name: 'BLOCK state returns red (#dc3545)',
    state: 'BLOCK',
    expectedColor: '#dc3545',
    description: 'User sees red color for blocked pathways - clear refusal'
  },
  test3: {
    name: 'ESCALATE state returns orange (#fd7e14)',
    state: 'ESCALATE',
    expectedColor: '#fd7e14',
    description: 'User sees orange color for escalation required'
  },
  test4: {
    name: 'SAFE_REDIRECT state returns purple (#6f42c1)',
    state: 'SAFE_REDIRECT',
    expectedColor: '#6f42c1',
    description: 'User sees purple color for safe redirects'
  }
}

/**
 * Test Suite 2: Enforcement Label Mapping
 */
export const TEST_ENFORCEMENT_LABELS = {
  test5: {
    name: 'ALLOW state shows ✅ ALLOWED',
    state: 'ALLOW',
    expectedLabel: '✅ ALLOWED',
    description: 'Clear confirmation that action is allowed'
  },
  test6: {
    name: 'BLOCK state shows 🚫 BLOCKED',
    state: 'BLOCK',
    expectedLabel: '🚫 BLOCKED',
    description: 'Clear indication that action is blocked by authority'
  },
  test7: {
    name: 'ESCALATE state shows 📈 ESCALATION REQUIRED',
    state: 'ESCALATE',
    expectedLabel: '📈 ESCALATION REQUIRED',
    description: 'Clear indication that escalation is needed'
  },
  test8: {
    name: 'SAFE_REDIRECT state shows ↩️ SAFE REDIRECT',
    state: 'SAFE_REDIRECT',
    expectedLabel: '↩️ SAFE REDIRECT',
    description: 'Alternative pathway suggested'
  }
}

/**
 * Test Suite 3: ALLOW State Rendering
 */
export const TEST_ALLOW_STATE = {
  test9: {
    name: 'ALLOW decision displays with correct enforcement banner color (green)',
    expectation: 'Banner shows #28a745 with ✅ ALLOWED label',
    scenario: 'User submits civil litigation query'
  },
  test10: {
    name: 'ALLOW decision shows high confidence (95%)',
    expectation: 'Confidence breakdown shows 0.95',
    scenario: 'User views confidence metrics'
  },
  test11: {
    name: 'ALLOW decision lists legal route (4 steps)',
    expectation: 'Legal route shows: File at District Court → Prepare case → Present evidence → Await judgment',
    scenario: 'User expands legal route section'
  },
  test12: {
    name: 'ALLOW decision shows procedural steps clearly',
    expectation: '5 procedural steps rendered as ordered list',
    scenario: 'User views procedural requirements'
  }
}

/**
 * Test Suite 4: BLOCK State Rendering (Critical)
 */
export const TEST_BLOCK_STATE = {
  test13: {
    name: 'BLOCK decision displays with correct enforcement banner color (red)',
    expectation: 'Banner shows #dc3545 with 🚫 BLOCKED label',
    scenario: 'User submits criminal matter query',
    critical: true
  },
  test14: {
    name: 'BLOCK state clearly shows refusal authority',
    expectation: 'Message indicates "cannot be pursued through civil courts" and "referral to law enforcement required"',
    scenario: 'User reads legal analysis of BLOCK decision',
    critical: true
  },
  test15: {
    name: 'BLOCK decision redirects to law enforcement pathway',
    expectation: 'Legal route shows: Approach Police Station → File FIR → Investigation → Prosecution',
    scenario: 'User views suggested alternative pathway',
    critical: true
  },
  test16: {
    name: 'BLOCK decision shows specific next steps',
    expectation: 'Procedural steps show: Contact police, File FIR, Provide evidence',
    scenario: 'User follows BLOCK decision instructions',
    critical: true
  }
}

/**
 * Test Suite 5: ESCALATE State Rendering
 */
export const TEST_ESCALATE_STATE = {
  test17: {
    name: 'ESCALATE decision displays with correct enforcement banner color (orange)',
    expectation: 'Banner shows #fd7e14 with 📈 ESCALATION REQUIRED label',
    scenario: 'User submits complex commercial dispute query'
  },
  test18: {
    name: 'ESCALATE state shows lower confidence (72%)',
    expectation: 'Confidence breakdown shows 0.72 with component breakdowns',
    scenario: 'User views confidence metrics'
  },
  test19: {
    name: 'ESCALATE decision shows expert consultation requirement',
    expectation: 'Legal analysis mentions "expert legal review" and "senior legal counsel recommended"',
    scenario: 'User reads reason for escalation'
  },
  test20: {
    name: 'ESCALATE decision involves arbitration pathway',
    expectation: 'Legal route includes: Legal Consultation → Arbitration → Expert Review → International Proceedings',
    scenario: 'User views escalation pathway'
  }
}

/**
 * Test Suite 6: SAFE_REDIRECT State Rendering
 */
export const TEST_SAFE_REDIRECT_STATE = {
  test21: {
    name: 'SAFE_REDIRECT decision displays with correct enforcement banner color (purple)',
    expectation: 'Banner shows #6f42c1 with ↩️ SAFE REDIRECT label',
    scenario: 'User submits administrative appeal query'
  },
  test22: {
    name: 'SAFE_REDIRECT state suggests administrative tribunal',
    expectation: 'Legal analysis mentions "redirect to administrative tribunal for more efficient resolution"',
    scenario: 'User reads recommendation'
  },
  test23: {
    name: 'SAFE_REDIRECT preserves civil court option',
    expectation: 'Note indicates "civil courts can also handle it if preferred"',
    scenario: 'User sees flexibility of recommendation'
  },
  test24: {
    name: 'SAFE_REDIRECT shows optimal pathway with timeframes',
    expectation: 'Timeline shows: Application (2-4 weeks) → Review (3-6 months) → Hearing (1-2 months)',
    scenario: 'User plans timeline'
  }
}

/**
 * Test Suite 7: Error Handling - No Silent Failures
 */
export const TEST_ERROR_HANDLING = {
  test25: {
    name: 'Empty query shows error message',
    expectation: 'Error message: "Please enter a legal query"',
    scenario: 'User clicks submit with empty text'
  },
  test26: {
    name: 'Backend connection failure shows user message',
    expectation: 'Error message: "Failed to fetch decision. Please try again."',
    scenario: 'Backend is unreachable'
  },
  test27: {
    name: 'Invalid response data shows error',
    expectation: 'Error message from backend or fallback message shown',
    scenario: 'Backend returns invalid JSON'
  },
  test28: {
    name: 'Network timeout shows specific error',
    expectation: 'User sees: "Request timeout. Backend server may be down."',
    scenario: 'API call exceeds 30 second timeout'
  }
}

/**
 * Test Suite 8: Real Backend Integration
 */
export const TEST_BACKEND_INTEGRATION = {
  test29: {
    name: 'Test backend connection',
    endpoint: 'https://nyaya-ai-0f02.onrender.com/health',
    expectedStatus: 200,
    description: 'Backend should respond to health check'
  },
  test30: {
    name: 'Query endpoint returns enforcement_decision field',
    endpoint: 'https://nyaya-ai-0f02.onrender.com/nyaya/query',
    expectedField: 'enforcement_decision',
    description: 'Response must include enforcement_decision to render correctly'
  },
  test31: {
    name: 'Response includes all required fields',
    requiredFields: [
      'domain',
      'jurisdiction',
      'confidence',
      'enforcement_decision',
      'reasoning_trace',
      'legal_route',
      'procedural_steps',
      'timeline',
      'evidence_requirements',
      'remedies',
      'provenance_chain',
      'trace_id'
    ],
    description: 'All fields needed for DecisionPage rendering'
  }
}

/**
 * DAY 2 Test Execution Report Template
 */
export const DAY2_TEST_REPORT = {
  date: '2026-03-04',
  phase: 'DAY 2 - Backend Integration & Enforcement Testing',
  totalTests: 31,
  categories: {
    colorMapping: { tests: 4, name: 'Color Mapping' },
    labelMapping: { tests: 4, name: 'Label Mapping' },
    allowState: { tests: 4, name: 'ALLOW State' },
    blockState: { tests: 4, name: 'BLOCK State (Critical)' },
    escalateState: { tests: 4, name: 'ESCALATE State' },
    redirectState: { tests: 4, name: 'SAFE_REDIRECT State' },
    errorHandling: { tests: 4, name: 'Error Handling' },
    backendIntegration: { tests: 3, name: 'Real Backend' }
  },
  executionNotes: [
    'All enforcement states must render with correct colors and labels',
    'BLOCK state is critical - must clearly show refusal authority',
    'No silent failures allowed - all errors must display to user',
    'Real backend responses must map correctly to UI components',
    'Timeout must be handled gracefully (30 second limit)',
    'Empty query validation must prevent submission'
  ]
}

export default {
  MOCK_DECISIONS,
  TEST_ENFORCEMENT_COLORS,
  TEST_ENFORCEMENT_LABELS,
  TEST_ALLOW_STATE,
  TEST_BLOCK_STATE,
  TEST_ESCALATE_STATE,
  TEST_SAFE_REDIRECT_STATE,
  TEST_ERROR_HANDLING,
  TEST_BACKEND_INTEGRATION,
  DAY2_TEST_REPORT
}
