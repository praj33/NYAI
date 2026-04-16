// OfflineBanner.jsx — Non-intrusive degraded mode status banner
import React from 'react'

const OfflineBanner = ({ isOffline, isSyncing, hasPending, onSyncClick }) => {
  if (!isOffline) return null

  return (
    <div style={{
      position: 'fixed',
      bottom: '24px',
      left: '50%',
      transform: 'translateX(-50%)',
      zIndex: 2000,
      display: 'flex',
      alignItems: 'center',
      gap: '16px',
      padding: '12px 20px',
      background: 'rgba(30, 30, 40, 0.92)',
      backdropFilter: 'blur(12px)',
      WebkitBackdropFilter: 'blur(12px)',
      border: '1px solid rgba(255, 193, 7, 0.4)',
      borderRadius: '12px',
      boxShadow: '0 4px 24px rgba(0,0,0,0.4)',
      maxWidth: '90vw'
    }}>
      {/* Pulsing indicator */}
      <span style={{
        width: '10px',
        height: '10px',
        borderRadius: '50%',
        backgroundColor: '#ffc107',
        flexShrink: 0,
        animation: 'pulse 1.8s ease-in-out infinite'
      }} />

      <span style={{
        color: 'rgba(255,255,255,0.9)',
        fontSize: '13px',
        lineHeight: '1.4'
      }}>
        System Operating in Offline Mode: Data is being saved locally. Analysis will resume when the connection is restored.
      </span>

      {hasPending && (
        <button
          onClick={onSyncClick}
          disabled={isSyncing}
          style={{
            flexShrink: 0,
            padding: '6px 14px',
            background: isSyncing ? 'rgba(255,255,255,0.1)' : 'rgba(255, 193, 7, 0.2)',
            border: '1px solid rgba(255, 193, 7, 0.5)',
            borderRadius: '8px',
            color: '#ffc107',
            fontSize: '12px',
            fontWeight: '600',
            cursor: isSyncing ? 'not-allowed' : 'pointer',
            whiteSpace: 'nowrap'
          }}
        >
          {isSyncing ? 'Syncing…' : 'Sync Case to Server'}
        </button>
      )}

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.4; transform: scale(0.85); }
        }
      `}</style>
    </div>
  )
}

export default OfflineBanner
