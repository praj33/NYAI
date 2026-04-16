/**
 * EscalationNotice.jsx
 * Rendered when enforcement state is 'escalate'.
 *
 * Renders: DecisionHeader, CaseContext, ProceduralSteps, DecisionTimeline.
 * Does NOT render: Determination (decision + reasoning strings are withheld).
 * Overlays a sticky banner indicating the file has been routed to human counsel.
 */
import React from 'react'
import DecisionHeader from './DecisionHeader.jsx'
import CaseContext from './CaseContext.jsx'
import ProceduralSteps from './ProceduralSteps.jsx'
import DecisionTimeline from './DecisionTimeline.jsx'

const EscalationNotice = ({
  traceId,
  enforcementStatus,
  jurisdiction,
  caseSummary,
  legalRoute,
  proceduralSteps,
  timeline
}) => (
  <article style={{
    backgroundColor: '#fff',
    border: '1px solid #d1d5db',
    borderRadius: '8px',
    overflow: 'hidden',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
  }}>
    {/* Standard document header */}
    <DecisionHeader
      traceId={traceId}
      enforcementStatus={enforcementStatus}
      jurisdiction={jurisdiction}
    />

    {/* Escalation banner — sticky within scroll context */}
    <div style={{
      backgroundColor: '#fff7ed',
      borderBottom: '2px solid #f97316',
      padding: '16px 40px',
      display: 'flex',
      alignItems: 'flex-start',
      gap: '14px'
    }}>
      <span style={{ fontSize: '22px', flexShrink: 0, marginTop: '2px' }}>⚖️</span>
      <div style={{ flex: 1 }}>
        <div style={{
          fontSize: '11px', fontWeight: '700', letterSpacing: '2px',
          textTransform: 'uppercase', color: '#c2410c', marginBottom: '4px'
        }}>
          Escalation Required — Awaiting Human Review
        </div>
        <p style={{ margin: '0 0 6px 0', fontSize: '13px', color: '#7c2d12', lineHeight: '1.6' }}>
          {enforcementStatus?.reason || 'This case has been routed to human legal counsel for review before a final automated determination can be issued.'}
        </p>
        {enforcementStatus?.escalation_target && (
          <p style={{ margin: 0, fontSize: '12px', color: '#9a3412' }}>
            <strong>Escalation target:</strong> {enforcementStatus.escalation_target}
          </p>
        )}
      </div>
      <code style={{
        flexShrink: 0, fontSize: '10px', fontFamily: '"Courier New", monospace',
        color: '#9ca3af', backgroundColor: '#f3f4f6',
        padding: '4px 8px', borderRadius: '4px', alignSelf: 'center'
      }}>
        {traceId}
      </code>
    </div>

    {/* Permitted sections */}
    <CaseContext caseSummary={caseSummary} legalRoute={legalRoute} />
    <ProceduralSteps proceduralSteps={proceduralSteps} />
    <DecisionTimeline timeline={timeline} />

    {/* Determination placeholder — decision string is NOT rendered */}
    <section style={{
      padding: '32px 40px',
      borderTop: '1px solid #e5e7eb',
      backgroundColor: '#f9fafb'
    }}>
      <div style={{
        padding: '28px 32px',
        border: '2px dashed #d1d5db',
        borderRadius: '8px',
        textAlign: 'center'
      }}>
        <span style={{ fontSize: '28px', display: 'block', marginBottom: '12px' }}>⏳</span>
        <p style={{
          margin: 0, fontSize: '14px', color: '#6b7280',
          fontStyle: 'italic', lineHeight: '1.6'
        }}>
          Final determination is pending human legal review.<br />
          This section will be available once counsel has completed their assessment.
        </p>
      </div>
    </section>
  </article>
)

export default EscalationNotice
