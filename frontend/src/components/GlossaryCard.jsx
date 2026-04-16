import React, { useState } from 'react';
import ApiErrorState from './ApiErrorState.jsx';
import SkeletonLoader from './SkeletonLoader.jsx';

const GlossaryCard = ({ terms, jurisdiction, caseType, traceId, loading, error, onRetry }) => {
  const [expandedTerms, setExpandedTerms] = useState(new Set())

  if (loading) return <SkeletonLoader type="card" count={3} />

  if (error || !terms || !Array.isArray(terms) || terms.length === 0 || !jurisdiction) {
    return (
      <ApiErrorState
        title="Glossary Unavailable"
        message={error || 'The backend returned an incomplete glossary response.'}
        traceId={traceId}
        onRetry={onRetry}
      />
    )
  }

  const toggleTerm = (term) => {
    const newExpanded = new Set(expandedTerms);
    if (newExpanded.has(term)) {
      newExpanded.delete(term);
    } else {
      newExpanded.add(term);
    }
    setExpandedTerms(newExpanded);
  };

  return (
    <div className="consultation-card">
      {/* Header */}
      <h2 style={{
        fontSize: '1.5rem',
        color: '#2c3e50',
        marginBottom: '20px',
        fontWeight: '600'
      }}>
        Legal Glossary
        {caseType && (
          <span style={{
            fontSize: '0.9rem',
            color: '#6c757d',
            fontWeight: '400',
            marginLeft: '10px'
          }}>
            ({caseType})
          </span>
        )}
      </h2>

      {/* Jurisdiction */}
      <div style={{ marginBottom: '20px' }}>
        <div className="section-label">Jurisdiction</div>
        <p style={{
          color: '#495057',
          fontSize: '14px',
          fontWeight: '500'
        }}>
          {jurisdiction}
        </p>
      </div>

      {/* Terms List */}
      <div>
        <div className="section-label">Terms & Definitions</div>
        {terms?.map((termData, index) => {
          const isExpanded = expandedTerms.has(termData?.term);
          const hasConfidence = termData?.confidence !== undefined;

          return (
            <div key={index} style={{
              border: '1px solid #e9ecef',
              borderRadius: '8px',
              marginBottom: '10px',
              overflow: 'hidden'
            }}>
              {/* Term Header */}
              <div
                style={{
                  padding: '15px',
                  backgroundColor: '#f8f9fa',
                  cursor: 'pointer',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}
                onClick={() => toggleTerm(termData?.term)}
              >
                <h3 style={{
                  fontSize: '1.1rem',
                  color: '#2c3e50',
                  margin: 0,
                  fontWeight: '600'
                }}>
                  {termData?.term}
                </h3>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  {hasConfidence && (
                    <span style={{
                      fontSize: '12px',
                      color: '#6c757d',
                      fontWeight: '500'
                    }}>
                      Confidence: {(termData.confidence * 100).toFixed(1)}%
                    </span>
                  )}
                  <span style={{
                    fontSize: '18px',
                    color: '#6c757d',
                    transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
                    transition: 'transform 0.2s ease'
                  }}>
                    ▼
                  </span>
                </div>
              </div>

              {/* Expandable Content */}
              {isExpanded && (
                <div style={{ padding: '15px' }}>
                  {/* Definition */}
                  <div style={{ marginBottom: '15px' }}>
                    <div style={{
                      fontSize: '14px',
                      fontWeight: '600',
                      color: '#2c3e50',
                      marginBottom: '5px'
                    }}>
                      Definition
                    </div>
                    <p style={{
                      color: '#495057',
                      lineHeight: '1.6',
                      fontSize: '14px',
                      margin: 0
                    }}>
                      {termData.definition}
                    </p>
                  </div>

                  {/* Context */}
                  {termData.context && (
                    <div style={{ marginBottom: '15px' }}>
                      <div style={{
                        fontSize: '14px',
                        fontWeight: '600',
                        color: '#2c3e50',
                        marginBottom: '5px'
                      }}>
                        Context in This Case
                      </div>
                      <p style={{
                        color: '#495057',
                        lineHeight: '1.6',
                        fontSize: '14px',
                        margin: 0
                      }}>
                        {termData.context}
                      </p>
                    </div>
                  )}

                  {/* Related Terms */}
                  {termData.relatedTerms && termData.relatedTerms.length > 0 && (
                    <div style={{ marginBottom: '15px' }}>
                      <div style={{
                        fontSize: '14px',
                        fontWeight: '600',
                        color: '#2c3e50',
                        marginBottom: '5px'
                      }}>
                        Related Terms
                      </div>
                      <div style={{
                        display: 'flex',
                        flexWrap: 'wrap',
                        gap: '8px'
                      }}>
                        {termData.relatedTerms.map((related, idx) => (
                          <span key={idx} style={{
                            backgroundColor: '#e9ecef',
                            color: '#495057',
                            padding: '4px 8px',
                            borderRadius: '4px',
                            fontSize: '12px',
                            fontWeight: '500'
                          }}>
                            {related}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Jurisdiction Note */}
                  {termData.jurisdiction && termData.jurisdiction !== jurisdiction && (
                    <div style={{ marginBottom: '15px' }}>
                      <div style={{
                        fontSize: '14px',
                        fontWeight: '600',
                        color: '#2c3e50',
                        marginBottom: '5px'
                      }}>
                        Jurisdiction Note
                      </div>
                      <p style={{
                        color: '#6c757d',
                        fontSize: '14px',
                        margin: 0,
                        fontStyle: 'italic'
                      }}>
                        This definition is specific to {termData.jurisdiction} law.
                      </p>
                    </div>
                  )}

                  {/* Confidence Score */}
                  {hasConfidence && (
                    <div>
                      <div style={{
                        fontSize: '14px',
                        fontWeight: '600',
                        color: '#2c3e50',
                        marginBottom: '5px'
                      }}>
                        Confidence Score
                      </div>
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
                            width: `${termData.confidence * 100}%`,
                            height: '100%',
                            backgroundColor: termData.confidence > 0.8 ? '#28a745' : termData.confidence > 0.6 ? '#ffc107' : '#dc3545',
                            transition: 'width 0.3s ease'
                          }} />
                        </div>
                        <span style={{
                          fontSize: '14px',
                          fontWeight: '600',
                          color: '#495057'
                        }}>
                          {(termData.confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default GlossaryCard;