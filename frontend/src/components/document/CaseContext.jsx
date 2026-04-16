/**
 * CaseContext.jsx
 * Fields consumed: case_summary, legal_route
 */
import React from 'react'

const SectionLabel = ({ children }) => (
  <div style={{
    fontSize: '10px', fontWeight: '700', letterSpacing: '2px',
    textTransform: 'uppercase', color: '#6b7280', marginBottom: '10px',
    paddingBottom: '6px', borderBottom: '1px solid #e5e7eb'
  }}>
    {children}
  </div>
)

const CaseContext = ({ caseSummary, legalRoute }) => (
  <section style={{ padding: '32px 40px', borderBottom: '1px solid #e5e7eb' }}>
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '40px' }}>

      {/* Findings of Fact */}
      <div>
        <SectionLabel>Findings of Fact</SectionLabel>
        <p style={{
          margin: 0, fontSize: '14px', lineHeight: '1.8',
          color: '#374151', fontFamily: 'Georgia, "Times New Roman", serif'
        }}>
          {caseSummary}
        </p>
      </div>

      {/* Statutory / Regulatory Framework */}
      <div>
        <SectionLabel>Statutory Framework Applied</SectionLabel>
        {legalRoute.length === 0 ? (
          <p style={{ margin: 0, fontSize: '13px', color: '#9ca3af', fontStyle: 'italic' }}>
            No statutory framework recorded.
          </p>
        ) : (
          <ol style={{ margin: 0, paddingLeft: '18px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {legalRoute.map((item, i) => (
              <li key={i} style={{
                fontSize: '13px', color: '#374151', lineHeight: '1.6',
                paddingLeft: '4px'
              }}>
                {item}
              </li>
            ))}
          </ol>
        )}
      </div>
    </div>
  </section>
)

export default CaseContext
