/**
 * Recommendation States Test Suite
 *
 * Tests all advisory recommendation types:
 * - INFORM (informational guidance)
 * - REVIEW (additional review recommended)
 * - ESCALATE (consult legal professional)
 * - INSUFFICIENT_DATA (cannot provide reliable guidance)
 */

export const MOCK_DECISIONS = {
  INFORM: {
    domain: 'civil_litigation',
    jurisdiction: 'IN',
    jurisdiction_detected: 'India',
    confidence: {
      overall: 0.95,
      jurisdiction: 0.92,
      domain: 0.97,
      statute_match: 0.90,
      procedural_match: 0.97
    },
    recommendation: {
      type: 'INFORM',
      confidence: 0.95,
      rationale: 'Query resolved with high confidence statutory matches.'
    },
    reasoning_trace: {
      legal_analysis: 'The pathway for civil litigation is clearly established under Indian law.',
      procedural_steps: ['File claim at district court', 'Pay court fees', 'Serve notice to defendant']
    },
    legal_route: ['File at District Court', 'Prepare case', 'Present evidence'],
    trace_id: 'INFORM-001-2026-03-04'
  },

  REVIEW: {
    domain: 'criminal_matter',
    jurisdiction: 'IN',
    jurisdiction_detected: 'India',
    confidence: {
      overall: 0.55,
      jurisdiction: 0.45,
      domain: 0.70,
      statute_match: 0.60,
      procedural_match: 0.50
    },
    recommendation: {
      type: 'REVIEW',
      confidence: 0.55,
      rationale: 'Statutes found but jurisdiction confidence is low — additional review recommended.'
    },
    reasoning_trace: {
      legal_analysis: 'Statutes matched but jurisdiction detection confidence is below threshold.',
      procedural_steps: ['Verify jurisdiction', 'Consult local counsel']
    },
    legal_route: ['Verify Jurisdiction', 'Review Statutes'],
    trace_id: 'REVIEW-001-2026-03-04'
  },

  ESCALATE: {
    domain: 'constitutional',
    jurisdiction: 'IN',
    jurisdiction_detected: 'India',
    confidence: {
      overall: 0.40,
      jurisdiction: 0.60,
      domain: 0.35,
      statute_match: 0.20,
      procedural_match: 0.45
    },
    recommendation: {
      type: 'ESCALATE',
      confidence: 0.40,
      rationale: 'No statutes matched — consider consulting a legal professional.'
    },
    reasoning_trace: {
      legal_analysis: 'Complex constitutional matter requiring specialist review.',
      procedural_steps: ['Consult constitutional lawyer', 'Gather supporting documents']
    },
    legal_route: ['Specialist Consultation'],
    trace_id: 'ESCALATE-001-2026-03-04'
  },

  INSUFFICIENT_DATA: {
    domain: 'general',
    jurisdiction: 'IN',
    jurisdiction_detected: 'India',
    confidence: {
      overall: 0.15,
      jurisdiction: 0.20,
      domain: 0.10,
      statute_match: 0.05,
      procedural_match: 0.15
    },
    recommendation: {
      type: 'INSUFFICIENT_DATA',
      confidence: 0.15,
      rationale: 'Insufficient data to provide reliable legal guidance.'
    },
    reasoning_trace: {
      legal_analysis: 'Query too vague to match specific statutory provisions.',
      procedural_steps: []
    },
    legal_route: [],
    trace_id: 'INSUFFICIENT-001-2026-03-04'
  }
}

export const TEST_RECOMMENDATION_TYPES = {
  test1: {
    name: 'INFORM type renders informational guidance',
    type: 'INFORM',
    expectation: 'Full document view with no advisory banner'
  },
  test2: {
    name: 'REVIEW type shows review banner',
    type: 'REVIEW',
    expectation: 'Document view with review notice banner'
  },
  test3: {
    name: 'ESCALATE type shows escalation banner',
    type: 'ESCALATE',
    expectation: 'Document view with escalation notice banner'
  },
  test4: {
    name: 'INSUFFICIENT_DATA shows clarification request',
    type: 'INSUFFICIENT_DATA',
    expectation: 'Reduced view with clarification request'
  }
}

export const TEST_BACKEND_INTEGRATION = {
  test5: {
    name: 'Query endpoint returns recommendation field',
    endpoint: '/nyaya/query',
    expectedField: 'recommendation',
    description: 'Response must include recommendation.type to render correctly'
  },
  test6: {
    name: 'Response includes all required TANTRA fields',
    requiredFields: [
      'domain',
      'jurisdiction',
      'confidence',
      'recommendation',
      'trace_id',
      'request_id',
      'input_hash',
      'determinism_proof',
      'timestamp',
      'facts',
      'analysis',
      'explanation_chain',
      'risk_flags',
      'legal_context'
    ],
    description: 'All fields needed for advisory document rendering'
  }
}

export const DAY2_TEST_REPORT = {
  date: '2026-06-11',
  phase: 'TANTRA Convergence — Recommendation Testing',
  totalTests: 6,
  categories: {
    recommendationTypes: { tests: 4, name: 'Recommendation Types' },
    backendIntegration: { tests: 2, name: 'Backend Integration' }
  },
  executionNotes: [
    'All recommendation types must render with correct advisory labels',
    'No content withholding — advisory only model',
    'Backend responses must include recommendation.type for advisory rendering'
  ]
}

export default {
  MOCK_DECISIONS,
  TEST_RECOMMENDATION_TYPES,
  TEST_BACKEND_INTEGRATION,
  DAY2_TEST_REPORT
}
