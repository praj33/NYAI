/**
 * GravitasResponseTransformer
 *
 * Utilities for transforming, validating, and formatting Nyaya API responses
 * into the format expected by the Gravitas UI components.
 */

export const GravitasResponseTransformer = {
  transform: (apiResponse) => {
    if (!apiResponse || typeof apiResponse !== 'object') {
      throw new Error('Invalid API response: expected object')
    }

    return {
      domain: sanitizeString(apiResponse.domain, 'general'),
      jurisdiction: sanitizeString(apiResponse.jurisdiction, 'Unknown'),
      trace_id: sanitizeString(apiResponse.trace_id, generateTraceId()),
      confidence: normalizeConfidence(apiResponse.confidence),
      legal_route: sanitizeArray(apiResponse.legal_route, []),
      constitutional_articles: sanitizeArray(apiResponse.constitutional_articles, []),
      provenance_chain: sanitizeProvenanceChain(apiResponse.provenance_chain || []),
      reasoning_trace: sanitizeObject(apiResponse.reasoning_trace, {}),
      recommendation: normalizeRecommendation(apiResponse.recommendation)
    }
  },

  isValid: (decision) => {
    return (
      decision &&
      typeof decision === 'object' &&
      decision.trace_id &&
      decision.jurisdiction &&
      decision.domain
    )
  },

  getSummary: (decision) => {
    if (!GravitasResponseTransformer.isValid(decision)) {
      return 'Invalid decision data'
    }

    const confidencePercent = Math.round(decision.confidence * 100)
    const jurisdiction = decision.jurisdiction || 'Unknown'
    const domain = decision.domain || 'General'

    return `${confidencePercent}% confidence - ${domain} case in ${jurisdiction}`
  },

  formatConfidence: (confidence) => {
    const percent = Math.round(normalizeConfidence(confidence) * 100)

    if (percent >= 85) return `Very High (${percent}%)`
    if (percent >= 65) return `High (${percent}%)`
    if (percent >= 45) return `Moderate (${percent}%)`
    if (percent >= 25) return `Low (${percent}%)`
    return `Very Low (${percent}%)`
  },

  getConfidenceColor: (confidence) => {
    const percent = Math.round(normalizeConfidence(confidence) * 100)

    if (percent >= 85) return '#28a745'
    if (percent >= 65) return '#20c997'
    if (percent >= 45) return '#ffc107'
    if (percent >= 25) return '#fd7e14'
    return '#dc3545'
  },

  formatRecommendation: (recommendation) => {
    if (!recommendation) return null

    const typeLabels = {
      INFORM: 'ℹ️ Informational guidance',
      REVIEW: '⚠️ Review recommended',
      ESCALATE: '📈 Escalation advised',
      INSUFFICIENT_DATA: '❓ Insufficient data'
    }

    return {
      ...recommendation,
      displayLabel: typeLabels[recommendation.type] || 'Unknown recommendation',
      severity: getRecommendationSeverity(recommendation.type)
    }
  },

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

    if (decision.recommendation?.type && decision.recommendation.type !== 'INFORM') {
      points.push(`${formatLabel(decision.recommendation.type)}`)
    }

    return points
  },

  toDebugString: (decision) => {
    return `[${decision.trace_id.substring(0, 8)}] ${decision.domain} @ ${decision.jurisdiction} (${Math.round(decision.confidence * 100)}%)`
  },

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
  if (value && typeof value === 'object' && typeof value.overall === 'number') {
    return normalizeConfidence(value.overall)
  }
  const num = parseFloat(value)
  if (isNaN(num)) return 0.5
  if (num < 0) return 0
  if (num > 1) return 1
  return num
}

function normalizeRecommendation(rec) {
  if (!rec || typeof rec !== 'object') {
    return { type: 'INSUFFICIENT_DATA', confidence: 0, rationale: '' }
  }
  const validTypes = new Set(['INFORM', 'REVIEW', 'ESCALATE', 'INSUFFICIENT_DATA'])
  return {
    type: validTypes.has(rec.type) ? rec.type : 'INSUFFICIENT_DATA',
    confidence: typeof rec.confidence === 'number' ? rec.confidence : 0,
    rationale: rec.rationale || '',
    urgency_flag: rec.urgency_flag === true,
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

function getRecommendationSeverity(type) {
  switch (type) {
    case 'ESCALATE':
    case 'INSUFFICIENT_DATA':
      return 'high'
    case 'REVIEW':
      return 'medium'
    case 'INFORM':
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
