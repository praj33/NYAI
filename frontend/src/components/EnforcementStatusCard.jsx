import React from 'react';

const EnforcementStatusCard = ({ enforcementStatus, traceId }) => {
  // Handle missing or invalid enforcement status
  if (!enforcementStatus || !enforcementStatus.state) {
    return null;
  }

  const { state, reason, blocked_path, escalation_required, escalation_target, redirect_suggestion, safe_explanation } = enforcementStatus;

  // Get styling based on enforcement state
  const getStateConfig = () => {
    switch (state) {
      case 'block':
        return {
          color: '#dc3545',
          bgColor: 'rgba(220, 53, 69, 0.1)',
          borderColor: 'rgba(220, 53, 69, 0.3)',
          icon: '🚫',
          label: 'BLOCKED',
          severity: 'high'
        };
      case 'escalate':
        return {
          color: '#fd7e14',
          bgColor: 'rgba(253, 126, 20, 0.1)',
          borderColor: 'rgba(253, 126, 20, 0.3)',
          icon: '📈',
          label: 'ESCALATION REQUIRED',
          severity: 'medium'
        };
      case 'soft_redirect':
        return {
          color: '#6f42c1',
          bgColor: 'rgba(111, 66, 193, 0.1)',
          borderColor: 'rgba(111, 66, 193, 0.3)',
          icon: '↩️',
          label: 'RECOMMENDED REDIRECT',
          severity: 'low'
        };
      case 'conditional':
        return {
          color: '#ffc107',
          bgColor: 'rgba(255, 193, 7, 0.1)',
          borderColor: 'rgba(255, 193, 7, 0.3)',
          icon: '⚠️',
          label: 'CONDITIONAL ACCESS',
          severity: 'medium'
        };
      case 'clear':
      default:
        return {
          color: '#28a745',
          bgColor: 'rgba(40, 167, 69, 0.1)',
          borderColor: 'rgba(40, 167, 69, 0.3)',
          icon: '✅',
          label: 'CLEAR',
          severity: 'none'
        };
    }
  };

  const stateConfig = getStateConfig();

  // Don't render if state is clear (no enforcement issues)
  if (state === 'clear') {
    return null;
  }

  return (
    <div 
      className="consultation-card"
      style={{
        borderLeft: `4px solid ${stateConfig.color}`,
        backgroundColor: stateConfig.bgColor,
        border: `1px solid ${stateConfig.borderColor}`,
        marginBottom: '20px'
      }}
    >
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '15px',
        marginBottom: '20px',
        paddingBottom: '15px',
        borderBottom: `1px solid ${stateConfig.borderColor}`
      }}>
        <div style={{
          width: '50px',
          height: '50px',
          borderRadius: '50%',
          backgroundColor: stateConfig.color,
          color: 'white',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '24px',
          flexShrink: 0
        }}>
          {stateConfig.icon}
        </div>
        <div>
          <h2 style={{
            fontSize: '1.3rem',
            color: stateConfig.color,
            margin: 0,
            fontWeight: '700'
          }}>
            {stateConfig.label}
          </h2>
          <p style={{
            color: '#6c757d',
            fontSize: '14px',
            margin: '5px 0 0 0'
          }}>
            Enforcement Status for Legal Pathway
          </p>
        </div>
      </div>

      {/* Trace ID */}
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

      {/* Safe Explanation */}
      {safe_explanation && (
        <div style={{
          marginBottom: '20px',
          padding: '15px',
          backgroundColor: 'white',
          borderRadius: '8px',
          border: `1px solid ${stateConfig.borderColor}`
        }}>
          <div style={{
            fontSize: '14px',
            fontWeight: '600',
            color: stateConfig.color,
            marginBottom: '10px'
          }}>
            What This Means
          </div>
          <p style={{
            color: '#495057',
            fontSize: '14px',
            lineHeight: '1.6',
            margin: 0
          }}>
            {safe_explanation}
          </p>
        </div>
      )}

      {/* Reason */}
      {reason && (
        <div style={{ marginBottom: '15px' }}>
          <div style={{
            fontSize: '14px',
            fontWeight: '600',
            color: '#495057',
            marginBottom: '8px'
          }}>
            Reason
          </div>
          <p style={{
            color: '#6c757d',
            fontSize: '14px',
            lineHeight: '1.6',
            margin: 0
          }}>
            {reason}
          </p>
        </div>
      )}

      {/* Blocked Path */}
      {blocked_path && state === 'block' && (
        <div style={{
          marginBottom: '15px',
          padding: '15px',
          backgroundColor: 'rgba(220, 53, 69, 0.1)',
          borderRadius: '8px',
          border: '1px solid rgba(220, 53, 69, 0.3)'
        }}>
          <div style={{
            fontSize: '14px',
            fontWeight: '600',
            color: '#dc3545',
            marginBottom: '8px'
          }}>
            Blocked Pathway
          </div>
          <p style={{
            color: '#495057',
            fontSize: '14px',
            margin: 0
          }}>
            {blocked_path}
          </p>
        </div>
      )}

      {/* Escalation Info */}
      {escalation_required && (
        <div style={{
          marginBottom: '15px',
          padding: '15px',
          backgroundColor: 'rgba(253, 126, 20, 0.1)',
          borderRadius: '8px',
          border: '1px solid rgba(253, 126, 20, 0.3)'
        }}>
          <div style={{
            fontSize: '14px',
            fontWeight: '600',
            color: '#fd7e14',
            marginBottom: '8px'
          }}>
            Escalation Required
          </div>
          {escalation_target && (
            <p style={{
              color: '#495057',
              fontSize: '14px',
              margin: '0 0 8px 0'
            }}>
              <strong>Target:</strong> {escalation_target}
            </p>
          )}
          <p style={{
            color: '#6c757d',
            fontSize: '14px',
            margin: 0
          }}>
            This matter requires review by a higher authority before proceeding.
          </p>
        </div>
      )}

      {/* Redirect Suggestion */}
      {redirect_suggestion && state === 'soft_redirect' && (
        <div style={{
          marginBottom: '15px',
          padding: '15px',
          backgroundColor: 'rgba(111, 66, 193, 0.1)',
          borderRadius: '8px',
          border: '1px solid rgba(111, 66, 193, 0.3)'
        }}>
          <div style={{
            fontSize: '14px',
            fontWeight: '600',
            color: '#6f42c1',
            marginBottom: '8px'
          }}>
            Suggested Alternative
          </div>
          <p style={{
            color: '#495057',
            fontSize: '14px',
            margin: 0
          }}>
            {redirect_suggestion}
          </p>
        </div>
      )}

      {/* Action Required */}
      <div style={{
        padding: '15px',
        backgroundColor: 'rgba(0, 0, 0, 0.03)',
        borderRadius: '8px',
        marginTop: '20px'
      }}>
        <div style={{
          fontSize: '14px',
          fontWeight: '600',
          color: '#495057',
          marginBottom: '8px'
        }}>
          Recommended Action
        </div>
        <p style={{
          color: '#6c757d',
          fontSize: '14px',
          margin: 0,
          lineHeight: '1.6'
        }}>
          {state === 'block' && 'Please consult with a legal professional to explore alternative pathways.'}
          {state === 'escalate' && 'Contact the appropriate authority or escalation point for review.'}
          {state === 'soft_redirect' && 'Consider the suggested alternative pathway for better outcomes.'}
          {state === 'conditional' && 'Review and satisfy the conditions before proceeding.'}
        </p>
      </div>
    </div>
  );
};

export default EnforcementStatusCard;
