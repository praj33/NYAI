import React, { useState } from 'react'
import { legalQueryService } from '../services/nyayaApi.js'

// Validate that traceId is a valid non-empty string
const isValidTraceId = (traceId) => {
  return typeof traceId === 'string' && traceId.length > 0 && traceId.trim().length > 0
}

// Validate that feedback value is a boolean
const isValidFeedbackValue = (value) => {
  return typeof value === 'boolean'
}

// Validate feedback type is one of the allowed types
const isValidFeedbackType = (type) => {
  const allowedTypes = ['helpful', 'clear', 'matches_situation', 'clarity', 'correctness', 'usefulness']
  return allowedTypes.includes(type)
}

const FeedbackButtons = ({ traceId, context = '' }) => {
  const [feedback, setFeedback] = useState({
    helpful: null,
    clear: null,
    matchesSituation: null
  })
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  const submitFeedback = async (type, value) => {
    // Validate traceId before sending signal
    if (!isValidTraceId(traceId)) {
      console.log('Skipping feedback submission - no valid trace ID')
      return
    }

    if (!isValidFeedbackValue(value)) {
      setError('Invalid feedback value')
      return
    }

    setError(null)
    setSubmitting(true)
    try {
      const rating = value ? 5 : 1
      
      const feedbackData = {
        trace_id: traceId,
        rating: rating,
        feedback_type: 'correctness',
        comment: `${type}: ${value ? 'positive' : 'negative'}`
      }

      const result = await legalQueryService.submitFeedback(feedbackData)
      
      if (result.success) {
        console.log(`Feedback submitted: ${type} = ${value}`)
      } else {
        console.error('Feedback error:', result.error)
      }
    } catch (error) {
      console.error('Failed to submit feedback:', error)
    } finally {
      setSubmitting(false)
    }
  }

  const handleFeedback = (type, value) => {
    setFeedback(prev => ({ ...prev, [type]: value }))
    submitFeedback(type, value)
  }

  return (
    <div style={{
      marginTop: '20px',
      padding: '20px',
      background: 'rgba(255, 255, 255, 0.05)',
      backdropFilter: 'blur(10px)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: '12px'
    }}>
      <h5 style={{
        fontSize: '14px',
        color: '#fff',
        marginBottom: '15px',
        fontWeight: '600'
      }}>
        Help us improve our responses
      </h5>

      {/* Helpful/Not Helpful */}
      <div style={{ marginBottom: '15px' }}>
        <div style={{
          fontSize: '13px',
          color: 'rgba(255, 255, 255, 0.7)',
          marginBottom: '8px',
          fontWeight: '500'
        }}>
          Was this response helpful?
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            onClick={() => handleFeedback('helpful', true)}
            disabled={submitting}
            style={{
              padding: '8px 12px',
              border: feedback.helpful === true ? '2px solid #28a745' : '2px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '6px',
              background: feedback.helpful === true ? '#28a745' : 'rgba(255, 255, 255, 0.05)',
              color: feedback.helpful === true ? 'white' : 'rgba(255, 255, 255, 0.8)',
              cursor: 'pointer',
              fontSize: '13px',
              display: 'flex',
              alignItems: 'center',
              gap: '5px'
            }}
          >
            👍 Helpful
          </button>
          <button
            onClick={() => handleFeedback('helpful', false)}
            disabled={submitting}
            style={{
              padding: '8px 12px',
              border: feedback.helpful === false ? '2px solid #dc3545' : '2px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '6px',
              background: feedback.helpful === false ? '#dc3545' : 'rgba(255, 255, 255, 0.05)',
              color: feedback.helpful === false ? 'white' : 'rgba(255, 255, 255, 0.8)',
              cursor: 'pointer',
              fontSize: '13px',
              display: 'flex',
              alignItems: 'center',
              gap: '5px'
            }}
          >
            👎 Not Helpful
          </button>
        </div>
      </div>

      {/* Was this clear? */}
      <div style={{ marginBottom: '15px' }}>
        <div style={{
          fontSize: '13px',
          color: 'rgba(255, 255, 255, 0.7)',
          marginBottom: '8px',
          fontWeight: '500'
        }}>
          Was this clear?
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            onClick={() => handleFeedback('clear', true)}
            disabled={submitting}
            style={{
              padding: '6px 12px',
              border: feedback.clear === true ? '2px solid #28a745' : '2px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '6px',
              background: feedback.clear === true ? '#28a745' : 'rgba(255, 255, 255, 0.05)',
              color: feedback.clear === true ? 'white' : 'rgba(255, 255, 255, 0.8)',
              cursor: 'pointer',
              fontSize: '13px'
            }}
          >
            Yes
          </button>
          <button
            onClick={() => handleFeedback('clear', false)}
            disabled={submitting}
            style={{
              padding: '6px 12px',
              border: feedback.clear === false ? '2px solid #dc3545' : '2px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '6px',
              background: feedback.clear === false ? '#dc3545' : 'rgba(255, 255, 255, 0.05)',
              color: feedback.clear === false ? 'white' : 'rgba(255, 255, 255, 0.8)',
              cursor: 'pointer',
              fontSize: '13px'
            }}
          >
            No
          </button>
        </div>
      </div>

      {/* Did this match your situation? */}
      <div style={{ marginBottom: '15px' }}>
        <div style={{
          fontSize: '13px',
          color: 'rgba(255, 255, 255, 0.7)',
          marginBottom: '8px',
          fontWeight: '500'
        }}>
          Did this match your situation?
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            onClick={() => handleFeedback('matchesSituation', true)}
            disabled={submitting}
            style={{
              padding: '6px 12px',
              border: feedback.matchesSituation === true ? '2px solid #28a745' : '2px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '6px',
              background: feedback.matchesSituation === true ? '#28a745' : 'rgba(255, 255, 255, 0.05)',
              color: feedback.matchesSituation === true ? 'white' : 'rgba(255, 255, 255, 0.8)',
              cursor: 'pointer',
              fontSize: '13px'
            }}
          >
            Yes
          </button>
          <button
            onClick={() => handleFeedback('matchesSituation', false)}
            disabled={submitting}
            style={{
              padding: '6px 12px',
              border: feedback.matchesSituation === false ? '2px solid #dc3545' : '2px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '6px',
              background: feedback.matchesSituation === false ? '#dc3545' : 'rgba(255, 255, 255, 0.05)',
              color: feedback.matchesSituation === false ? 'white' : 'rgba(255, 255, 255, 0.8)',
              cursor: 'pointer',
              fontSize: '13px'
            }}
          >
            No
          </button>
        </div>
      </div>

      {/* Submit Feedback Button */}
      <button
        onClick={() => {
          if (feedback.helpful !== null || feedback.clear !== null || feedback.matchesSituation !== null) {
            alert('Feedback submitted successfully!');
          }
        }}
        disabled={submitting || (feedback.helpful === null && feedback.clear === null && feedback.matchesSituation === null)}
        style={{
          width: '100%',
          padding: '12px',
          marginTop: '15px',
          border: 'none',
          borderRadius: '8px',
          background: (feedback.helpful !== null || feedback.clear !== null || feedback.matchesSituation !== null) ? '#3b82f6' : 'rgba(255, 255, 255, 0.1)',
          color: '#fff',
          cursor: (feedback.helpful !== null || feedback.clear !== null || feedback.matchesSituation !== null) ? 'pointer' : 'not-allowed',
          fontSize: '14px',
          fontWeight: '600'
        }}
      >
        {submitting ? 'Submitting...' : 'Submit Feedback'}
      </button>

      {/* Error display */}
      {error && (
        <div style={{
          marginTop: '15px',
          padding: '10px',
          background: 'rgba(220, 53, 69, 0.2)',
          border: '1px solid rgba(220, 53, 69, 0.4)',
          borderRadius: '6px',
          color: '#ff6b6b',
          fontSize: '13px'
        }}>
          {error}
        </div>
      )}
    </div>
  )
}

export default FeedbackButtons