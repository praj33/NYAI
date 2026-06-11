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
 * @returns {Promise<Object>} Legal decision response with recommendation
 */
export async function queryNyayaDecision(query, jurisdiction = 'IN') {
  try {
    if (!query || !query.trim()) {
      throw new Error('Query cannot be empty')
    }

    const response = await nyayaClient.post('/nyaya/query', {
      query: query.trim(),
      jurisdiction_hint: jurisdiction,
      user_context: { role: 'citizen', confidence_required: true }
    })

    if (!response.data?.recommendation?.type) {
      console.warn('Warning: Response missing recommendation.type field')
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
 * Validate recommendation type
 * @param {string} type - Recommendation type value
 * @returns {boolean} True if valid
 */
export function isValidRecommendationType(type) {
  const validTypes = ['INFORM', 'REVIEW', 'ESCALATE', 'INSUFFICIENT_DATA']
  return validTypes.includes(type)
}

/**
 * Get recommendation type details
 * @param {string} type - Recommendation type
 * @returns {Object} Color and label for the type
 */
export function getRecommendationTypeDetails(type) {
  const typeMap = {
    INFORM: {
      color: '#28a745',
      label: 'ℹ️ INFORMATIONAL',
      icon: 'ℹ️',
      description: 'Advisory guidance provided'
    },
    REVIEW: {
      color: '#ffc107',
      label: '⚠️ REVIEW RECOMMENDED',
      icon: '⚠️',
      description: 'Additional review recommended before acting'
    },
    ESCALATE: {
      color: '#fd7e14',
      label: '📈 ESCALATION ADVISED',
      icon: '📈',
      description: 'Consider consulting a legal professional'
    },
    INSUFFICIENT_DATA: {
      color: '#6c757d',
      label: '❓ INSUFFICIENT DATA',
      icon: '❓',
      description: 'Insufficient data for reliable guidance'
    }
  }
  return typeMap[type] || typeMap.INFORM
}

export default { queryNyayaDecision, testNyayaConnection, isValidRecommendationType, getRecommendationTypeDetails }
