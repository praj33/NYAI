// casePayloadValidator.js — Runtime validation schema for incoming casePayload
// Uses strict validation to prevent TypeError when rendering GravitasDocumentView.
// Validates all 9 required fields per the formatter contract.

// Import Zod if available, otherwise uses custom validation
let zod = null
try {
  zod = require('zod')
} catch (e) {
  // Zod not available, use custom validation
}

/**
 * Validation result object
 * @typedef {Object} ValidationResult
 * @property {boolean} valid - Whether validation passed
 * @property {string|null} error - Error message if validation failed
 * @property {Object|null} sanitized - Sanitized casePayload object
 */

/**
 * Validates a procedural step object
 * @param {any} step 
 * @param {number} index 
 * @returns {{ valid: boolean, error: string|null, sanitized: any }}
 */
function validateProceduralStep(step, index) {
  if (!step || typeof step !== 'object') {
    return { valid: false, error: `procedural_steps[${index}] is not an object`, sanitized: null }
  }
  
  const validTypes = ['required', 'optional', 'conditional']
  
  return {
    valid: true,
    error: null,
    sanitized: {
      step_number: typeof step.step_number === 'number' ? step.step_number : index + 1,
      title: typeof step.title === 'string' ? step.title : `Step ${index + 1}`,
      description: typeof step.description === 'string' ? step.description : '',
      type: validTypes.includes(step.type) ? step.type : 'required',
      deadline: step.deadline && typeof step.deadline === 'string' ? step.deadline : null,
      documents: Array.isArray(step.documents) ? step.documents : []
    }
  }
}

/**
 * Validates a timeline event object
 * @param {any} event 
 * @param {number} index 
 * @returns {{ valid: boolean, error: string|null, sanitized: any }}
 */
function validateTimelineEvent(event, index) {
  if (!event || typeof event !== 'object') {
    return { valid: false, error: `timeline[${index}] is not an object`, sanitized: null }
  }
  
  const validTypes = ['event', 'deadline', 'milestone', 'step']
  const validStatuses = ['completed', 'pending', 'overdue']
  
  return {
    valid: true,
    error: null,
    sanitized: {
      id: typeof event.id === 'string' ? event.id : `event_${index}`,
      date: typeof event.date === 'string' ? event.date : new Date().toISOString(),
      title: typeof event.title === 'string' ? event.title : `Event ${index + 1}`,
      description: typeof event.description === 'string' ? event.description : '',
      type: validTypes.includes(event.type) ? event.type : 'event',
      status: validStatuses.includes(event.status) ? event.status : 'pending',
      documents: Array.isArray(event.documents) ? event.documents : [],
      parties: Array.isArray(event.parties) ? event.parties : []
    }
  }
}

/**
 * Validates enforcement status object
 * @param {any} status 
 * @returns {{ valid: boolean, error: string|null, sanitized: any }}
 */
function validateEnforcementStatus(status) {
  if (!status || typeof status !== 'object') {
    return { valid: false, error: 'enforcement_status is not an object', sanitized: null }
  }
  
  const validStates = ['clear', 'block', 'escalate', 'soft_redirect', 'conditional']
  const validVerdicts = ['ENFORCEABLE', 'PENDING_REVIEW', 'NON_ENFORCEABLE']
  
  const state = validStates.includes(status.state) ? status.state : 'block'
  const verdict = validVerdicts.includes(status.verdict) ? status.verdict : 'NON_ENFORCEABLE'
  
  return {
    valid: true,
    error: null,
    sanitized: {
      state,
      verdict,
      reason: typeof status.reason === 'string' ? status.reason : 'Validation pending',
      barriers: Array.isArray(status.barriers) ? status.barriers : [],
      blocked_path: status.blocked_path ?? null,
      escalation_required: Boolean(status.escalation_required),
      escalation_target: status.escalation_target ?? null,
      redirect_suggestion: status.redirect_suggestion ?? null,
      safe_explanation: typeof status.safe_explanation === 'string' 
        ? status.safe_explanation 
        : 'Enforcement status could not be verified.',
      trace_id: status.trace_id ?? null
    }
  }
}

/**
 * Main casePayload validator
 * Strictly validates all 9 required fields per formatter contract:
 * - trace_id (required)
 * - enforcement_status (required)
 * - jurisdiction (required)
 * - case_summary (required)
 * - legal_route (required)
 * - procedural_steps (may be empty array)
 * - timeline (may be empty array)
 * - decision (required)
 * - reasoning (required)
 * 
 * @param {any} payload - Raw casePayload from backend
 * @param {boolean} strict - If true, throws on missing non-critical fields. If false, provides fallbacks.
 * @returns {ValidationResult}
 */
export function validateCasePayload(payload, strict = false) {
  // Handle null/undefined
  if (!payload) {
    return {
      valid: false,
      error: 'casePayload is null or undefined',
      sanitized: null
    }
  }

  // Handle non-object
  if (typeof payload !== 'object') {
    return {
      valid: false,
      error: 'casePayload is not an object',
      sanitized: null
    }
  }

  // Required fields that MUST be present (throw in strict mode)
  const requiredFields = ['trace_id', 'enforcement_status', 'jurisdiction', 'case_summary', 'legal_route', 'decision', 'reasoning']
  
  for (const field of requiredFields) {
    if (payload[field] == null || (typeof payload[field] === 'string' && payload[field].trim() === '')) {
      if (strict) {
        return {
          valid: false,
          error: `casePayload missing required field: "${field}"`,
          sanitized: null
        }
      }
    }
  }

  // Validate enforcement_status (critical - must exist and have verdict)
  const enforcementValidation = validateEnforcementStatus(payload.enforcement_status)
  if (!enforcementValidation.valid) {
    if (strict) {
      return {
        valid: false,
        error: enforcementValidation.error,
        sanitized: null
      }
    }
  }

  // Validate procedural_steps (non-critical - can be empty or missing)
  let proceduralSteps = []
  if (Array.isArray(payload.procedural_steps)) {
    const validatedSteps = payload.procedural_steps.map((step, i) => validateProceduralStep(step, i))
    const invalidSteps = validatedSteps.filter(s => !s.valid)
    
    if (invalidSteps.length > 0 && strict) {
      return {
        valid: false,
        error: invalidSteps[0].error,
        sanitized: null
      }
    }
    
    proceduralSteps = validatedSteps.map(s => s.sanitized)
  } else if (strict) {
    return {
      valid: false,
      error: 'procedural_steps is not an array',
      sanitized: null
    }
  }

  // Validate timeline (non-critical - can be empty or missing)
  let timeline = []
  if (Array.isArray(payload.timeline)) {
    const validatedEvents = payload.timeline.map((event, i) => validateTimelineEvent(event, i))
    const invalidEvents = validatedEvents.filter(e => !e.valid)
    
    if (invalidEvents.length > 0 && strict) {
      return {
        valid: false,
        error: invalidEvents[0].error,
        sanitized: null
      }
    }
    
    timeline = validatedEvents.map(e => e.sanitized)
  } else if (strict) {
    return {
      valid: false,
      error: 'timeline is not an array',
      sanitized: null
    }
  }

  // Validate legal_route (must be array of strings)
  let legalRoute = []
  if (Array.isArray(payload.legal_route)) {
    legalRoute = payload.legal_route.filter(item => typeof item === 'string')
  } else if (strict) {
    return {
      valid: false,
      error: 'legal_route is not an array',
      sanitized: null
    }
  }

  // Build sanitized output
  const sanitized = {
    trace_id: typeof payload.trace_id === 'string' ? payload.trace_id : 'unknown',
    enforcement_status: enforcementValidation.sanitized,
    jurisdiction: typeof payload.jurisdiction === 'string' ? payload.jurisdiction : 'Unknown',
    case_summary: typeof payload.case_summary === 'string' ? payload.case_summary : 'Summary unavailable',
    legal_route: legalRoute,
    procedural_steps: proceduralSteps,
    timeline: timeline,
    decision: typeof payload.decision === 'string' ? payload.decision : 'Decision pending',
    reasoning: typeof payload.reasoning === 'string' ? payload.reasoning : 'Reasoning unavailable'
  }

  return {
    valid: true,
    error: null,
    sanitized
  }
}

/**
 * Validates a single field and returns a fallback UI indicator
 * Use for optional/missing non-critical fields in rendering
 * 
 * @param {any} value - Field value to check
 * @param {string} fieldName - Name of field for error message
 * @param {any} fallback - Fallback value if validation fails (non-strict only)
 * @param {boolean} strict - Whether to throw or return fallback
 * @returns {{ valid: boolean, value: any }}
 */
export function validateField(value, fieldName, fallback = null, strict = false) {
  if (value != null && (typeof value !== 'object' || Array.isArray(value))) {
    return { valid: true, value }
  }
  
  if (strict) {
    throw new Error(`Field "${fieldName}" is invalid or missing`)
  }
  
  return { valid: false, value: fallback }
}

// Zod schema (if Zod is available in the project)
export const casePayloadZodSchema = zod ? zod.object({
  trace_id: zod.string().min(1, 'trace_id is required'),
  enforcement_status: zod.object({
    state: zod.enum(['clear', 'block', 'escalate', 'soft_redirect', 'conditional']),
    verdict: zod.enum(['ENFORCEABLE', 'PENDING_REVIEW', 'NON_ENFORCEABLE']),
    reason: zod.string(),
    barriers: zod.array(zod.string()).default([]),
    blocked_path: zod.string().nullable().default(null),
    escalation_required: zod.boolean().default(false),
    escalation_target: zod.string().nullable().default(null),
    redirect_suggestion: zod.string().nullable().default(null),
    safe_explanation: zod.string(),
    trace_id: zod.string().nullable().default(null)
  }),
  jurisdiction: zod.string().min(1, 'jurisdiction is required'),
  case_summary: zod.string().min(1, 'case_summary is required'),
  legal_route: zod.array(zod.string()),
  procedural_steps: zod.array(zod.object({
    step_number: zod.number().int().positive(),
    title: zod.string(),
    description: zod.string(),
    type: zod.enum(['required', 'optional', 'conditional']),
    deadline: zod.string().nullable(),
    documents: zod.array(zod.string())
  })).default([]),
  timeline: zod.array(zod.object({
    id: zod.string(),
    date: zod.string(),
    title: zod.string(),
    description: zod.string(),
    type: zod.enum(['event', 'deadline', 'milestone', 'step']),
    status: zod.enum(['completed', 'pending', 'overdue']),
    documents: zod.array(zod.string()),
    parties: zod.array(zod.string())
  })).default([]),
  decision: zod.string().min(1, 'decision is required'),
  reasoning: zod.string().min(1, 'reasoning is required')
}) : null
