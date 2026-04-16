import React from 'react';
import ApiErrorState from './ApiErrorState.jsx';
import SkeletonLoader from './SkeletonLoader.jsx';

const LegalRouteCard = ({ routes, jurisdiction, caseType, traceId, loading, error, onRetry }) => {
  if (loading) return <SkeletonLoader type="card" count={3} />

  if (error || !routes || !Array.isArray(routes) || routes.length === 0 || !jurisdiction) {
    return (
      <ApiErrorState
        title="Legal Routes Unavailable"
        message={error || 'The backend returned an incomplete legal routes response.'}
        traceId={traceId}
        onRetry={onRetry}
      />
    )
  }

  const getSuitabilityColor = (suitability) => {
    if (suitability >= 0.8) return '#28a745'; // High - green
    if (suitability >= 0.6) return '#ffc107'; // Medium - yellow
    return '#dc3545'; // Low - red
  };

  const getSuitabilityLabel = (suitability) => {
    if (suitability >= 0.8) return 'High';
    if (suitability >= 0.6) return 'Medium';
    return 'Low';
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
        Legal Pathways - {caseType}
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

      {/* Routes */}
      <div style={{ marginBottom: '20px' }}>
        <div className="section-label">Available Routes</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {routes.map((route, index) => (
            <div key={index} style={{
              border: '1px solid #e9ecef',
              borderRadius: '8px',
              padding: '20px',
              backgroundColor: '#f8f9fa'
            }}>
              {/* Route Name */}
              <h3 style={{
                fontSize: '1.2rem',
                color: '#2c3e50',
                marginBottom: '15px',
                fontWeight: '600'
              }}>
                {route.name}
              </h3>

              {/* Description */}
              <div style={{ marginBottom: '15px' }}>
                <p style={{
                  color: '#495057',
                  lineHeight: '1.6',
                  fontSize: '14px'
                }}>
                  {route.description}
                </p>
              </div>

              {/* Recommendation */}
              <div style={{ marginBottom: '15px' }}>
                <div style={{
                  fontSize: '14px',
                  fontWeight: '600',
                  color: '#495057',
                  marginBottom: '5px'
                }}>
                  Recommendation:
                </div>
                <p style={{
                  color: '#495057',
                  lineHeight: '1.6',
                  fontSize: '14px'
                }}>
                  {route.recommendation}
                </p>
              </div>

              {/* Suitability Score */}
              <div style={{ marginBottom: '15px' }}>
                <div style={{
                  fontSize: '14px',
                  fontWeight: '600',
                  color: '#495057',
                  marginBottom: '8px'
                }}>
                  Suitability Score:
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
                      width: `${route.suitability * 100}%`,
                      height: '100%',
                      backgroundColor: getSuitabilityColor(route.suitability),
                      transition: 'width 0.3s ease'
                    }} />
                  </div>
                  <span style={{
                    fontSize: '14px',
                    fontWeight: '600',
                    color: '#495057'
                  }}>
                    {getSuitabilityLabel(route.suitability)} ({(route.suitability * 100).toFixed(1)}%)
                  </span>
                </div>
              </div>

              {/* Estimates */}
              {(route.estimatedDuration || route.estimatedCost) && (
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '20px',
                  marginBottom: '15px'
                }}>
                  {route.estimatedDuration && (
                    <div>
                      <div style={{
                        fontSize: '14px',
                        fontWeight: '600',
                        color: '#495057',
                        marginBottom: '5px'
                      }}>
                        Estimated Duration:
                      </div>
                      <p style={{
                        color: '#495057',
                        fontSize: '14px'
                      }}>
                        {route.estimatedDuration}
                      </p>
                    </div>
                  )}
                  {route.estimatedCost && (
                    <div>
                      <div style={{
                        fontSize: '14px',
                        fontWeight: '600',
                        color: '#495057',
                        marginBottom: '5px'
                      }}>
                        Estimated Cost:
                      </div>
                      <p style={{
                        color: '#495057',
                        fontSize: '14px'
                      }}>
                        {route.estimatedCost}
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Pros and Cons */}
              {(route.pros || route.cons) && (
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: route.pros && route.cons ? '1fr 1fr' : '1fr',
                  gap: '20px'
                }}>
                  {route.pros && route.pros.length > 0 && (
                    <div>
                      <div style={{
                        fontSize: '14px',
                        fontWeight: '600',
                        color: '#28a745',
                        marginBottom: '8px'
                      }}>
                        Pros:
                      </div>
                      <ul style={{
                        color: '#495057',
                        paddingLeft: '20px',
                        lineHeight: '1.6',
                        fontSize: '14px'
                      }}>
                        {route.pros.map((pro, proIndex) => (
                          <li key={proIndex} style={{ marginBottom: '4px' }}>
                            {pro}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {route.cons && route.cons.length > 0 && (
                    <div>
                      <div style={{
                        fontSize: '14px',
                        fontWeight: '600',
                        color: '#dc3545',
                        marginBottom: '8px'
                      }}>
                        Cons:
                      </div>
                      <ul style={{
                        color: '#495057',
                        paddingLeft: '20px',
                        lineHeight: '1.6',
                        fontSize: '14px'
                      }}>
                        {route.cons.map((con, conIndex) => (
                          <li key={conIndex} style={{ marginBottom: '4px' }}>
                            {con}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default LegalRouteCard;