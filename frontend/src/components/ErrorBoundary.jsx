// ErrorBoundary.jsx — React ErrorBoundary class component
// Catches unhandled frontend exceptions and renders SystemCrash UI overlay.
// Wraps GravitasDocumentView and EnforcementGatekeeper to prevent white screen of death.
import React from 'react'
import ApiErrorState from './ApiErrorState.jsx'

/**
 * SystemCrash - Full-page overlay for unhandled React errors
 * Displays trace_id and "Return to Dashboard" action button
 */
const SystemCrash = ({ traceId, errorMessage, onReturnToDashboard, onRetry }) => {
  const handleReturn = () => {
    if (onReturnToDashboard) {
      onReturnToDashboard()
    } else {
      window.location.href = '/'
    }
  }

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.9)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
      padding: '20px'
    }}>
      <div style={{
        background: 'linear-gradient(135deg, rgba(220, 53, 69, 0.15) 0%, rgba(0, 0, 0, 0.8) 100%)',
        border: '1px solid rgba(220, 53, 69, 0.4)',
        borderRadius: '16px',
        padding: '48px',
        maxWidth: '550px',
        width: '100%',
        textAlign: 'center'
      }}>
        {/* Critical Error Icon */}
        <div style={{
          fontSize: '64px',
          marginBottom: '24px'
        }}>
          ⚠️
        </div>

        {/* Title */}
        <h2 style={{
          color: '#ef4444',
          marginBottom: '16px',
          fontSize: '28px',
          fontWeight: '700'
        }}>
          System Critical Error
        </h2>

        {/* Error Message */}
        <p style={{
          color: 'rgba(255, 255, 255, 0.8)',
          fontSize: '15px',
          lineHeight: '1.6',
          marginBottom: '24px'
        }}>
          {errorMessage || 'An unexpected error occurred. The application encountered an unhandled exception.'}
        </p>

        {/* Technical Details */}
        <div style={{
          background: 'rgba(0, 0, 0, 0.4)',
          borderRadius: '8px',
          padding: '16px',
          marginBottom: '24px',
          textAlign: 'left'
        }}>
          <p style={{
            color: 'rgba(255, 255, 255, 0.6)',
            fontSize: '12px',
            marginBottom: '8px',
            textTransform: 'uppercase',
            letterSpacing: '1px'
          }}>
            Technical Details
          </p>
          <p style={{
            color: 'rgba(255, 255, 255, 0.5)',
            fontSize: '12px',
            fontFamily: 'monospace',
            wordBreak: 'break-word'
          }}>
            Uncaught JavaScript exception in React component tree.
            Check browser console for stack trace.
          </p>
        </div>

        {/* Trace ID */}
        {traceId && (
          <div style={{
            display: 'inline-block',
            padding: '8px 16px',
            background: 'rgba(0, 0, 0, 0.3)',
            borderRadius: '4px',
            fontSize: '12px',
            fontFamily: 'monospace',
            color: 'rgba(255, 255, 255, 0.7)',
            marginBottom: '32px',
            wordBreak: 'break-all'
          }}>
            Reference ID: {traceId}
          </div>
        )}

        {/* Action Buttons */}
        <div style={{
          display: 'flex',
          gap: '12px',
          justifyContent: 'center',
          flexWrap: 'wrap'
        }}>
          <button
            onClick={handleReturn}
            style={{
              background: '#ef4444',
              border: 'none',
              borderRadius: '8px',
              padding: '14px 28px',
              color: '#fff',
              cursor: 'pointer',
              fontSize: '15px',
              fontWeight: '600'
            }}
          >
            Return to Dashboard
          </button>
          
          {onRetry && (
            <button
              onClick={onRetry}
              style={{
                background: 'transparent',
                border: '1px solid rgba(239, 68, 68, 0.5)',
                borderRadius: '8px',
                padding: '14px 28px',
                color: '#ef4444',
                cursor: 'pointer',
                fontSize: '15px',
                fontWeight: '600'
              }}
            >
              Try Again
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

/**
 * ErrorBoundary - React class component that catches JavaScript errors in child component tree
 * 
 * Features:
 * - Catches unhandled exceptions in React components
 * - Prevents white screen of death
 * - Displays SystemCrash overlay with trace_id
 * - Provides "Return to Dashboard" action
 * - Supports optional retry functionality
 * 
 * Usage:
 *   <ErrorBoundary>
 *     <GravitasDocumentView />
 *   </ErrorBoundary>
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    // Log error to console for debugging
    console.error('ErrorBoundary caught unhandled error:', error, errorInfo)
    
    // Store error info for potential reporting
    this.setState({ errorInfo })
    
    // Optionally report to error tracking service
    this._reportError(error, errorInfo)
  }

  /**
   * Report error to external tracking service (if configured)
   */
  _reportError(error, errorInfo) {
    // Could integrate with Sentry, Datadog, etc.
    const traceId = window.__gravitas_active_trace_id || null
    
    // Build error payload
    const errorPayload = {
      message: error?.message || 'Unknown error',
      stack: error?.stack || '',
      componentStack: errorInfo?.componentStack || '',
      traceId,
      timestamp: new Date().toISOString(),
      userAgent: navigator?.userAgent || ''
    }
    
    // Log for now - could be sent to backend
    console.error('Error payload for reporting:', errorPayload)
  }

  /**
   * Reset error state to attempt recovery
   */
  handleRetry = () => {
    this.setState({ hasError: false, error: null, errorInfo: null })
  }

  /**
   * Navigate to dashboard
   */
  handleReturnToDashboard = () => {
    window.location.href = '/'
  }

  render() {
    if (this.state.hasError) {
      const traceId = this.props.traceId || window.__gravitas_active_trace_id || null
      const errorMessage = this.state.error?.message || 'An unexpected error occurred'
      const { onReturnToDashboard, onRetry } = this.props

      // Use custom fallback if provided, otherwise default SystemCrash
      if (this.props.fallback) {
        return this.props.fallback({
          error: this.state.error,
          errorInfo: this.state.errorInfo,
          traceId,
          onRetry: this.handleRetry,
          onReturnToDashboard: onReturnToDashboard || this.handleReturnToDashboard
        })
      }

      return (
        <SystemCrash
          traceId={traceId}
          errorMessage={errorMessage}
          onReturnToDashboard={onReturnToDashboard || this.handleReturnToDashboard}
          onRetry={onRetry || this.handleRetry}
        />
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary

// Also export SystemCrash for direct usage if needed
export { SystemCrash }
