import React from 'react';

const RecommendationStatusCard = ({ recommendation, traceId }) => {
  if (!recommendation || !recommendation.type) {
    return null;
  }

  const { type, rationale, confidence } = recommendation;

  const getTypeConfig = () => {
    switch (type) {
      case 'ESCALATE':
        return {
          color: '#fd7e14',
          bgColor: 'rgba(253, 126, 20, 0.1)',
          borderColor: 'rgba(253, 126, 20, 0.3)',
          icon: '📈',
          label: 'ESCALATION ADVISED',
          severity: 'medium'
        };
      case 'REVIEW':
        return {
          color: '#ffc107',
          bgColor: 'rgba(255, 193, 7, 0.1)',
          borderColor: 'rgba(255, 193, 7, 0.3)',
          icon: '⚠️',
          label: 'REVIEW RECOMMENDED',
          severity: 'medium'
        };
      case 'INSUFFICIENT_DATA':
        return {
          color: '#6c757d',
          bgColor: 'rgba(108, 117, 125, 0.1)',
          borderColor: 'rgba(108, 117, 125, 0.3)',
          icon: '❓',
          label: 'INSUFFICIENT DATA',
          severity: 'high'
        };
      case 'INFORM':
      default:
        return {
          color: '#28a745',
          bgColor: 'rgba(40, 167, 69, 0.1)',
          borderColor: 'rgba(40, 167, 69, 0.3)',
          icon: 'ℹ️',
          label: 'INFORMATIONAL',
          severity: 'none'
        };
    }
  };

  const typeConfig = getTypeConfig();

  if (type === 'INFORM') {
    return null;
  }

  return (
    <div
      className="consultation-card"
      style={{
        borderLeft: `4px solid ${typeConfig.color}`,
        backgroundColor: typeConfig.bgColor,
        border: `1px solid ${typeConfig.borderColor}`,
        marginBottom: '20px'
      }}
    >
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '15px',
        marginBottom: '20px',
        paddingBottom: '15px',
        borderBottom: `1px solid ${typeConfig.borderColor}`
      }}>
        <div style={{
          width: '50px',
          height: '50px',
          borderRadius: '50%',
          backgroundColor: typeConfig.color,
          color: 'white',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '24px',
          flexShrink: 0
        }}>
          {typeConfig.icon}
        </div>
        <div>
          <h2 style={{
            fontSize: '1.3rem',
            color: typeConfig.color,
            margin: 0,
            fontWeight: '700'
          }}>
            {typeConfig.label}
          </h2>
          <p style={{
            color: '#6c757d',
            fontSize: '14px',
            margin: '5px 0 0 0'
          }}>
            Advisory Recommendation — Not a binding decision
          </p>
        </div>
      </div>

      {traceId && (
        <div style={{
          marginBottom: '15px',
          padding: '10px',
          backgroundColor: 'rgba(0, 0, 0, 0.05)',
          borderRadius: '6px',
          fontSize: '13px',
          fontFamily: 'monospace'
        }}>
          <strong>Trace ID:</strong> {traceId}
        </div>
      )}

      {rationale && (
        <div style={{ marginBottom: '15px' }}>
          <div style={{
            fontSize: '14px',
            fontWeight: '600',
            color: '#495057',
            marginBottom: '8px'
          }}>
            Rationale
          </div>
          <p style={{
            color: '#6c757d',
            fontSize: '14px',
            lineHeight: '1.6',
            margin: 0
          }}>
            {rationale}
          </p>
        </div>
      )}

      {typeof confidence === 'number' && (
        <div style={{
          padding: '10px',
          backgroundColor: 'rgba(0, 0, 0, 0.03)',
          borderRadius: '6px',
          fontSize: '13px'
        }}>
          <strong>Confidence:</strong> {Math.round(confidence * 100)}%
        </div>
      )}
    </div>
  );
};

export default RecommendationStatusCard;
