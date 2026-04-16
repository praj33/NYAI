import React from 'react'

const ProceduralTimeline = ({ jurisdiction }) => {
  const timelineData = {
    India: [
      {
        step: 'Filing',
        description: 'File FIR at Police Station or submit complaint',
        duration: '1-3 days',
        icon: '📝',
        status: 'current'
      },
      {
        step: 'Investigation',
        description: 'Police investigation and evidence collection',
        duration: '15-90 days',
        icon: '🔍',
        status: 'pending'
      },
      {
        step: 'Court Process',
        description: 'Chargesheet filing, trial, and judgment',
        duration: '6-24 months',
        icon: '⚖️',
        status: 'pending'
      }
    ],
    UK: [
      {
        step: 'Filing',
        description: 'Report to Police or contact CPS',
        duration: '1-7 days',
        icon: '📞'
      },
      {
        step: 'Investigation',
        description: 'Police investigation and CPS review',
        duration: '14-60 days',
        icon: '🔍'
      },
      {
        step: 'Court Process',
        description: 'Magistrates Court, Crown Court trial',
        duration: '3-12 months',
        icon: '⚖️'
      }
    ],
    UAE: [
      {
        step: 'Filing',
        description: 'Submit complaint to Public Prosecution',
        duration: '1-5 days',
        icon: '📋'
      },
      {
        step: 'Investigation',
        description: 'Public Prosecution investigation',
        duration: '7-30 days',
        icon: '🔍'
      },
      {
        step: 'Court Process',
        description: 'Federal Court proceedings and judgment',
        duration: '2-8 months',
        icon: '⚖️'
      }
    ]
  }

  const steps = timelineData[jurisdiction] || []

  // Handle missing or empty steps
  if (!jurisdiction || steps.length === 0) {
    return (
      <div className="procedural-timeline">
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <h3 style={{ color: '#dc3545', marginBottom: '10px' }}>Information will appear here once available</h3>
          <p style={{ color: '#6c757d' }}>
            Procedural timeline data is currently unavailable for the selected jurisdiction.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="procedural-timeline">
      <h4 style={{
        fontSize: '1.1rem',
        color: '#2c3e50',
        marginBottom: '20px',
        textAlign: 'center'
      }}>
        Procedural Timeline in {jurisdiction}
      </h4>

      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '20px',
        position: 'relative'
      }}>
        {/* Timeline line */}
        <div style={{
          position: 'absolute',
          left: '30px',
          top: '40px',
          bottom: '40px',
          width: '2px',
          backgroundColor: '#007bff',
          zIndex: 1
        }} />

        {steps.map((step, index) => (
          <div
            key={index}
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: '15px',
              position: 'relative'
            }}
          >
            {/* Step icon */}
            <div style={{
              width: '60px',
              height: '60px',
              borderRadius: '50%',
              backgroundColor: '#007bff',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '24px',
              flexShrink: 0,
              zIndex: 2,
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
              {step.icon}
            </div>

            {/* Step content */}
            <div style={{
              backgroundColor: '#f8f9fa',
              padding: '15px',
              borderRadius: '8px',
              border: '1px solid #e9ecef',
              flex: 1
            }}>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '8px'
              }}>
                <h5 style={{
                  fontSize: '1rem',
                  color: '#2c3e50',
                  margin: 0,
                  fontWeight: '600'
                }}>
                  {step.step}
                </h5>
                <span style={{
                  backgroundColor: '#007bff',
                  color: 'white',
                  padding: '4px 8px',
                  borderRadius: '4px',
                  fontSize: '12px',
                  fontWeight: '500'
                }}>
                  {step.duration}
                </span>
              </div>
              <p style={{
                margin: 0,
                color: '#6c757d',
                fontSize: '14px',
                lineHeight: '1.5'
              }}>
                {step.description}
              </p>
            </div>
          </div>
        ))}
      </div>

      <div style={{
        marginTop: '20px',
        padding: '15px',
        backgroundColor: '#fff3cd',
        border: '1px solid #ffeaa7',
        borderRadius: '8px',
        fontSize: '14px',
        color: '#856404'
      }}>
        <strong>Note:</strong> These are typical duration ranges and may vary based on case complexity, jurisdiction specifics, and other factors. Always consult with local legal professionals for accurate timelines.
      </div>
    </div>
  )
}

export default ProceduralTimeline