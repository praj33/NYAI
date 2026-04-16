/**
 * RedirectModal.jsx
 * Rendered when enforcement state is 'soft_redirect'.
 *
 * The full document renders underneath. A non-blocking overlay appears
 * suggesting the alternative path with a clear CTA. The user can dismiss
 * it and continue reading the current document.
 */
import React, { useState } from 'react'

const RedirectModal = ({ redirectSuggestion, safeExplanation, traceId, onDismiss }) => {
  const [dismissed, setDismissed] = useState(false)

  if (dismissed) return null

  const handleDismiss = () => {
    setDismissed(true)
    onDismiss?.()
  }

  return (
    <div style={{
      position: 'fixed',
      bottom: '32px',
      right: '32px',
      zIndex: 1500,
      width: '380px',
      maxWidth: 'calc(100vw - 48px)',
      backgroundColor: '#fff',
      border: '1.5px solid #7c3aed',
      borderRadius: '10px',
      boxShadow: '0 8px 32px rgba(124, 58, 237, 0.18)',
      overflow: 'hidden',
      animation: 'rdm-slidein 0.3s ease-out'
    }}>
      <style>{`
        @keyframes rdm-slidein {
          from { opacity: 0; transform: translateY(16px); }
          to   { opacity: 1; transform: translateY(0); }
        }
      `}</style>

      {/* Header */}
      <div style={{
        backgroundColor: '#7c3aed',
        padding: '14px 18px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '18px' }}>↩️</span>
          <div>
            <div style={{ fontSize: '10px', fontWeight: '700', letterSpacing: '1.5px', textTransform: 'uppercase', color: 'rgba(255,255,255,0.7)' }}>
              Alternative Route Available
            </div>
            <div style={{ fontSize: '13px', fontWeight: '600', color: '#fff' }}>
              Recommended Redirect
            </div>
          </div>
        </div>
        <button
          onClick={handleDismiss}
          aria-label="Dismiss redirect suggestion"
          style={{
            background: 'none', border: 'none', color: 'rgba(255,255,255,0.7)',
            fontSize: '18px', cursor: 'pointer', lineHeight: 1, padding: '2px 4px'
          }}
        >
          ×
        </button>
      </div>

      <div style={{ padding: '18px' }}>
        {/* Explanation */}
        {safeExplanation && (
          <p style={{ margin: '0 0 14px 0', fontSize: '13px', color: '#374151', lineHeight: '1.6' }}>
            {safeExplanation}
          </p>
        )}

        {/* Redirect suggestion */}
        {redirectSuggestion && (
          <div style={{
            padding: '12px 14px', backgroundColor: '#f5f3ff',
            border: '1px solid #ddd6fe', borderRadius: '6px', marginBottom: '16px'
          }}>
            <div style={{ fontSize: '10px', fontWeight: '700', color: '#6d28d9', letterSpacing: '1px', textTransform: 'uppercase', marginBottom: '6px' }}>
              Suggested Alternative
            </div>
            <p style={{ margin: 0, fontSize: '13px', color: '#4c1d95', lineHeight: '1.6', fontWeight: '500' }}>
              {redirectSuggestion}
            </p>
          </div>
        )}

        {/* CTA */}
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={handleDismiss}
            style={{
              flex: 1, padding: '9px 14px',
              backgroundColor: '#7c3aed', color: '#fff',
              border: 'none', borderRadius: '6px',
              fontSize: '13px', fontWeight: '600', cursor: 'pointer'
            }}
          >
            Explore Alternative
          </button>
          <button
            onClick={handleDismiss}
            style={{
              padding: '9px 14px',
              backgroundColor: 'transparent', color: '#6b7280',
              border: '1px solid #d1d5db', borderRadius: '6px',
              fontSize: '13px', cursor: 'pointer'
            }}
          >
            Continue
          </button>
        </div>

        {/* Trace reference */}
        <div style={{ marginTop: '12px', textAlign: 'right' }}>
          <code style={{ fontSize: '10px', fontFamily: '"Courier New", monospace', color: '#d1d5db' }}>
            {traceId}
          </code>
        </div>
      </div>
    </div>
  )
}

export default RedirectModal
