/**
 * Backend Integration Tests — Recommendation Model
 */

const VALID_RECOMMENDATION_TYPES = ['INFORM', 'REVIEW', 'ESCALATE', 'INSUFFICIENT_DATA']

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
  runAllTests
}
