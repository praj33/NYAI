/**
 * Nyaya AI Backend API Integration
 * 
 * Connects to deployed Nyaya backend at https://nyaya-ai-0f02.onrender.com
 * Handles real legal decision queries and responses
 */

import axios from 'axios'

const NYAYA_API_BASE = 'https://nyaya-ai-0f02.onrender.com'

// Create axios instance for Nyaya API
const nyayaClient = axios.create({
  baseURL: NYAYA_API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Response interceptor for error handling
nyayaClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('Nyaya API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

/**
 * Query Nyaya AI for legal decision
 * @param {string} query - Legal query text
 * @param {string} jurisdiction - Optional jurisdiction (IN, UK, UAE, etc)
 * @returns {Promise<Object>} Legal decision response with enforcement_decision
 */
export async function queryNyayaDecision(query, jurisdiction = 'IN') {
  try {
    if (!query || !query.trim()) {
      throw new Error('Query cannot be empty')
    }

    const response = await nyayaClient.post('/nyaya/query', {
      query: query.trim(),
      jurisdiction_hint: jurisdiction
    })

    // Validate response has enforcement_decision
    if (!response.data?.enforcement_decision) {
      console.warn('Warning: Response missing enforcement_decision field')
    }

    return {
      success: true,
      data: response.data,
      timestamp: new Date().toISOString()
    }
  } catch (error) {
    console.error('Query failed:', error)
    
    // Provide specific error messages
    let errorMessage = 'Failed to fetch decision'
    
    if (error.code === 'ECONNABORTED') {
      errorMessage = 'Request timeout (30s). Backend server may be experiencing issues.'
    } else if (error.code === 'ECONNREFUSED') {
      errorMessage = 'Cannot connect to backend. Please check your internet connection.'
    } else if (error.response?.status === 400) {
      errorMessage = error.response.data?.detail || 'Invalid query format'
    } else if (error.response?.status === 500) {
      errorMessage = 'Backend server error. Please try again later.'
    } else if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail
    } else if (error.message) {
      errorMessage = error.message
    }

    return {
      success: false,
      error: errorMessage,
      timestamp: new Date().toISOString()
    }
  }
}

/**
 * Test connection to Nyaya backend
 * @returns {Promise<Object>} Connection test result
 */
export async function testNyayaConnection() {
  try {
    const response = await nyayaClient.get('/health', { timeout: 5000 })
    return {
      success: true,
      status: response.status,
      timestamp: new Date().toISOString(),
      message: 'Backend is online and responding'
    }
  } catch (error) {
    console.error('Connection test failed:', error.message)
    return {
      success: false,
      error: error.message,
      timestamp: new Date().toISOString(),
      message: 'Backend is not responding'
    }
  }
}

/**
 * Validate enforcement state
 * @param {string} state - Enforcement state value
 * @returns {boolean} True if valid
 */
export function isValidEnforcementState(state) {
  const validStates = ['ALLOW', 'BLOCK', 'ESCALATE', 'SAFE_REDIRECT']
  return validStates.includes(state)
}

/**
 * Get enforcement state details
 * @param {string} state - Enforcement state
 * @returns {Object} Color and label for the state
 */
export function getEnforcementStateDetails(state) {
  const stateMap = {
    ALLOW: {
      color: '#28a745',
      label: '✅ ALLOWED',
      icon: '✅',
      description: 'This legal pathway is permitted'
    },
    BLOCK: {
      color: '#dc3545',
      label: '🚫 BLOCKED',
      icon: '🚫',
      description: 'This pathway is blocked by legal authority'
    },
    ESCALATE: {
      color: '#fd7e14',
      label: '📈 ESCALATION REQUIRED',
      icon: '📈',
      description: 'This matter requires expert review and escalation'
    },
    SAFE_REDIRECT: {
      color: '#6f42c1',
      label: '↩️ SAFE REDIRECT',
      icon: '↩️',
      description: 'This matter should be redirected to a more appropriate venue'
    }
  }
  return stateMap[state] || stateMap.ALLOW
}

export default { queryNyayaDecision, testNyayaConnection, isValidEnforcementState, getEnforcementStateDetails }
