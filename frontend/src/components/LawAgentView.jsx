import React from 'react'

const LawAgentView = ({ responseData }) => {
  if (!responseData) {
    return (
      <div style={{
        maxWidth: '900px',
        margin: '0 auto',
        padding: '40px 20px'
      }}>
        <div style={{
          background: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: '12px',
          padding: '60px 40px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>⚖️</div>
          <h2 style={{ color: '#fff', fontSize: '24px', marginBottom: '12px', fontWeight: '600' }}>
            No Evaluated Case
          </h2>
          <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '14px' }}>
            Submit a legal query to view structured analysis
          </p>
        </div>
      </div>
    )
  }

  const { 
    domain, 
    jurisdiction, 
    jurisdiction_detected,
    confidence, 
    statutes = [], 
    reasoning_trace = {},
    legal_route = [],
    trace_id,
    enforcement_decision
  } = responseData

  const { 
    legal_analysis = '', 
    procedural_steps = [], 
    remedies = [],
    timeline = {}
  } = reasoning_trace

  const enforcementState = enforcement_decision || 'ALLOW'
  const enforcementColors = {
    'ALLOW': { bg: 'rgba(34, 197, 94, 0.1)', border: '#22c55e', text: '#22c55e' },
    'BLOCK': { bg: 'rgba(239, 68, 68, 0.1)', border: '#ef4444', text: '#ef4444' },
    'ESCALATE': { bg: 'rgba(249, 115, 22, 0.1)', border: '#f97316', text: '#f97316' },
    'SOFT_REDIRECT': { bg: 'rgba(59, 130, 246, 0.1)', border: '#3b82f6', text: '#3b82f6' }
  }

  const colors = enforcementColors[enforcementState] || enforcementColors['ALLOW']

  return (
    <div style={{
      maxWidth: '900px',
      margin: '0 auto',
      padding: '20px',
      display: 'flex',
      flexDirection: 'column',
      gap: '24px'
    }}>
      {/* SECTION 1 - Case Summary */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '12px',
        padding: '24px'
      }}>
        <h3 style={{ 
          color: '#fff', 
          fontSize: '14px', 
          fontWeight: '700', 
          textTransform: 'uppercase',
          letterSpacing: '1px',
          marginBottom: '16px',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          paddingBottom: '12px'
        }}>
          SECTION 1 — Case Summary
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '13px' }}>Jurisdiction</span>
            <span style={{ color: '#fff', fontSize: '13px', fontWeight: '600' }}>
              {jurisdiction_detected || jurisdiction || 'Not specified'}
            </span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '13px' }}>Domain</span>
            <span style={{ color: '#fff', fontSize: '13px', fontWeight: '600' }}>
              {domain || 'Not specified'}
            </span>
          </div>
          {legal_route && legal_route.length > 0 && (
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '13px' }}>Legal Route</span>
              <span style={{ color: '#fff', fontSize: '13px', fontWeight: '600' }}>
                {legal_route.join(' → ')}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* SECTION 2 - Procedural Steps */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '12px',
        padding: '24px'
      }}>
        <h3 style={{ 
          color: '#fff', 
          fontSize: '14px', 
          fontWeight: '700', 
          textTransform: 'uppercase',
          letterSpacing: '1px',
          marginBottom: '16px',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          paddingBottom: '12px'
        }}>
          SECTION 2 — Procedural Steps
        </h3>
        {procedural_steps && procedural_steps.length > 0 ? (
          <ol style={{ margin: 0, paddingLeft: '20px', color: '#fff', fontSize: '13px', lineHeight: '1.8' }}>
            {procedural_steps.map((step, idx) => (
              <li key={idx} style={{ marginBottom: '8px' }}>{step}</li>
            ))}
          </ol>
        ) : (
          <p style={{ color: 'rgba(255, 255, 255, 0.5)', fontSize: '13px', margin: 0 }}>Not available</p>
        )}
      </div>

      {/* SECTION 3 - Timeline */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '12px',
        padding: '24px'
      }}>
        <h3 style={{ 
          color: '#fff', 
          fontSize: '14px', 
          fontWeight: '700', 
          textTransform: 'uppercase',
          letterSpacing: '1px',
          marginBottom: '16px',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          paddingBottom: '12px'
        }}>
          SECTION 3 — Timeline
        </h3>
        {timeline && (timeline.min_duration || timeline.max_duration) ? (
          <div style={{ color: '#fff', fontSize: '13px' }}>
            <span style={{ color: 'rgba(255, 255, 255, 0.6)' }}>Duration Range: </span>
            <span style={{ fontWeight: '600' }}>
              {timeline.min_duration || 'N/A'} - {timeline.max_duration || 'N/A'}
            </span>
          </div>
        ) : (
          <p style={{ color: 'rgba(255, 255, 255, 0.5)', fontSize: '13px', margin: 0 }}>Not available</p>
        )}
      </div>

      {/* SECTION 4 - Evidence Required */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '12px',
        padding: '24px'
      }}>
        <h3 style={{ 
          color: '#fff', 
          fontSize: '14px', 
          fontWeight: '700', 
          textTransform: 'uppercase',
          letterSpacing: '1px',
          marginBottom: '16px',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          paddingBottom: '12px'
        }}>
          SECTION 4 — Evidence Required
        </h3>
        {statutes && statutes.length > 0 ? (
          <ul style={{ margin: 0, paddingLeft: '20px', color: '#fff', fontSize: '13px', lineHeight: '1.8' }}>
            {statutes.map((statute, idx) => (
              <li key={idx} style={{ marginBottom: '8px' }}>
                {statute.section_id || statute.title || statute}
              </li>
            ))}
          </ul>
        ) : (
          <p style={{ color: 'rgba(255, 255, 255, 0.5)', fontSize: '13px', margin: 0 }}>Not available</p>
        )}
      </div>

      {/* SECTION 5 - Enforcement Decision */}
      <div style={{
        background: colors.bg,
        backdropFilter: 'blur(10px)',
        border: `2px solid ${colors.border}`,
        borderRadius: '12px',
        padding: '24px'
      }}>
        <h3 style={{ 
          color: '#fff', 
          fontSize: '14px', 
          fontWeight: '700', 
          textTransform: 'uppercase',
          letterSpacing: '1px',
          marginBottom: '16px',
          borderBottom: `1px solid ${colors.border}`,
          paddingBottom: '12px'
        }}>
          SECTION 5 — Enforcement Decision
        </h3>
        <div style={{ 
          fontSize: '32px', 
          fontWeight: '700', 
          color: colors.text,
          marginBottom: '12px',
          letterSpacing: '2px'
        }}>
          {enforcementState}
        </div>
        {legal_analysis && (
          <p style={{ color: '#fff', fontSize: '13px', lineHeight: '1.6', margin: '12px 0' }}>
            {legal_analysis}
          </p>
        )}
        {trace_id && (
          <div style={{ 
            marginTop: '16px', 
            paddingTop: '16px', 
            borderTop: `1px solid ${colors.border}` 
          }}>
            <span style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '11px' }}>Trace ID: </span>
            <code style={{ 
              color: colors.text, 
              fontSize: '11px', 
              fontFamily: 'monospace',
              background: 'rgba(0, 0, 0, 0.2)',
              padding: '4px 8px',
              borderRadius: '4px'
            }}>
              {trace_id}
            </code>
          </div>
        )}
      </div>
    </div>
  )
}

export default LawAgentView
