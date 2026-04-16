/**
 * GravitasResponseTransformer
 * 
 * Utilities for transforming, validating, and formatting Nyaya API responses
 * into the format expected by the Gravitas UI components.
 * 
 * Provides:
 * - Response validation and sanitization
 * - Data transformation and enrichment
 * - Error handling and fallback defaults
 * - Formatting utilities for display
 */

/**
 * Validates and transforms a NyayaResponse from the backend
 * 
 * @param {Object} apiResponse - Raw response from /nyaya/query endpoint
 * @returns {Object} Validated and transformed response ready for GravitasDecisionPanel
 * @throws {Error} If response is missing critical fields
 * 
 * @example
 * const response = await nyayaApi.query({ query: "Can I file a case?" });
 * const validatedData = GravitasResponseTransformer.transform(response);
 * <GravitasDecisionPanel decision={validatedData} />
 */
export const GravitasResponseTransformer = {
  /**
   * Transform and validate NyayaResponse
   */
  transform: (apiResponse) => {
    if (!apiResponse || typeof apiResponse !== 'object') {
      throw new Error('Invalid API response: expected object')
    }

    return {
      // Required fields
      domain: sanitizeString(apiResponse.domain, 'general'),
      jurisdiction: sanitizeString(apiResponse.jurisdiction, 'Unknown'),
      trace_id: sanitizeString(apiResponse.trace_id, generateTraceId()),
      
      // Confidence - always 0.0 to 1.0
      confidence: normalizeConfidence(apiResponse.confidence),
      
      // Arrays
      legal_route: sanitizeArray(apiResponse.legal_route, []),
      constitutional_articles: sanitizeArray(apiResponse.constitutional_articles, []),
      provenance_chain: sanitizeProvenanceChain(apiResponse.provenance_chain || []),
      
      // Objects
      reasoning_trace: sanitizeObject(apiResponse.reasoning_trace, {}),
      enforcement_status: normalizeEnforcementStatus(apiResponse.enforcement_status)
    }
  },

  /**
   * Validate if response meets minimum requirements for display
   */
  isValid: (decision) => {
    return (
      decision &&
      typeof decision === 'object' &&
      decision.trace_id &&
      decision.jurisdiction &&
      decision.domain
    )
  },

  /**
   * Get a user-friendly summary from the decision
   */
  getSummary: (decision) => {
    if (!GravitasResponseTransformer.isValid(decision)) {
      return 'Invalid decision data'
    }

    const confidencePercent = Math.round(decision.confidence * 100)
    const jurisdiction = decision.jurisdiction || 'Unknown'
    const domain = decision.domain || 'General'

    return `${confidencePercent}% confidence - ${domain} case in ${jurisdiction}`
  },

  /**
   * Format confidence for human-readable text
   */
  formatConfidence: (confidence) => {
    const percent = Math.round(normalizeConfidence(confidence) * 100)
    
    if (percent >= 85) return `Very High (${percent}%)`
    if (percent >= 65) return `High (${percent}%)`
    if (percent >= 45) return `Moderate (${percent}%)`
    if (percent >= 25) return `Low (${percent}%)`
    return `Very Low (${percent}%)`
  },

  /**
   * Get confidence color for UI
   */
  getConfidenceColor: (confidence) => {
    const percent = Math.round(normalizeConfidence(confidence) * 100)
    
    if (percent >= 85) return '#28a745' // Green
    if (percent >= 65) return '#20c997' // Teal
    if (percent >= 45) return '#ffc107' // Yellow
    if (percent >= 25) return '#fd7e14' // Orange
    return '#dc3545' // Red
  },

  /**
   * Format enforcement status for display
   */
  formatEnforcementStatus: (status) => {
    if (!status) return null

    const stateLabels = {
      clear: '✅ Clear to proceed',
      block: '🚫 Pathway blocked',
      escalate: '📈 Escalation required',
      soft_redirect: '↩️ Consider alternative',
      conditional: '⚠️ Conditional access'
    }

    return {
      ...status,
      displayLabel: stateLabels[status.state] || 'Unknown status',
      severity: getSeverity(status.state)
    }
  },

  /**
   * Extract key points for quick reference
   */
  getKeyPoints: (decision) => {
    const points = []

    if (decision.domain) {
      points.push(`Domain: ${formatLabel(decision.domain)}`)
    }

    if (decision.jurisdiction) {
      points.push(`Jurisdiction: ${decision.jurisdiction}`)
    }

    if (decision.confidence) {
      points.push(`Confidence: ${GravitasResponseTransformer.formatConfidence(decision.confidence)}`)
    }

    if (decision.legal_route && decision.legal_route.length > 0) {
      points.push(`Route: ${decision.legal_route.join(' → ')}`)
    }

    if (decision.constitutional_articles && decision.constitutional_articles.length > 0) {
      points.push(`${decision.constitutional_articles.length} Constitutional articles referenced`)
    }

    if (decision.enforcement_status?.state && decision.enforcement_status.state !== 'clear') {
      points.push(`⚠️ ${formatLabel(decision.enforcement_status.state)}`)
    }

    return points
  },

  /**
   * Create a compact representation for logging/debugging
   */
  toDebugString: (decision) => {
    return `[${decision.trace_id.substring(0, 8)}] ${decision.domain} @ ${decision.jurisdiction} (${Math.round(decision.confidence * 100)}%)`
  },

  /**
   * Merge multiple decisions (for multi-jurisdiction responses)
   */
  mergeMultiple: (decisions) => {
    if (!Array.isArray(decisions) || decisions.length === 0) {
      return null
    }

    const avgConfidence = decisions.reduce((sum, d) => sum + d.confidence, 0) / decisions.length

    return {
      merged: true,
      count: decisions.length,
      decisions,
      average_confidence: normalizeConfidence(avgConfidence),
      trace_ids: decisions.map(d => d.trace_id),
      jurisdictions: [...new Set(decisions.map(d => d.jurisdiction))]
    }
  }
}

/**
 * Internal helper functions
 */

function sanitizeString(value, defaultValue = '') {
  if (typeof value === 'string') {
    return value.trim() || defaultValue
  }
  return defaultValue
}

function sanitizeArray(value, defaultValue = []) {
  if (Array.isArray(value)) {
    return value.filter(item => item !== null && item !== undefined)
  }
  return defaultValue
}

function sanitizeObject(value, defaultValue = {}) {
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    return value
  }
  return defaultValue
}

function normalizeConfidence(value) {
  const num = parseFloat(value)
  if (isNaN(num)) return 0.5
  if (num < 0) return 0
  if (num > 1) return 1
  return num
}

function normalizeEnforcementStatus(status) {
  if (!status) return null

  const validStates = ['clear', 'block', 'escalate', 'soft_redirect', 'conditional']
  const state = validStates.includes(status.state) ? status.state : 'clear'

  return {
    state,
    reason: sanitizeString(status.reason, ''),
    blocked_path: status.blocked_path || null,
    escalation_required: Boolean(status.escalation_required),
    escalation_target: status.escalation_target || null,
    redirect_suggestion: status.redirect_suggestion || null,
    safe_explanation: sanitizeString(status.safe_explanation, ''),
    trace_id: sanitizeString(status.trace_id, '')
  }
}

function sanitizeProvenanceChain(chain) {
  if (!Array.isArray(chain)) return []

  return chain
    .filter(item => item && typeof item === 'object')
    .map(item => ({
      source: sanitizeString(item.source, 'Processing Step'),
      description: sanitizeString(item.description, ''),
      timestamp: item.timestamp || new Date().toISOString(),
      data: item.data || null
    }))
}

function getSeverity(state) {
  switch (state) {
    case 'block':
      return 'critical'
    case 'escalate':
    case 'conditional':
      return 'high'
    case 'soft_redirect':
      return 'medium'
    case 'clear':
    default:
      return 'none'
  }
}

function formatLabel(str) {
  return str
    .replace(/([A-Z])/g, ' $1')
    .replace(/_/g, ' ')
    .trim()
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

function generateTraceId() {
  return `trace_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

export default GravitasResponseTransformer
