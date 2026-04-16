// ApiErrorState.jsx — Shared error state for backend validation failures
// Displays trace_id and a Report Issue button. Never shows generic fallback strings.
import React from 'react'

const ApiErrorState = ({ title, message, traceId, onRetry }) => (
  <div className="consultation-card">
    <div style={{ textAlign: 'center', padding: '24px' }}>
      <div style={{ fontSize: '32px', marginBottom: '12px' }}>⚠️</div>
      <h3 style={{ color: '#dc3545', marginBottom: '8px', fontSize: '16px', fontWeight: '600' }}>
        {title || 'Data Unavailable'}
      </h3>
      <p style={{ color: '#6c757d', fontSize: '13px', lineHeight: '1.5', marginBottom: '16px' }}>
        {message || 'The backend returned an incomplete or invalid response.'}
      </p>

      {traceId && (
        <div style={{
          display: 'inline-block',
          padding: '6px 12px',
          backgroundColor: '#f8f9fa',
          border: '1px solid #dee2e6',
          borderRadius: '4px',
          fontSize: '11px',
          fontFamily: 'monospace',
          color: '#495057',
          marginBottom: '16px',
          wordBreak: 'break-all'
        }}>
          Reference ID: {traceId}
        </div>
      )}

      <div style={{ display: 'flex', gap: '10px', justifyContent: 'center', flexWrap: 'wrap' }}>
        {onRetry && (
          <button
            onClick={onRetry}
            style={{
              padding: '8px 16px',
              backgroundColor: '#007bff',
              color: '#fff',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: '500'
            }}
          >
            Retry
          </button>
        )}
        {traceId && (
          <button
            onClick={() => {
              const subject = encodeURIComponent(`Gravitas UI Error — Trace ${traceId}`)
              const body = encodeURIComponent(`Reference ID: ${traceId}\nError: ${message}\n\nPlease investigate.`)
              window.open(`mailto:support@nyaya.ai?subject=${subject}&body=${body}`)
            }}
            style={{
              padding: '8px 16px',
              backgroundColor: 'transparent',
              color: '#dc3545',
              border: '1px solid #dc3545',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: '500'
            }}
          >
            Report Issue
          </button>
        )}
      </div>
    </div>
  </div>
)

export default ApiErrorState
