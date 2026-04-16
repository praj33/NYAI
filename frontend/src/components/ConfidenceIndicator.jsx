import React from 'react'

const ConfidenceIndicator = ({ confidence }) => {
  const percentage = Math.round(confidence * 100)

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '8px',
      alignItems: 'flex-start'
    }}>
      <div style={{
        fontSize: '14px',
        fontWeight: '600',
        color: '#2c3e50'
      }}>
        Confidence Level: {percentage}%
      </div>
      <div style={{
        width: '200px',
        height: '8px',
        backgroundColor: '#e9ecef',
        borderRadius: '4px',
        overflow: 'hidden'
      }}>
        <div style={{
          width: `${percentage}%`,
          height: '100%',
          backgroundColor: percentage > 80 ? '#28a745' : percentage > 60 ? '#ffc107' : '#dc3545',
          transition: 'width 0.3s ease'
        }}></div>
      </div>
    </div>
  )
}

export default ConfidenceIndicator