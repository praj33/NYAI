/**
 * DecisionHeader.jsx
 * Fields consumed: trace_id, enforcement_status, jurisdiction
 *
 * Verdict → header accent:
 *   ENFORCEABLE     → green  ✅
 *   PENDING_REVIEW  → amber  ⏳
 *   NON_ENFORCEABLE → red    🚫
 */
import React from 'react'

const VERDICT_CONFIG = {
  ENFORCEABLE: {
    color: '#1a7f4b', bg: '#d1fae5', border: '#6ee7b7',
    icon: '✅', label: 'Enforceable'
  },
  PENDING_REVIEW: {
    color: '#92400e', bg: '#fef3c7', border: '#fcd34d',
    icon: '⏳', label: 'Pending Review'
  },
  NON_ENFORCEABLE: {
    color: '#991b1b', bg: '#fee2e2', border: '#fca5a5',
    icon: '🚫', label: 'Non-Enforceable'
  }
}

const DecisionHeader = ({ traceId, enforcementStatus, jurisdiction }) => {
  const verdict = enforcementStatus?.verdict ?? 'PENDING_REVIEW'
  const cfg = VERDICT_CONFIG[verdict] ?? VERDICT_CONFIG.PENDING_REVIEW

  return (
    <header style={{
      borderBottom: `3px solid ${cfg.border}`,
      backgroundColor: cfg.bg,
      padding: '28px 40px 20px'
    }}>
      <div style={{
        fontSize: '11px', fontWeight: '700', letterSpacing: '2px',
        textTransform: 'uppercase', color: '#6b7280', marginBottom: '8px'
      }}>
        Legal Decision Document
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{
            margin: '0 0 10px 0', fontSize: '1.75rem', fontWeight: '700',
            color: '#111827', fontFamily: 'Georgia, "Times New Roman", serif'
          }}>
            {jurisdiction}
          </h1>

          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: '8px',
            padding: '6px 14px', backgroundColor: 'white',
            border: `1.5px solid ${cfg.border}`, borderRadius: '20px',
            fontSize: '13px', fontWeight: '600', color: cfg.color
          }}>
            <span>{cfg.icon}</span>
            <span>{cfg.label}</span>
          </div>

          {enforcementStatus?.reason && (
            <p style={{ margin: '10px 0 0 0', fontSize: '13px', color: cfg.color, maxWidth: '520px', lineHeight: '1.5' }}>
              {enforcementStatus.reason}
            </p>
          )}
        </div>

        {/* Audit trace_id — top-right */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px' }}>
          <span style={{ fontSize: '10px', fontWeight: '600', color: '#9ca3af', letterSpacing: '1px', textTransform: 'uppercase' }}>
            Reference ID
          </span>
          <code style={{
            fontSize: '11px', fontFamily: '"Courier New", monospace',
            color: '#374151', backgroundColor: 'rgba(0,0,0,0.05)',
            padding: '4px 10px', borderRadius: '4px'
          }}>
            {traceId}
          </code>
        </div>
      </div>

      {/* Enforcement barriers — NON_ENFORCEABLE only */}
      {verdict === 'NON_ENFORCEABLE' && enforcementStatus?.barriers?.length > 0 && (
        <div style={{
          marginTop: '16px', padding: '12px 16px',
          backgroundColor: '#fee2e2', border: '1px solid #fca5a5', borderRadius: '6px'
        }}>
          <div style={{ fontSize: '12px', fontWeight: '700', color: '#991b1b', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            Enforcement Barriers
          </div>
          <ul style={{ margin: 0, paddingLeft: '18px' }}>
            {enforcementStatus.barriers.map((barrier, i) => (
              <li key={i} style={{ fontSize: '13px', color: '#7f1d1d', lineHeight: '1.6' }}>{barrier}</li>
            ))}
          </ul>
        </div>
      )}
    </header>
  )
}

export default DecisionHeader
