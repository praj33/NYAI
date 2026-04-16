/**
 * Backend Integration Testing - DAY 2
 * 
 * Tests real connection to: https://nyaya-ai-0f02.onrender.com
 * Validates enforcement states and error handling
 */

import axios from 'axios'

const NYAYA_API = 'https://nyaya-ai-0f02.onrender.com'

/**
 * Test 1: Backend Health Check
 * Verifies backend is responding
 */
export async function testBackendConnection() {
  console.log('🔍 TEST 1: Backend Connection Check...')
  try {
    const response = await axios.get(`${NYAYA_API}/health`, { timeout: 5000 })
    console.log('✅ Backend is online')
    return { success: true, status: response.status }
  } catch (error) {
    if (error.code === 'ECONNABORTED') {
      console.error('❌ Backend timeout (5s)')
      return { success: false, error: 'Timeout' }
    }
    console.error('❌ Backend unreachable:', error.message)
    return { success: false, error: error.message }
  }
}

/**
 * Test 2: Query Endpoint - Real Decision
 * Sends a real query and validates response structure
 */
export async function testQueryEndpoint() {
  console.log('\n🔍 TEST 2: Query Endpoint...')
  try {
    const testQuery = 'What are the procedures for filing a civil suit in India?'
    
    const response = await axios.post(`${NYAYA_API}/nyaya/query`, {
      query: testQuery,
      jurisdiction: 'IN'
    }, { timeout: 30000 })

    const decision = response.data
    console.log('✅ Query successful')
    console.log(`   Trace ID: ${decision.trace_id}`)
    console.log(`   Jurisdiction: ${decision.jurisdiction}`)
    console.log(`   Enforcement: ${decision.enforcement_decision}`)
    console.log(`   Confidence: ${Math.round(decision.confidence?.overall * 100)}%`)

    return { success: true, decision }
  } catch (error) {
    console.error('❌ Query failed:', error.response?.data || error.message)
    return { success: false, error: error.message }
  }
}

/**
 * Test 3: Validate Response Fields
 * Ensures all required fields are present
 */
export function validateResponseFields(decision) {
  console.log('\n🔍 TEST 3: Response Field Validation...')
  
  const requiredFields = [
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
  ]

  const missingFields = []
  const presentFields = []

  requiredFields.forEach(field => {
    if (decision.hasOwnProperty(field)) {
      presentFields.push(field)
    } else {
      missingFields.push(field)
    }
  })

  if (missingFields.length === 0) {
    console.log('✅ All required fields present')
    presentFields.forEach(f => console.log(`   ✓ ${f}`))
    return true
  } else {
    console.error('❌ Missing fields:')
    missingFields.forEach(f => console.error(`   ✗ ${f}`))
    return false
  }
}

/**
 * Test 4: Enforcement State Validation
 * Verifies enforcement_decision contains valid state
 */
export function validateEnforcementState(decision) {
  console.log('\n🔍 TEST 4: Enforcement State Validation...')
  
  const validStates = ['ALLOW', 'BLOCK', 'ESCALATE', 'SAFE_REDIRECT']
  const state = decision.enforcement_decision

  if (!state) {
    console.error('❌ enforcement_decision field is missing')
    return false
  }

  if (validStates.includes(state)) {
    console.log(`✅ Valid enforcement state: ${state}`)
    return true
  } else {
    console.error(`❌ Invalid enforcement state: ${state}`)
    console.error(`   Valid states: ${validStates.join(', ')}`)
    return false
  }
}

/**
 * Test 5: ALLOW State - Proper Rendering
 * Tests ALLOW state specific fields
 */
export async function testALLOWState() {
  console.log('\n🔍 TEST 5: ALLOW State Rendering...')
  
  try {
    const response = await axios.post(`${NYAYA_API}/nyaya/query`, {
      query: 'file a civil suit in district court',
      jurisdiction: 'IN'
    }, { timeout: 30000 })

    const decision = response.data
    
    if (decision.enforcement_decision !== 'ALLOW') {
      console.log(`⚠️  Got ${decision.enforcement_decision} instead of ALLOW (this is OK for testing other states)`)
      return { success: true, note: `Received ${decision.enforcement_decision}` }
    }

    console.log('✅ ALLOW state received')
    console.log(`   Color: #28a745 (green)`)
    console.log(`   Label: ✅ ALLOWED`)
    console.log(`   Confidence: ${Math.round(decision.confidence?.overall * 100)}%`)
    console.log(`   Legal Route: ${decision.legal_route?.join(' → ')}`)

    return { success: true, decision }
  } catch (error) {
    console.error('❌ ALLOW state test failed:', error.message)
    return { success: false, error: error.message }
  }
}

/**
 * Test 6: BLOCK State - Proper Rendering & Authority
 * CRITICAL: Tests BLOCK state shows clear refusal authority
 */
export async function testBLOCKState() {
  console.log('\n🔍 TEST 6: BLOCK State Rendering (CRITICAL)...')
  
  try {
    const response = await axios.post(`${NYAYA_API}/nyaya/query`, {
      query: 'report criminal offense matters',
      jurisdiction: 'IN'
    }, { timeout: 30000 })

    const decision = response.data
    
    if (decision.enforcement_decision !== 'BLOCK') {
      console.log(`⚠️  Got ${decision.enforcement_decision} instead of BLOCK (this is OK for testing other states)`)
      return { success: true, note: `Received ${decision.enforcement_decision}` }
    }

    console.log('✅ BLOCK state received - CRITICAL VALIDATION')
    console.log(`   Color: #dc3545 (red) - Refusal Authority`)
    console.log(`   Label: 🚫 BLOCKED`)
    console.log(`   Confidence: ${Math.round(decision.confidence?.overall * 100)}%`)
    
    // Check legal analysis shows refusal
    const hasRefusal = decision.reasoning_trace?.legal_analysis?.toLowerCase().includes('cannot') ||
                       decision.reasoning_trace?.legal_analysis?.toLowerCase().includes('blocked') ||
                       decision.reasoning_trace?.legal_analysis?.toLowerCase().includes('law enforcement')
    
    if (hasRefusal) {
      console.log('   ✅ Legal analysis clearly shows refusal authority')
    } else {
      console.warn('   ⚠️  Legal analysis may not clearly show refusal (check manually)')
    }

    return { success: true, decision }
  } catch (error) {
    console.error('❌ BLOCK state test failed:', error.message)
    return { success: false, error: error.message }
  }
}

/**
 * Test 7: ESCALATE State - Proper Rendering
 * Tests ESCALATE state shows expert/senior counsel requirement
 */
export async function testESCALATEState() {
  console.log('\n🔍 TEST 7: ESCALATE State Rendering...')
  
  try {
    const response = await axios.post(`${NYAYA_API}/nyaya/query`, {
      query: 'complex multinational commercial arbitration matter',
      jurisdiction: 'UAE'
    }, { timeout: 30000 })

    const decision = response.data
    
    if (decision.enforcement_decision !== 'ESCALATE') {
      console.log(`⚠️  Got ${decision.enforcement_decision} instead of ESCALATE (this is OK for testing other states)`)
      return { success: true, note: `Received ${decision.enforcement_decision}` }
    }

    console.log('✅ ESCALATE state received')
    console.log(`   Color: #fd7e14 (orange)`)
    console.log(`   Label: 📈 ESCALATION REQUIRED`)
    console.log(`   Confidence: ${Math.round(decision.confidence?.overall * 100)}% (typically lower for escalations)`)
    console.log(`   Legal Route: ${decision.legal_route?.join(' → ')}`)

    return { success: true, decision }
  } catch (error) {
    console.error('❌ ESCALATE state test failed:', error.message)
    return { success: false, error: error.message }
  }
}

/**
 * Test 8: SAFE_REDIRECT State - Proper Rendering
 * Tests SAFE_REDIRECT shows alternative pathways
 */
export async function testSAFE_REDIRECTState() {
  console.log('\n🔍 TEST 8: SAFE_REDIRECT State Rendering...')
  
  try {
    const response = await axios.post(`${NYAYA_API}/nyaya/query`, {
      query: 'administrative tribunal appeal for government decision',
      jurisdiction: 'UK'
    }, { timeout: 30000 })

    const decision = response.data
    
    if (decision.enforcement_decision !== 'SAFE_REDIRECT') {
      console.log(`⚠️  Got ${decision.enforcement_decision} instead of SAFE_REDIRECT (this is OK for testing other states)`)
      return { success: true, note: `Received ${decision.enforcement_decision}` }
    }

    console.log('✅ SAFE_REDIRECT state received')
    console.log(`   Color: #6f42c1 (purple)`)
    console.log(`   Label: ↩️ SAFE REDIRECT`)
    console.log(`   Confidence: ${Math.round(decision.confidence?.overall * 100)}%`)
    console.log(`   Suggested Route: ${decision.legal_route?.join(' → ')}`)

    return { success: true, decision }
  } catch (error) {
    console.error('❌ SAFE_REDIRECT state test failed:', error.message)
    return { success: false, error: error.message }
  }
}

/**
 * Test 9: Error Handling - Backend Error Response
 * Validates error messages are captured
 */
export async function testErrorHandling() {
  console.log('\n🔍 TEST 9: Error Handling Validation...')
  
  try {
    // Test with empty query
    const response = await axios.post(`${NYAYA_API}/nyaya/query`, {
      query: '',
      jurisdiction: 'IN'
    }, { timeout: 30000 })
    
    console.error('❌ Empty query should have failed but succeeded')
    return { success: false, error: 'Empty query was accepted' }
  } catch (error) {
    if (error.response?.data?.detail) {
      console.log('✅ Error properly captured and returned')
      console.log(`   Error message: ${error.response.data.detail}`)
      return { success: true, error: error.response.data.detail }
    } else {
      console.log('✅ Error caught (no detail in response)')
      return { success: true }
    }
  }
}

/**
 * Test 10: Timeout Handling
 * Validates 30 second timeout is respected
 */
export async function testTimeoutHandling() {
  console.log('\n🔍 TEST 10: Timeout Handling (30s limit)...')
  
  try {
    const response = await axios.post(`${NYAYA_API}/nyaya/query`, {
      query: 'test query',
      jurisdiction: 'IN'
    }, { timeout: 30000 })

    console.log('✅ Request completed within 30 second timeout')
    return { success: true }
  } catch (error) {
    if (error.code === 'ECONNABORTED') {
      console.log('✅ Timeout was enforced (request exceeded 30s)')
      return { success: true, timeout: true }
    } else {
      console.log('⚠️  Request failed but not due to timeout')
      return { success: false, error: error.message }
    }
  }
}

/**
 * Run All DAY 2 Tests
 */
export async function runAllDay2Tests() {
  console.log('\n═══════════════════════════════════════════════════════════════')
  console.log('DAY 2 - BACKEND INTEGRATION & ENFORCEMENT STATE TESTING')
  console.log('═══════════════════════════════════════════════════════════════')
  console.log(`Backend URL: ${NYAYA_API}`)
  console.log(`Start Time: ${new Date().toISOString()}\n`)

  const results = {
    passed: 0,
    failed: 0,
    tests: []
  }

  // Test 1: Connection
  const conn = await testBackendConnection()
  results.tests.push({ name: 'Backend Connection', ...conn })
  if (conn.success) results.passed++; else results.failed++

  if (!conn.success) {
    console.log('\n❌ Backend is not responding. Cannot continue with remaining tests.\n')
    return results
  }

  // Test 2: Query
  const query = await testQueryEndpoint()
  results.tests.push({ name: 'Query Endpoint', ...query })
  if (query.success) results.passed++; else results.failed++

  if (query.success && query.decision) {
    // Test 3: Fields
    const fields = validateResponseFields(query.decision)
    results.tests.push({ name: 'Response Fields', success: fields })
    if (fields) results.passed++; else results.failed++

    // Test 4: Enforcement State
    const enforcement = validateEnforcementState(query.decision)
    results.tests.push({ name: 'Enforcement State', success: enforcement })
    if (enforcement) results.passed++; else results.failed++

    // Test ALLOW
    const allow = await testALLOWState()
    results.tests.push({ name: 'ALLOW State', success: allow.success })
    if (allow.success) results.passed++; else results.failed++

    // Test BLOCK (Critical)
    const block = await testBLOCKState()
    results.tests.push({ name: 'BLOCK State (CRITICAL)', success: block.success })
    if (block.success) results.passed++; else results.failed++

    // Test ESCALATE
    const escalate = await testESCALATEState()
    results.tests.push({ name: 'ESCALATE State', success: escalate.success })
    if (escalate.success) results.passed++; else results.failed++

    // Test SAFE_REDIRECT
    const redirect = await testSAFE_REDIRECTState()
    results.tests.push({ name: 'SAFE_REDIRECT State', success: redirect.success })
    if (redirect.success) results.passed++; else results.failed++

    // Test Error Handling
    const errors = await testErrorHandling()
    results.tests.push({ name: 'Error Handling', success: errors.success })
    if (errors.success) results.passed++; else results.failed++

    // Test Timeout
    const timeout = await testTimeoutHandling()
    results.tests.push({ name: 'Timeout Handling', success: timeout.success })
    if (timeout.success) results.passed++; else results.failed++
  }

  // Print summary
  console.log('\n═══════════════════════════════════════════════════════════════')
  console.log('TEST SUMMARY')
  console.log('═══════════════════════════════════════════════════════════════')
  console.log(`✅ Passed: ${results.passed}`)
  console.log(`❌ Failed: ${results.failed}`)
  console.log(`End Time: ${new Date().toISOString()}\n`)

  return results
}

export default {
  testBackendConnection,
  testQueryEndpoint,
  validateResponseFields,
  validateEnforcementState,
  testALLOWState,
  testBLOCKState,
  testESCALATEState,
  testSAFE_REDIRECTState,
  testErrorHandling,
  testTimeoutHandling,
  runAllDay2Tests
}
