import React, { useState } from 'react'
import GlareHover from './GlareHover.jsx'

const LegalOSDashboard = ({ onModuleSelect }) => {
  const [activeModule, setActiveModule] = useState(null)

  const modules = [
    {
      id: 'consult',
      title: 'Ask Legal Question',
      description: 'Get instant AI-powered legal analysis',
      color: '#3b82f6'
    },
    {
      id: 'decision',
      title: 'Legal Decisions',
      description: 'Query structured legal decisions with enforcement',
      color: '#ec4899'
    },
    {
      id: 'procedure',
      title: 'Jurisdiction Procedure',
      description: 'Navigate through legal procedures by jurisdiction',
      color: '#8b5cf6'
    },
    {
      id: 'timeline',
      title: 'Case Timeline',
      description: 'Generate timeline for your legal case',
      color: '#10b981'
    },
    {
      id: 'glossary',
      title: 'Legal Glossary',
      description: 'Search legal terms and definitions',
      color: '#f59e0b'
    }
  ]

  return (
    <div style={{ padding: '40px 20px', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Hero Section */}
      <div style={{ textAlign: 'center', marginBottom: '60px' }}>
        <h1 style={{ 
          fontSize: '48px', 
          fontWeight: '700', 
          marginBottom: '16px',
          background: 'linear-gradient(135deg, #ffffff 0%, rgba(255, 255, 255, 0.7) 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text'
        }}>
          NYAI
        </h1>
        <p style={{ 
          fontSize: '18px', 
          color: 'rgba(255, 255, 255, 0.7)',
          maxWidth: '600px',
          margin: '0 auto'
        }}>
          AI-powered legal intelligence across India, UK, and UAE jurisdictions
        </p>
      </div>

      {/* Module Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: '20px',
        marginBottom: '60px',
        maxWidth: '750px',
        margin: '0 auto 60px auto'
      }}>
        {modules.map(module => (
          <GlareHover key={module.id}>
            <button
              onClick={() => onModuleSelect(module.id)}
              style={{
                background: 'rgba(255, 255, 255, 0.05)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '16px',
                padding: '24px',
                textAlign: 'left',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                position: 'relative',
                overflow: 'hidden',
                width: '100%',
                height: '140px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.08)'
                e.currentTarget.style.borderColor = module.color
                e.currentTarget.style.transform = 'translateY(-4px)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)'
                e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)'
                e.currentTarget.style.transform = 'translateY(0)'
              }}
            >
            <h3 style={{ 
              color: '#fff', 
              fontSize: '20px', 
              fontWeight: '600', 
              marginBottom: '8px' 
            }}>
              {module.title}
            </h3>
            <p style={{ 
              color: 'rgba(255, 255, 255, 0.6)', 
              fontSize: '14px',
              lineHeight: '1.6',
              margin: 0
            }}>
              {module.description}
            </p>
            <div style={{
              position: 'absolute',
              top: 0,
              right: 0,
              width: '120px',
              height: '120px',
              background: `radial-gradient(circle, ${module.color}20 0%, transparent 70%)`,
              pointerEvents: 'none'
            }} />
            </button>
          </GlareHover>
        ))}
      </div>

      {/* About Us */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.03)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '16px',
        padding: '32px',
        textAlign: 'center'
      }}>
        <h3 style={{ 
          color: '#fff', 
          fontSize: '18px', 
          fontWeight: '600',
          marginBottom: '24px'
        }}>
          About Us
        </h3>
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          gap: '40px',
          flexWrap: 'wrap'
        }}>
          {['Sovereign Compliant', 'Transparent AI', 'Real-time Analysis', 'Multi-Jurisdiction'].map((feature, idx) => (
            <div key={idx} style={{ 
              color: 'rgba(255, 255, 255, 0.7)',
              fontSize: '14px',
              fontWeight: '500'
            }}>
              {feature}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default LegalOSDashboard
