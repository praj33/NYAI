import React, { useState } from 'react'
import ProceduralTimeline from './ProceduralTimeline.jsx'
import FeedbackButtons from './FeedbackButtons.jsx'
import { legalQueryService } from '../services/nyayaApi.js'

const MultiJurisdictionCard = () => {
  const [query, setQuery] = useState('')
  const [selectedJurisdictions, setSelectedJurisdictions] = useState(['India'])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [comparativeAnalysis, setComparativeAnalysis] = useState(null)
  const [traceId, setTraceId] = useState(null)
  const [error, setError] = useState(null)

  const availableJurisdictions = [
    { id: 'India', name: 'India', description: 'Comprehensive analysis under Indian law' },
    { id: 'UK', name: 'United Kingdom', description: 'UK legal framework and precedents' },
    { id: 'UAE', name: 'United Arab Emirates', description: 'UAE civil and commercial law' }
  ]

  const toggleJurisdiction = (jurisdiction) => {
    setSelectedJurisdictions(prev => 
      prev.includes(jurisdiction) 
        ? prev.filter(j => j !== jurisdiction)
        : [...prev, jurisdiction]
    )
  }

  const handleAnalyze = async () => {
    if (!query.trim() || selectedJurisdictions.length === 0) return

    setIsAnalyzing(true)
    setError(null)
    
    // Call real Nyaya AI backend
    try {
      const result = await legalQueryService.submitMultiJurisdictionQuery({
        query: query,
        jurisdictions: selectedJurisdictions
      })
      
      if (result.success) {
        setTraceId(result.trace_id)
        setComparativeAnalysis(result.data)
      } else {
        setError(result.error || 'Failed to get response from backend')
      }
    } catch (error) {
      console.error('Error:', error)
      setError(error.message || 'Failed to connect to backend')
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="consultation-card">
      {/* Advisory-Style Heading */}
      <h2 style={{
        fontSize: '1.5rem',
        color: '#2c3e50',
        marginBottom: '20px',
        fontWeight: '400'
      }}>
        Cross-Jurisdictional Legal Comparison
      </h2>

      <p style={{
        color: '#6c757d',
        marginBottom: '25px',
        fontSize: '14px'
      }}>
        Examining how various legal frameworks address your matter can provide valuable insights for your decision-making process.
      </p>

      {/* Consultation-Grade Section Label */}
      <div className="consultation-section">
        <div className="section-label">State Your Legal Inquiry</div>
        <textarea
          className="consultation-input"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="I'm seeking to understand how this legal matter is treated in different jurisdictions. Based on what you've described, could you compare the approaches and highlight the significant distinctions?"
          style={{ minHeight: '100px' }}
        />
      </div>

      {/* Jurisdiction Selection */}
      <div className="consultation-section">
        <div className="section-label">Choose Jurisdictions for Comparison</div>
        <p style={{
          fontSize: '14px',
          color: '#6c757d',
          marginBottom: '15px'
        }}>
          Select the legal systems you wish me to evaluate on your behalf.
        </p>
        
        <div style={{ 
          display: 'grid', 
          gap: '10px',
          marginBottom: '20px'
        }}>
          {availableJurisdictions.map((jurisdiction) => (
            <label 
              key={jurisdiction.id}
              style={{ 
                display: 'flex', 
                alignItems: 'center', 
                padding: '10px',
                border: '1px solid #e9ecef',
                borderRadius: '6px',
                cursor: 'pointer',
                backgroundColor: selectedJurisdictions.includes(jurisdiction.id) ? '#f8f9fa' : 'white'
              }}
            >
              <input
                type="checkbox"
                checked={selectedJurisdictions.includes(jurisdiction.id)}
                onChange={() => toggleJurisdiction(jurisdiction.id)}
                style={{ marginRight: '10px' }}
              />
              <div>
                <div style={{ fontWeight: '600', color: '#2c3e50' }}>
                  {jurisdiction.name}
                </div>
                <div style={{ fontSize: '12px', color: '#6c757d' }}>
                  {jurisdiction.description}
                </div>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* Jurisdiction-Specific Guidance */}
      {selectedJurisdictions.length > 0 && (
        <div className="consultation-section">
          <div className="section-label">How This Works in Selected Jurisdictions</div>
          <div style={{ display: 'grid', gap: '15px', marginTop: '15px' }}>
            {selectedJurisdictions.map((jurisdiction) => {
              const guidance = {
                India: {
                  courtSystem: 'Indian Judicial System',
                  authorityTone: 'Formal and procedural, emphasizing due process and evidence-based decisions',
                  emergencyGuidance: 'File FIR at nearest Police Station, contact local magistrate for immediate orders',
                  emergencyContacts: 'Police: 100 | Ambulance: 108 | Fire: 101'
                },
                UK: {
                  courtSystem: 'UK Courts and Tribunals',
                  authorityTone: 'Adversarial system with emphasis on precedent and judicial discretion',
                  emergencyGuidance: 'Contact Police (999) or Crown Prosecution Service for urgent matters',
                  emergencyContacts: 'Emergency: 999 | Police (non-emergency): 101'
                },
                UAE: {
                  courtSystem: 'UAE Federal Judiciary',
                  authorityTone: 'Civil law system with Islamic Sharia influences, emphasizing reconciliation',
                  emergencyGuidance: 'Contact Public Prosecution or local police for immediate legal intervention',
                  emergencyContacts: 'Police: 999 | Ambulance: 998 | Fire: 997'
                }
              }[jurisdiction];

              return (
                <div
                  key={jurisdiction}
                  style={{
                    padding: '15px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '8px',
                    border: '1px solid #e9ecef'
                  }}
                >
                  <h4 style={{
                    fontSize: '1rem',
                    color: '#2c3e50',
                    marginBottom: '10px',
                    fontWeight: '600'
                  }}>
                    {jurisdiction}
                  </h4>
                  <div style={{ fontSize: '14px', color: '#495057', lineHeight: '1.5' }}>
                    <div style={{ marginBottom: '8px' }}>
                      <strong>Court System:</strong> {guidance.courtSystem}
                    </div>
                    <div style={{ marginBottom: '8px' }}>
                      <strong>Authority Tone:</strong> {guidance.authorityTone}
                    </div>
                    <div style={{ marginBottom: '8px' }}>
                      <strong>Emergency Guidance:</strong> {guidance.emergencyGuidance}
                    </div>
                    <div style={{ marginBottom: '15px', fontSize: '13px', color: '#dc3545', fontWeight: '600' }}>
                      <strong>🚨 Emergency Contacts:</strong> {guidance.emergencyContacts}
                    </div>
                    <ProceduralTimeline jurisdiction={jurisdiction} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <button
        onClick={handleAnalyze}
        className="consultation-btn"
        disabled={isAnalyzing || !query.trim() || selectedJurisdictions.length === 0}
        style={{ width: '100%' }}
      >
        {isAnalyzing ? 'Performing Multi-Jurisdictional Review...' : 'Conduct Comparative Analysis'}
      </button>

      {/* Comparative Analysis Results */}
      {comparativeAnalysis && (
        <div style={{ marginTop: '25px' }}>
          <h3 style={{
            fontSize: '1.2rem',
            color: '#2c3e50',
            marginBottom: '20px'
          }}>
            Comparative Legal Assessment
          </h3>
          
          {comparativeAnalysis.results.map((result, index) => (
            <div 
              key={result.jurisdiction}
              style={{
                marginBottom: '20px',
                padding: '20px',
                backgroundColor: '#f8f9fa',
                borderRadius: '8px',
                border: '1px solid #e9ecef'
              }}
            >
              <h4 style={{
                fontSize: '1.1rem',
                color: '#2c3e50',
                marginBottom: '10px'
              }}>
                Analysis under {result.jurisdiction} Law
              </h4>
              
              <p style={{ marginBottom: '15px', lineHeight: '1.6' }}>
                {result.analysis}
              </p>

              <div style={{ marginBottom: '15px' }}>
                <strong>Key Differences:</strong>
                <ul style={{ paddingLeft: '20px', marginTop: '5px' }}>
                  {result.keyDifferences.map((diff, i) => (
                    <li key={i} style={{ marginBottom: '3px' }}>{diff}</li>
                  ))}
                </ul>
              </div>

              <div>
                <strong>Recommendations:</strong>
                <ul style={{ paddingLeft: '20px', marginTop: '5px' }}>
                  {result.recommendations.map((rec, i) => (
                    <li key={i} style={{ marginBottom: '3px' }}>{rec}</li>
                  ))}
                </ul>
              </div>
            </div>
          ))}

          {/* Feedback Section */}
          <FeedbackButtons traceId={traceId} context="Multi-Jurisdiction Analysis" />
        </div>
      )}
    </div>
  )
}

export default MultiJurisdictionCard