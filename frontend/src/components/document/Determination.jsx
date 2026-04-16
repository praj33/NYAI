/**
 * Determination.jsx
 * Fields consumed: decision, reasoning
 *
 * The ultimate ruling is rendered with maximum typographic emphasis.
 * Reasoning is the logical justification connecting facts to the decision.
 */
import React from 'react'

const Determination = ({ decision, reasoning }) => (
  <section style={{ padding: '32px 40px' }}>

    {/* The Ruling */}
    <div style={{
      marginBottom: '32px',
      padding: '28px 32px',
      backgroundColor: '#1e3a5f',
      borderRadius: '8px',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Decorative rule mark */}
      <div style={{
        position: 'absolute', top: 0, left: 0, bottom: 0,
        width: '5px', backgroundColor: '#f59e0b'
      }} />

      <div style={{
        fontSize: '10px', fontWeight: '700', letterSpacing: '2px',
        textTransform: 'uppercase', color: '#93c5fd', marginBottom: '14px'
      }}>
        Final Determination
      </div>

      <p style={{
        margin: 0,
        fontSize: '1.2rem',
        fontWeight: '700',
        color: '#f9fafb',
        fontFamily: 'Georgia, "Times New Roman", serif',
        lineHeight: '1.7',
        letterSpacing: '0.1px'
      }}>
        {decision}
      </p>
    </div>

    {/* Reasoning */}
    <div>
      <div style={{
        fontSize: '10px', fontWeight: '700', letterSpacing: '2px',
        textTransform: 'uppercase', color: '#6b7280', marginBottom: '12px',
        paddingBottom: '6px', borderBottom: '1px solid #e5e7eb'
      }}>
        Reasoning &amp; Justification
      </div>

      <p style={{
        margin: 0,
        fontSize: '14px',
        color: '#374151',
        lineHeight: '1.9',
        fontFamily: 'Georgia, "Times New Roman", serif'
      }}>
        {reasoning}
      </p>
    </div>
  </section>
)

export default Determination
