import React from 'react'

const SessionStatus = ({ status }) => {
  const statusConfig = {
    active: { color: '#28a745', text: 'Active' },
    inactive: { color: '#ffc107', text: 'Inactive' },
    expired: { color: '#dc3545', text: 'Expired' }
  }

  const config = statusConfig[status] || { color: '#6c757d', text: status }

  return (
    <div style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '8px',
      padding: '8px 12px',
      backgroundColor: '#f8f9fa',
      borderRadius: '20px',
      fontSize: '14px',
      fontWeight: '500'
    }}>
      <div style={{
        width: '10px',
        height: '10px',
        borderRadius: '50%',
        backgroundColor: config.color
      }}></div>
      {config.text}
    </div>
  )
}

export default SessionStatus