import React, { useState, useCallback } from 'react'
import GravitasDecisionPanel from './GravitasDecisionPanel.jsx'
import GravitasResponseTransformer from '../lib/GravitasResponseTransformer.js'
import { nyayaApi } from '../services/nyayaApi.js'

/**
 * GravitasLegalDecisionScreen
 * 
 * Complete integration example showing how to:
 * 1. Submit a legal query to the Nyaya backend
 * 2. Transform the response using GravitasResponseTransformer
 * 3. Display the legal decision using GravitasDecisionPanel
 * 4. Handle feedback and explanation requests
 * 
 * This component is production-ready and demonstrates all integration patterns.
 * 
 * @example
 * <GravitasLegalDecisionScreen />
 */
const GravitasLegalDecisionScreen = () => {
  // State management
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [decision, setDecision] = useState(null)
  const [error, setError] = useState(null)
  const [explanation, setExplanation] = useState(null)
  const [showExplanation, setShowExplanation] = useState(false)
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false)

  /**
   * Handle legal query submission
   */
  const handleQuerySubmit = useCallback(async (e) => {
    e.preventDefault()
    
    if (!query.trim()) {
      setError('Please enter a legal query')
      return
    }

    setLoading(true)
    setError(null)
    setDecision(null)
    setExplanation(null)
    setShowExplanation(false)
    setFeedbackSubmitted(false)

    try {
      // Call the Nyaya API with the user's query
      const response = await nyayaApi.queryLegal({
        query: query.trim(),
        user_context: {
          role: 'citizen',
          confidence_required: true
        }
      })

      if (!response.success) {
        throw new Error(response.error || 'Failed to process query')
      }

      // Transform the response using GravitasResponseTransformer
      const transformedDecision = GravitasResponseTransformer.transform(response.data)

      // Validate the transformed data
      if (!GravitasResponseTransformer.isValid(transformedDecision)) {
        throw new Error('Invalid response structure')
      }

      // Set the decision for display
      setDecision(transformedDecision)
      
      // Log success for analytics
      console.log(
        'Decision Generated:',
        GravitasResponseTransformer.toDebugString(transformedDecision)
      )
    } catch (err) {
      console.error('Query Error:', err)
      setError(
        err.message || 'An unexpected error occurred. Please try again.'
      )
    } finally {
      setLoading(false)
    }
  }, [query])

  /**
   * Request detailed explanation of the decision
   */
  const handleExplainClick = useCallback(async (traceId) => {
    setLoading(true)
    setError(null)

    try {
      const response = await nyayaApi.explainReasoning({
        trace_id: traceId,
        explanation_level: 'detailed'
      })

      if (!response.success) {
        throw new Error(response.error || 'Failed to fetch explanation')
      }

      setExplanation(response.data)
      setShowExplanation(true)

      console.log('Explanation Retrieved:', traceId)
    } catch (err) {
      console.error('Explanation Error:', err)
      setError('Failed to retrieve detailed explanation')
    } finally {
      setLoading(false)
    }
  }, [])

  /**
   * Submit feedback on the decision
   */
  const handleFeedbackClick = useCallback(async (traceId) => {
    // In a production app, this would open a feedback modal
    // For this example, we'll simulate submitting a rating
    
    setLoading(true)
    setError(null)

    try {
      const response = await nyayaApi.submitFeedback({
        trace_id: traceId,
        rating: 4,
        feedback_type: 'usefulness',
        comment: 'Clear and helpful legal guidance'
      })

      if (!response.success) {
        throw new Error(response.error || 'Failed to submit feedback')
      }

      setFeedbackSubmitted(true)
      
      // Show success message for 3 seconds
      setTimeout(() => setFeedbackSubmitted(false), 3000)

      console.log('Feedback Submitted:', traceId)
    } catch (err) {
      console.error('Feedback Error:', err)
      setError('Failed to submit feedback')
    } finally {
      setLoading(false)
    }
  }, [])

  // Extract key points for sidebar summary
  const keyPoints = decision 
    ? GravitasResponseTransformer.getKeyPoints(decision)
    : []

  return (
    <div className="gravitas-decision-screen">
      {/* Query Input Section */}
      <div className="query-section">
        <div className="query-container">
          <h1 className="query-title">Gravitas Legal AI</h1>
          <p className="query-subtitle">
            Get intelligent legal guidance for your specific situation
          </p>

          <form onSubmit={handleQuerySubmit} className="query-form">
            <textarea
              className="query-input"
              placeholder="Describe your legal situation... (e.g., 'Can I sue my landlord for property damage?')"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              rows={4}
              disabled={loading}
            />
            
            <button
              type="submit"
              className="query-button"
              disabled={loading || !query.trim()}
            >
              {loading ? 'Processing...' : 'Get Legal Guidance'}
            </button>
          </form>

          {/* Error Display */}
          {error && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              <p>{error}</p>
              <button
                onClick={() => setError(null)}
                className="error-dismiss"
              >
                ✕
              </button>
            </div>
          )}

          {/* Feedback Success Message */}
          {feedbackSubmitted && (
            <div className="success-message">
              <span className="success-icon">✅</span>
              <p>Thank you for your feedback! It helps us improve.</p>
            </div>
          )}
        </div>
      </div>

      {/* Results Section */}
      <div className="results-section">
        <div className="results-container">
          {/* Main Decision Panel */}
          <div className="decision-column">
            <GravitasDecisionPanel
              decision={decision}
              loading={loading}
              onExplainClick={handleExplainClick}
              onFeedbackClick={handleFeedbackClick}
            />
          </div>

          {/* Sidebar Summary */}
          {decision && (
            <div className="summary-sidebar">
              <div className="sidebar-card">
                <h3 className="sidebar-title">Quick Summary</h3>
                <div className="summary-points">
                  {keyPoints.map((point, index) => (
                    <div key={index} className="summary-point">
                      <div className="point-marker">•</div>
                      <div className="point-text">{point}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="sidebar-card">
                <h3 className="sidebar-title">How Confident?</h3>
                <div className="confidence-explanation">
                  <div className="confidence-score">
                    {Math.round(decision.confidence * 100)}%
                  </div>
                  <p className="confidence-meaning">
                    {GravitasResponseTransformer.formatConfidence(decision.confidence)}
                  </p>
                  <p className="confidence-note">
                    Higher percentages indicate greater certainty in the legal analysis.
                  </p>
                </div>
              </div>

              <div className="sidebar-card">
                <h3 className="sidebar-title">Need Help?</h3>
                <div className="help-links">
                  <a href="#" className="help-link">
                    💬 Contact a lawyer
                  </a>
                  <a href="#" className="help-link">
                    📚 Learn more about this topic
                  </a>
                  <a href="#" className="help-link">
                    ❓ FAQ
                  </a>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Explanation Panel (if shown) */}
        {showExplanation && explanation && (
          <div className="explanation-panel">
            <div className="explanation-header">
              <h3>Detailed Reasoning</h3>
              <button
                onClick={() => setShowExplanation(false)}
                className="close-button"
              >
                ✕
              </button>
            </div>
            <div className="explanation-content">
              {renderExplanation(explanation)}
            </div>
          </div>
        )}
      </div>

      {/* Styling for the integration */}
      <style jsx>{`
        .gravitas-decision-screen {
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          padding: 20px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto',
            'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans',
            'Helvetica Neue', sans-serif;
        }

        .query-section {
          margin-bottom: 40px;
        }

        .query-container {
          max-width: 900px;
          margin: 0 auto;
          background: white;
          border-radius: 12px;
          padding: 40px;
          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        }

        .query-title {
          font-size: 2.5rem;
          font-weight: 700;
          color: #2c3e50;
          margin: 0 0 10px 0;
        }

        .query-subtitle {
          font-size: 1.1rem;
          color: #7f8c8d;
          margin: 0 0 30px 0;
        }

        .query-form {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .query-input {
          width: 100%;
          padding: 16px;
          border: 2px solid #e9ecef;
          border-radius: 8px;
          font-size: 1rem;
          font-family: inherit;
          resize: vertical;
          transition: all 0.3s;
        }

        .query-input:focus {
          outline: none;
          border-color: #667eea;
          box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .query-input:disabled {
          background-color: #f8f9fa;
          cursor: not-allowed;
        }

        .query-button {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          padding: 14px 28px;
          border: none;
          border-radius: 8px;
          font-size: 1.1rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s;
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }

        .query-button:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 8px 20px rgba(102, 126, 234, 0.5);
        }

        .query-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .error-message {
          display: flex;
          align-items: flex-start;
          gap: 12px;
          background: #f8d7da;
          border: 1px solid #f5c6cb;
          border-radius: 8px;
          padding: 12px 16px;
          color: #721c24;
        }

        .error-icon {
          font-size: 1.3rem;
          flex-shrink: 0;
        }

        .error-message p {
          margin: 0;
          flex: 1;
        }

        .error-dismiss {
          background: none;
          border: none;
          color: #721c24;
          cursor: pointer;
          font-size: 1.2rem;
          padding: 0;
          flex-shrink: 0;
        }

        .success-message {
          display: flex;
          align-items: center;
          gap: 12px;
          background: #d4edda;
          border: 1px solid #c3e6cb;
          border-radius: 8px;
          padding: 12px 16px;
          color: #155724;
        }

        .success-icon {
          font-size: 1.3rem;
        }

        .success-message p {
          margin: 0;
        }

        .results-section {
          max-width: 1400px;
          margin: 0 auto;
        }

        .results-container {
          display: grid;
          grid-template-columns: 1fr 320px;
          gap: 24px;
        }

        @media (max-width: 1200px) {
          .results-container {
            grid-template-columns: 1fr;
          }
        }

        .decision-column {
          min-height: 400px;
        }

        .summary-sidebar {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .sidebar-card {
          background: white;
          border-radius: 12px;
          padding: 24px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .sidebar-title {
          font-size: 1.1rem;
          font-weight: 600;
          color: #2c3e50;
          margin: 0 0 16px 0;
        }

        .summary-points {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .summary-point {
          display: flex;
          gap: 8px;
          font-size: 0.95rem;
          color: #495057;
          line-height: 1.5;
        }

        .point-marker {
          color: #667eea;
          font-weight: 700;
          flex-shrink: 0;
        }

        .confidence-score {
          font-size: 2.5rem;
          font-weight: 700;
          color: #667eea;
          text-align: center;
          margin-bottom: 8px;
        }

        .confidence-meaning {
          text-align: center;
          font-weight: 600;
          color: #2c3e50;
          margin: 0 0 8px 0;
        }

        .confidence-note {
          font-size: 0.85rem;
          color: #7f8c8d;
          margin: 0;
          text-align: center;
          line-height: 1.5;
        }

        .help-links {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .help-link {
          display: block;
          padding: 10px;
          background: #f8f9fa;
          border-radius: 6px;
          color: #667eea;
          text-decoration: none;
          font-size: 0.95rem;
          transition: all 0.2s;
          border: 1px solid #e9ecef;
        }

        .help-link:hover {
          background: #667eea;
          color: white;
          border-color: #667eea;
        }

        .explanation-panel {
          background: white;
          border-radius: 12px;
          margin-top: 24px;
          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
          overflow: hidden;
        }

        .explanation-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 24px;
          border-bottom: 1px solid #e9ecef;
        }

        .explanation-header h3 {
          margin: 0;
          color: #2c3e50;
        }

        .close-button {
          background: none;
          border: none;
          font-size: 1.5rem;
          cursor: pointer;
          color: #7f8c8d;
          padding: 0;
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .close-button:hover {
          color: #2c3e50;
        }

        .explanation-content {
          padding: 24px;
        }

        @media (max-width: 768px) {
          .gravitas-decision-screen {
            padding: 12px;
          }

          .query-container {
            padding: 20px;
          }

          .query-title {
            font-size: 1.8rem;
          }

          .query-subtitle {
            font-size: 1rem;
          }

          .results-container {
            grid-template-columns: 1fr;
          }

          .summary-sidebar {
            order: -1;
          }
        }
      `}</style>
    </div>
  )
}

/**
 * Helper function to render explanation content
 * Customize this based on your explanation response schema
 */
function renderExplanation(explanation) {
  if (!explanation) return null

  return (
    <div className="explanation-content-inner">
      {explanation.explanation && (
        <div className="explanation-section">
          <h4>Analysis</h4>
          <p>{explanation.explanation}</p>
        </div>
      )}
      {explanation.reasoning_tree && (
        <div className="explanation-section">
          <h4>Reasoning Tree</h4>
          <pre>{JSON.stringify(explanation.reasoning_tree, null, 2)}</pre>
        </div>
      )}
      {explanation.constitutional_articles && explanation.constitutional_articles.length > 0 && (
        <div className="explanation-section">
          <h4>Referenced Articles</h4>
          <ul>
            {explanation.constitutional_articles.map((article, index) => (
              <li key={index}>{article}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default GravitasLegalDecisionScreen
