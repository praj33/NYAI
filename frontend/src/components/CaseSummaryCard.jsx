import React from 'react';
import ApiErrorState from './ApiErrorState.jsx';
import SkeletonLoader from './SkeletonLoader.jsx';

const CaseSummaryCard = ({
  caseId,
  title,
  overview,
  keyFacts,
  jurisdiction,
  confidence,
  summaryAnalysis,
  dateFiled,
  status,
  parties,
  traceId,
  loading,
  error,
  onRetry
}) => {
  if (loading) return <SkeletonLoader type="card" count={4} />

  if (error || !title || !overview || !jurisdiction || confidence == null || !summaryAnalysis) {
    return (
      <ApiErrorState
        title="Case Summary Unavailable"
        message={error || 'The backend returned an incomplete case summary response.'}
        traceId={traceId}
        onRetry={onRetry}
      />
    )
  }

  return (
    <div className="consultation-card">
      {/* Case Title */}
      <h2 style={{
        fontSize: '1.5rem',
        color: '#2c3e50',
        marginBottom: '20px',
        fontWeight: '600'
      }}>
        {title}
      </h2>

      {/* Case Overview */}
      <div style={{ marginBottom: '20px' }}>
        <div className="section-label">Case Overview</div>
        <p style={{
          color: '#495057',
          lineHeight: '1.6',
          fontSize: '14px'
        }}>
          {overview}
        </p>
      </div>

      {/* Key Facts */}
      <div style={{ marginBottom: '20px' }}>
        <div className="section-label">Key Facts</div>
        <ul style={{
          color: '#495057',
          paddingLeft: '20px',
          lineHeight: '1.6',
          fontSize: '14px'
        }}>
          {keyFacts.map((fact, index) => (
            <li key={index} style={{ marginBottom: '8px' }}>
              {fact}
            </li>
          ))}
        </ul>
      </div>

      {/* Jurisdiction and Confidence */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '20px',
        marginBottom: '20px'
      }}>
        <div>
          <div className="section-label">Jurisdiction</div>
          <p style={{
            color: '#495057',
            fontSize: '14px',
            fontWeight: '500'
          }}>
            {jurisdiction}
          </p>
        </div>
        <div>
          <div className="section-label">Confidence Score</div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px'
          }}>
            <div style={{
              flex: 1,
              height: '8px',
              backgroundColor: '#e9ecef',
              borderRadius: '4px',
              overflow: 'hidden'
            }}>
              <div style={{
                width: `${confidence * 100}%`,
                height: '100%',
                backgroundColor: confidence > 0.8 ? '#28a745' : confidence > 0.6 ? '#ffc107' : '#dc3545',
                transition: 'width 0.3s ease'
              }} />
            </div>
            <span style={{
              fontSize: '14px',
              fontWeight: '600',
              color: '#495057'
            }}>
              {(confidence * 100).toFixed(1)}%
            </span>
          </div>
        </div>
      </div>

      {/* Summary Analysis */}
      <div style={{ marginBottom: '20px' }}>
        <div className="section-label">Legal Analysis</div>
        <p style={{
          color: '#495057',
          lineHeight: '1.6',
          fontSize: '14px'
        }}>
          <em>Based on currently available information: </em>{summaryAnalysis}
        </p>
      </div>

      {/* Optional Fields */}
      {(dateFiled || status || parties) && (
        <div style={{
          borderTop: '1px solid #e9ecef',
          paddingTop: '20px'
        }}>
          <div className="section-label">Additional Information</div>
          <div style={{
            display: 'grid',
            gap: '10px',
            fontSize: '14px',
            color: '#6c757d'
          }}>
            {dateFiled && (
              <div><strong>Date Filed:</strong> {dateFiled}</div>
            )}
            {status && (
              <div><strong>Status:</strong> {status}</div>
            )}
            {parties && (
              <div>
                <strong>Parties:</strong>
                {parties.plaintiff && <div style={{ marginLeft: '10px' }}>Plaintiff: {parties.plaintiff}</div>}
                {parties.defendant && <div style={{ marginLeft: '10px' }}>Defendant: {parties.defendant}</div>}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default CaseSummaryCard;