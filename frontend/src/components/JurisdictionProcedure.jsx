import React, { useState, useEffect } from 'react'
import { procedureService } from '../services/nyayaApi.js'

const JurisdictionProcedure = ({ onBack }) => {
  const [selectedJurisdiction, setSelectedJurisdiction] = useState('India')
  const [selectedDomain, setSelectedDomain] = useState('civil')
  const [procedures, setProcedures] = useState(null)
  const [loading, setLoading] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)

  const jurisdictionMap = {
    'India': 'IN',
    'UK': 'UK',
    'UAE': 'UAE'
  }

  useEffect(() => {
    fetchProcedures()
  }, [selectedJurisdiction, selectedDomain])

  const fetchProcedures = async () => {
    setLoading(true)
    const country = jurisdictionMap[selectedJurisdiction]
    const result = await procedureService.getProcedureSummary(country, selectedDomain)
    
    if (result.success && result.data) {
      setProcedures(result.data)
    }
    setLoading(false)
  }

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <button
        onClick={onBack}
        style={{
          background: 'rgba(255, 255, 255, 0.1)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderRadius: '8px',
          padding: '10px 20px',
          color: '#fff',
          cursor: 'pointer',
          marginBottom: '20px',
          fontSize: '14px'
        }}
      >
        ← Back to Dashboard
      </button>

      <div style={{
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '16px',
        padding: '32px'
      }}>
        <h2 style={{ color: '#fff', fontSize: '24px', marginBottom: '24px' }}>Jurisdiction Procedure Navigator</h2>

        {/* Jurisdiction Selector */}
        <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
          {['India', 'UK', 'UAE'].map(jurisdiction => (
            <button
              key={jurisdiction}
              onClick={() => {
                setSelectedJurisdiction(jurisdiction)
                setCurrentStep(0)
              }}
              style={{
                padding: '12px 24px',
                border: selectedJurisdiction === jurisdiction ? '2px solid #8b5cf6' : '2px solid rgba(255, 255, 255, 0.2)',
                borderRadius: '8px',
                background: selectedJurisdiction === jurisdiction ? 'rgba(139, 92, 246, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                color: '#fff',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '600'
              }}
            >
              {jurisdiction}
            </button>
          ))}
        </div>

        {/* Domain Selector */}
        <div style={{ display: 'flex', gap: '12px', marginBottom: '32px' }}>
          {['civil', 'criminal', 'constitutional'].map(domain => (
            <button
              key={domain}
              onClick={() => setSelectedDomain(domain)}
              style={{
                padding: '8px 16px',
                border: selectedDomain === domain ? '2px solid #3b82f6' : '2px solid rgba(255, 255, 255, 0.2)',
                borderRadius: '8px',
                background: selectedDomain === domain ? 'rgba(59, 130, 246, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                color: '#fff',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: '600',
                textTransform: 'capitalize'
              }}
            >
              {domain}
            </button>
          ))}
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'rgba(255, 255, 255, 0.6)' }}>
            Loading procedures from backend...
          </div>
        ) : procedures ? (
          <div style={{
            padding: '20px',
            background: 'rgba(255, 255, 255, 0.05)',
            borderRadius: '12px'
          }}>
            <pre style={{
              color: 'rgba(255, 255, 255, 0.9)',
              fontSize: '13px',
              lineHeight: '1.6',
              margin: 0,
              whiteSpace: 'pre-wrap',
              wordWrap: 'break-word'
            }}>
              {JSON.stringify(procedures, null, 2)}
            </pre>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px', color: 'rgba(255, 255, 255, 0.6)' }}>
            No procedures available
          </div>
        )}
      </div>
    </div>
  )
}

export default JurisdictionProcedure
