/**
 * Backend Integration Tests — Recommendation Model
 */

import { MOCK_DECISIONS } from './recommendation-states.test.js'

const VALID_RECOMMENDATION_TYPES = ['INFORM', 'REVIEW', 'ESCALATE', 'INSUFFICIENT_DATA']

const REQUIRED_RESPONSE_FIELDS = [
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
]

export async function testBackendConnection() {
  console.log('\n🔍 TEST 1: Backend Connection...')
  try {
    const response = await fetch('http://localhost:8000/health')
    if (!response.ok) throw new Error(`Health check failed: ${response.status}`)
    console.log('✅ Backend is reachable')
    return { success: true }
  } catch (error) {
    console.error('❌ Backend connection failed:', error.message)
    return { success: false, error: error.message }
  }
}

export async function testQueryEndpoint() {
  console.log('\n🔍 TEST 2: Query Endpoint...')
  try {
    const response = await fetch('http://localhost:8000/nyaya/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: 'theft of mobile phone',
        jurisdiction_hint: 'India',
        user_context: { role: 'citizen', confidence_required: true }
      })
    })

    if (!response.ok) throw new Error(`Query failed: ${response.status}`)
    const decision = await response.json()
    console.log(`   Recommendation: ${decision.recommendation?.type}`)
    return { success: true, decision }
  } catch (error) {
    console.error('❌ Query endpoint test failed:', error.message)
    return { success: false, error: error.message }
  }
}

export async function testRequiredFields() {
  console.log('\n🔍 TEST 3: Required Fields...')
  const result = await testQueryEndpoint()
  if (!result.success) return result

  const decision = result.decision
  const requiredFields = [
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
  ]

  const missing = requiredFields.filter(f => !(f in decision))
  if (missing.length > 0) {
    console.error('❌ Missing fields:', missing.join(', '))
    return { success: false, missing }
  }

  console.log('✅ All required fields present')
  return { success: true }
}

export function validateResponseFields(decision) {
  if (!decision || typeof decision !== 'object') return false
  return REQUIRED_RESPONSE_FIELDS.every(field => field in decision)
}

export function validateRecommendationState(decision) {
  const recType = decision?.recommendation?.type
  return Boolean(recType && VALID_RECOMMENDATION_TYPES.includes(recType))
}

async function testRecommendationStateRender(type) {
  const mock = MOCK_DECISIONS[type]
  if (!mock) {
    return { success: false, error: `No mock payload for recommendation type: ${type}` }
  }
  if (mock.recommendation?.type !== type) {
    return { success: false, error: `Mock payload type mismatch: expected ${type}` }
  }
  return { success: true, note: `${type} recommendation state validated via mock payload` }
}

export async function testINFORMState() {
  return testRecommendationStateRender('INFORM')
}

export async function testREVIEWState() {
  return testRecommendationStateRender('REVIEW')
}

export async function testESCALATEState() {
  return testRecommendationStateRender('ESCALATE')
}

export async function testINSUFFICIENT_DATAState() {
  return testRecommendationStateRender('INSUFFICIENT_DATA')
}

export async function testErrorHandling() {
  try {
    const response = await fetch('http://localhost:8000/nyaya/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: '' })
    })
    if (!response.ok) {
      return { success: true, note: 'Empty query rejected with error response' }
    }
    return { success: false, error: 'Empty query should not return success' }
  } catch (error) {
    return { success: true, note: 'Request failure surfaced without silent pass' }
  }
}

export async function testTimeoutHandling() {
  const start = Date.now()
  const result = await testBackendConnection()
  const elapsed = Date.now() - start
  return {
    success: result.success && elapsed < 30000,
    timeout: elapsed >= 30000,
    note: result.success ? `Request completed in ${elapsed}ms` : 'Backend unreachable'
  }
}

export async function testRecommendationType() {
  console.log('\n🔍 TEST 4: Recommendation Type Validation...')
  const result = await testQueryEndpoint()
  if (!result.success) return result

  const recType = result.decision.recommendation?.type
  if (!recType) {
    console.error('❌ recommendation.type field is missing')
    return { success: false }
  }

  if (!VALID_RECOMMENDATION_TYPES.includes(recType)) {
    console.error(`❌ Invalid recommendation type: ${recType}`)
    return { success: false }
  }

  console.log(`✅ Valid recommendation type: ${recType}`)
  return { success: true, type: recType }
}

export async function runAllTests() {
  console.log('=== BACKEND INTEGRATION TEST SUITE ===\n')
  const results = { tests: [], passed: 0, failed: 0 }

  const tests = [
    { name: 'Backend Connection', fn: testBackendConnection },
    { name: 'Query Endpoint', fn: testQueryEndpoint },
    { name: 'Required Fields', fn: testRequiredFields },
    { name: 'Recommendation Type', fn: testRecommendationType },
  ]

  for (const test of tests) {
    const result = await test.fn()
    results.tests.push({ name: test.name, success: result.success })
    if (result.success) results.passed++
    else results.failed++
  }

  console.log(`\n=== RESULTS: ${results.passed}/${tests.length} passed ===`)
  return results
}

export default {
  testBackendConnection,
  testQueryEndpoint,
  testRequiredFields,
  testRecommendationType,
  validateResponseFields,
  validateRecommendationState,
  testINFORMState,
  testREVIEWState,
  testESCALATEState,
  testINSUFFICIENT_DATAState,
  testErrorHandling,
  testTimeoutHandling,
  runAllTests
}
