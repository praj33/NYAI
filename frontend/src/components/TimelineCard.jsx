import React from 'react';
import ApiErrorState from './ApiErrorState.jsx';
import SkeletonLoader from './SkeletonLoader.jsx';

const TimelineCard = ({ events, jurisdiction, caseId, traceId, loading, error, onRetry }) => {
  if (loading) return <SkeletonLoader type="card" count={4} />

  if (error || !events || !Array.isArray(events) || events.length === 0 || !jurisdiction) {
    return (
      <ApiErrorState
        title="Timeline Unavailable"
        message={error || 'The backend returned an incomplete timeline response.'}
        traceId={traceId}
        onRetry={onRetry}
      />
    )
  }

  // Sort events by date
  const sortedEvents = [...events].sort((a, b) => new Date(a.date) - new Date(b.date));

  // Helper functions for styling
  const getEventTypeConfig = (type) => {
    switch (type) {
      case 'event':
        return { color: '#007bff', icon: '📅', label: 'Event' };
      case 'deadline':
        return { color: '#dc3545', icon: '⏰', label: 'Deadline' };
      case 'milestone':
        return { color: '#28a745', icon: '🏆', label: 'Milestone' };
      case 'step':
        return { color: '#6f42c1', icon: '📋', label: 'Step' };
      default:
        return { color: '#6c757d', icon: '📝', label: 'Unknown' };
    }
  };

  const getStatusConfig = (status) => {
    switch (status) {
      case 'completed':
        return { color: '#28a745', icon: '✅', label: 'Completed' };
      case 'pending':
        return { color: '#ffc107', icon: '⏳', label: 'Pending' };
      case 'overdue':
        return { color: '#dc3545', icon: '⚠️', label: 'Overdue' };
      default:
        return { color: '#6c757d', icon: '❓', label: 'Unknown' };
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
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
        Case Timeline - {caseId}
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

      {/* Timeline */}
      <div style={{ marginBottom: '20px' }}>
        <div className="section-label">Timeline Events</div>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '20px',
          position: 'relative'
        }}>
          {/* Timeline line */}
          <div style={{
            position: 'absolute',
            left: '30px',
            top: '40px',
            bottom: '40px',
            width: '2px',
            backgroundColor: '#007bff',
            zIndex: 1
          }} />

          {sortedEvents.map((event, index) => {
            const typeConfig = getEventTypeConfig(event.type);
            const statusConfig = event.status ? getStatusConfig(event.status) : null;

            return (
              <div
                key={event.id}
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '15px',
                  position: 'relative'
                }}
              >
                {/* Event icon */}
                <div style={{
                  width: '60px',
                  height: '60px',
                  borderRadius: '50%',
                  backgroundColor: typeConfig.color,
                  color: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '24px',
                  flexShrink: 0,
                  zIndex: 2,
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                }}>
                  {typeConfig.icon}
                </div>

                {/* Event content */}
                <div style={{
                  backgroundColor: '#f8f9fa',
                  padding: '15px',
                  borderRadius: '8px',
                  border: '1px solid #e9ecef',
                  flex: 1
                }}>
                  {/* Header with title, date, and status */}
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    marginBottom: '10px',
                    flexWrap: 'wrap',
                    gap: '10px'
                  }}>
                    <div style={{ flex: 1 }}>
                      <h4 style={{
                        fontSize: '1.1rem',
                        color: '#2c3e50',
                        margin: '0 0 5px 0',
                        fontWeight: '600'
                      }}>
                        {event.title}
                      </h4>
                      <div style={{
                        fontSize: '14px',
                        color: '#6c757d',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '10px'
                      }}>
                        <span>{formatDate(event.date)}</span>
                        <span style={{
                          backgroundColor: typeConfig.color,
                          color: 'white',
                          padding: '2px 6px',
                          borderRadius: '4px',
                          fontSize: '12px',
                          fontWeight: '500'
                        }}>
                          {typeConfig.label}
                        </span>
                        {statusConfig && (
                          <span style={{
                            backgroundColor: statusConfig.color,
                            color: 'white',
                            padding: '2px 6px',
                            borderRadius: '4px',
                            fontSize: '12px',
                            fontWeight: '500',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '2px'
                          }}>
                            {statusConfig.icon} {statusConfig.label}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Description */}
                  <p style={{
                    margin: '0 0 10px 0',
                    color: '#495057',
                    fontSize: '14px',
                    lineHeight: '1.5'
                  }}>
                    {event.description}
                  </p>

                  {/* Additional details */}
                  {(event.documents && event.documents.length > 0) || (event.parties && event.parties.length > 0) ? (
                    <div style={{
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '8px',
                      fontSize: '13px',
                      color: '#6c757d'
                    }}>
                      {event.documents && event.documents.length > 0 && (
                        <div>
                          <strong>Documents:</strong> {event.documents.join(', ')}
                        </div>
                      )}
                      {event.parties && event.parties.length > 0 && (
                        <div>
                          <strong>Parties:</strong> {event.parties.join(', ')}
                        </div>
                      )}
                    </div>
                  ) : null}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default TimelineCard;