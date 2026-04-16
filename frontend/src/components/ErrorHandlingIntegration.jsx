// ErrorHandlingIntegration.jsx — Integration wrapper demonstrating Phase 5 error & failure handling
// Shows how ErrorBoundary, ServiceOutage, and casePayloadValidator work together
// to prevent white screen of death and handle backend outages gracefully.

import React, { useState, useEffect } from 'react'
import ErrorBoundary, { SystemCrash } from './components/ErrorBoundary.jsx'
import ServiceOutage from './components/ServiceOutage.jsx'
import GravitasDocumentView from './components/document/GravitasDocumentView.jsx'
import EnforcementGatekeeper from './components/document/EnforcementGatekeeper.jsx'
import { useServiceOutage } from './hooks/useServiceOutage.js'
import { validateCasePayload } from './lib/casePayloadValidator.js'

/**
 * ErrorHandlingIntegration - Complete error & failure handling wrapper
 * 
 * This component demonstrates the multi-layered defense system:
 * 
 * LAYER 1: Service Outage Detection
 *   - Global axios interceptor detects 5xx/E-CONNREFUSED/timeout
 *   - useServiceOutage hook provides isServiceOutage state
 *   - Renders ServiceOutage component when backend is down
 * 
 * LAYER 2: Schema Validation
 *   - validateCasePayload sanitizes incoming decision object
 *   - Non-critical fields (procedural_steps, timeline) get fallbacks
 *   - Critical fields throw errors that bubble to ErrorBoundary
 * 
 * LAYER 3: React ErrorBoundary
 *   - Catches unhandled JavaScript exceptions
 *   - Prevents white screen of death
 *   - Renders SystemCrash overlay with trace_id
 * 
 * @param {{
 *   casePayload: import('./lib/gravitas.types').CasePayload,
 *   onFeedback?: Function,
 *   traceId?: string
 * }} props
 */
function ErrorHandlingIntegration({ casePayload, onFeedback, traceId }) {
  // Layer 1: Subscribe to backend service outage state
  const { isServiceOutage, outageError, clearOutage } = useServiceOutage()
  
  // Layer 2: Validate and sanitize casePayload before rendering
  const [validatedPayload, setValidatedPayload] = useState(null)
  const [validationError, setValidationError] = useState(null)
  
  useEffect(() => {
    if (!casePayload) {
      setValidatedPayload(null)
      setValidationError(null)
      return
    }
    
    // Validate with non-strict mode (provides fallbacks for missing non-critical fields)
    const result = validateCasePayload(casePayload, false)
    
    if (result.valid) {
      setValidatedPayload(result.sanitized)
      setValidationError(null)
    } else {
      // Validation failed - in strict mode we'd throw, here we show error state
      setValidatedPayload(null)
      setValidationError(result.error)
    }
  }, [casePayload])
  
  // If backend is down, show ServiceOutage (Layer 1)
  if (isServiceOutage) {
    return (
      <ServiceOutage
        traceId={outageError?.trace_id || traceId || window.__gravitas_active_trace_id}
        onReturnToDashboard={() => {
          clearOutage()
          window.location.href = '/'
        }}
      />
    )
  }
  
  // If validation failed for critical fields, show error (Layer 2)
  if (validationError) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <h2 style={{ color: '#dc3545', marginBottom: '16px' }}>
          Decision Document Unavailable
        </h2>
        <p style={{ color: 'rgba(255,255,255,0.7)', marginBottom: '16px' }}>
          {validationError}
        </p>
        {traceId && (
          <p style={{ color: 'rgba(255,255,255,0.5)', fontSize: '12px', fontFamily: 'monospace' }}>
            Reference ID: {traceId}
          </p>
        )}
        <button
          onClick={() => window.location.reload()}
          style={{
            marginTop: '20px',
            padding: '10px 20px',
            background: '#dc3545',
            border: 'none',
            borderRadius: '6px',
            color: '#fff',
            cursor: 'pointer'
          }}
        >
          Retry
        </button>
      </div>
    )
  }
  
  // Layer 3: Wrap in ErrorBoundary to catch any remaining exceptions
  return (
    <ErrorBoundary
      traceId={traceId || validatedPayload?.trace_id}
      onReturnToDashboard={() => window.location.href = '/'}
      onRetry={() => window.location.reload()}
    >
      {/* EnforcementGatekeeper applies enforcement logic before rendering document */}
      <EnforcementGatekeeper casePayload={validatedPayload}>
        {(enforcementState) => (
          <GravitasDocumentView
            casePayload={validatedPayload}
            onFeedback={onFeedback}
          />
        )}
      </EnforcementGatekeeper>
    </ErrorBoundary>
  )
}

/**
 * Example usage in App.jsx:
 * 
 * import ErrorHandlingIntegration from './ErrorHandlingIntegration.jsx'
 * 
 * function App() {
 *   const [casePayload, setCasePayload] = useState(null)
 *   const [traceId, setTraceId] = useState(null)
 * 
 *   return (
 *     <ErrorHandlingIntegration
 *       casePayload={casePayload}
 *       traceId={traceId}
 *       onFeedback={(id) => console.log('Feedback for:', id)}
 *     />
 *   )
 * }
 */

// Also export individual layers for granular control
export { ErrorBoundary, SystemCrash, ServiceOutage }
export { validateCasePayload } from './lib/casePayloadValidator.js'
export { useServiceOutage } from './hooks/useServiceOutage.js'

export default ErrorHandlingIntegration
