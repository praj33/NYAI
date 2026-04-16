/**
 * useGravitasDecision Hook
 * 
 * Simplifies integration of GravitasDecisionPanel into any component.
 * Handles API calls, state management, and error handling.
 * 
 * Usage:
 * const { decision, loading, error, submitQuery } = useGravitasDecision()
 */

import { useState, useCallback, useRef } from 'react'
import { nyayaApi } from '../services/nyayaApi.js'
import { casePresentationService } from '../services/nyayaApi.js'
import GravitasResponseTransformer from '../lib/GravitasResponseTransformer.js'

/**
 * Hook for managing legal decision queries and state
 * 
 * @param {Object} options - Configuration options
 * @param {string} options.defaultJurisdiction - Default jurisdiction hint
 * @param {string} options.defaultDomain - Default domain hint
 * @param {Function} options.onSuccess - Callback when decision ready
 * @param {Function} options.onError - Callback on error
 * 
 * @returns {Object} Hook state and methods
 * @returns {Object} return.decision - Current decision or null
 * @returns {boolean} return.loading - Loading state
 * @returns {string} return.error - Error message or null
 * @returns {Function} return.submitQuery - Submit query function
 * @returns {Function} return.clearError - Clear error message
 * @returns {Function} return.explainDecision - Get explanation
 * @returns {Function} return.submitFeedback - Submit feedback
 * @returns {Function} return.exportDecision - Export as JSON
 */
export function useGravitasDecision(options = {}) {
  const {
    defaultJurisdiction = null,
    defaultDomain = null,
    onSuccess = null,
    onError = null
  } = options

  // State
  const [decision, setDecision] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [explanation, setExplanation] = useState(null)
  const abortControllerRef = useRef(null)

  /**
   * Submit a legal query
   */
  const submitQuery = useCallback(async (query, options = {}) => {
    // Validate
    if (!query || !query.trim()) {
      setError('Please enter a legal query')
      return null
    }

    // Cancel previous request if still pending
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }

    // Create new abort controller
    abortControllerRef.current = new AbortController()

    setLoading(true)
    setError(null)
    setDecision(null)
    setExplanation(null)

    try {
      const request = {
        query: query.trim(),
        jurisdiction_hint: options.jurisdiction || defaultJurisdiction,
        domain_hint: options.domain || defaultDomain,
        user_context: options.userContext || {
          role: 'citizen',
          confidence_required: true
        }
      }

      const response = await nyayaApi.queryLegal(request)

      if (!response.success) {
        throw new Error(response.error || 'Failed to process query')
      }

      // Transform and validate
      const validatedDecision = GravitasResponseTransformer.transform(
        response.data
      )

      if (!GravitasResponseTransformer.isValid(validatedDecision)) {
        throw new Error('Invalid response structure from backend')
      }

      // Verify enforcement status before displaying results
      const enforcementResult = await casePresentationService.getEnforcementStatus(
        validatedDecision.trace_id,
        validatedDecision.jurisdiction
      )

      const decisionWithEnforcement = {
        ...validatedDecision,
        enforcement_status: enforcementResult.success ? enforcementResult.data : null
      }

      setDecision(decisionWithEnforcement)

      // Call success callback if provided
      if (onSuccess) {
        onSuccess(decisionWithEnforcement)
      }

      return decisionWithEnforcement
    } catch (err) {
      // Don't set error if request was aborted
      if (err.name === 'AbortError') {
        return null
      }

      const errorMessage = err.message || 'An unexpected error occurred'
      setError(errorMessage)

      // Call error callback if provided
      if (onError) {
        onError(err)
      }

      return null
    } finally {
      setLoading(false)
    }
  }, [defaultJurisdiction, defaultDomain, onSuccess, onError])

  /**
   * Clear error message
   */
  const clearError = useCallback(() => {
    setError(null)
  }, [])

  /**
   * Get detailed explanation of decision
   */
  const explainDecision = useCallback(
    async (explanationLevel = 'detailed') => {
      if (!decision) {
        setError('No decision available to explain')
        return null
      }

      setLoading(true)
      setError(null)

      try {
        const response = await nyayaApi.explainReasoning({
          trace_id: decision.trace_id,
          explanation_level: explanationLevel
        })

        if (!response.success) {
          throw new Error(response.error || 'Failed to fetch explanation')
        }

        setExplanation(response.data)
        return response.data
      } catch (err) {
        const errorMessage = err.message || 'Failed to get explanation'
        setError(errorMessage)
        return null
      } finally {
        setLoading(false)
      }
    },
    [decision]
  )

  /**
   * Submit feedback on decision
   */
  const submitFeedback = useCallback(
    async (rating, feedbackType = 'usefulness', comment = '') => {
      if (!decision) {
        setError('No decision to provide feedback for')
        return false
      }

      if (!rating || rating < 1 || rating > 5) {
        setError('Rating must be between 1 and 5')
        return false
      }

      setLoading(true)
      setError(null)

      try {
        const response = await nyayaApi.submitFeedback({
          trace_id: decision.trace_id,
          rating,
          feedback_type: feedbackType,
          comment: comment || undefined
        })

        if (!response.success) {
          throw new Error(response.error || 'Failed to submit feedback')
        }

        return true
      } catch (err) {
        const errorMessage = err.message || 'Failed to submit feedback'
        setError(errorMessage)
        return false
      } finally {
        setLoading(false)
      }
    },
    [decision]
  )

  /**
   * Export decision as JSON file
   */
  const exportDecision = useCallback(() => {
    if (!decision) {
      setError('No decision to export')
      return false
    }

    try {
      const dataBlob = new Blob([JSON.stringify(decision, null, 2)], {
        type: 'application/json'
      })
      const url = URL.createObjectURL(dataBlob)
      const link = document.createElement('a')
      link.href = url
      link.download = `decision-${decision.trace_id}.json`
      link.click()

      // Cleanup
      URL.revokeObjectURL(url)
      return true
    } catch (err) {
      setError('Failed to export decision')
      return false
    }
  }, [decision])

  /**
   * Get debug information
   */
  const getDebugInfo = useCallback(() => {
    return {
      decision: decision ? GravitasResponseTransformer.toDebugString(decision) : null,
      hasError: !!error,
      isLoading: loading,
      isValid: decision ? GravitasResponseTransformer.isValid(decision) : false
    }
  }, [decision, error, loading])

  return {
    decision,
    loading,
    error,
    explanation,
    submitQuery,
    clearError,
    explainDecision,
    submitFeedback,
    exportDecision,
    getDebugInfo
  }
}

export default useGravitasDecision
