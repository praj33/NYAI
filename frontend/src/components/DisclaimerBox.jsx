import React from 'react'

const DisclaimerBox = ({ text }) => {
  return (
    <div style={{
      padding: '15px',
      backgroundColor: '#fff3cd',
      border: '1px solid #ffeaa7',
      borderRadius: '8px',
      fontSize: '14px',
      color: '#856404'
    }}>
      <strong>Disclaimer:</strong> {text || "This guidance may evolve as more details are added."}
    </div>
  )
}

export default DisclaimerBox