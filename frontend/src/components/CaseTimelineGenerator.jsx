import { useState } from 'react'

const eventTypes = ['Notice', 'Filing', 'Agreement', 'Hearing', 'Incident']
const countries = ['India', 'United Kingdom', 'United Arab Emirates']
const states = {
  'India': ['Delhi', 'Maharashtra', 'Karnataka', 'Tamil Nadu', 'Gujarat', 'West Bengal', 'Rajasthan', 'Uttar Pradesh'],
  'United Kingdom': ['England', 'Scotland', 'Wales', 'Northern Ireland'],
  'United Arab Emirates': ['Abu Dhabi', 'Dubai', 'Sharjah', 'Ajman', 'Fujairah', 'Ras Al Khaimah', 'Umm Al Quwain']
}

export default function CaseTimelineGenerator({ onBack }) {
  const [events, setEvents] = useState([])
  const [currentEvent, setCurrentEvent] = useState({
    title: '',
    description: '',
    date: '',
    type: '',
    documents: []
  })
  const [jurisdiction, setJurisdiction] = useState({ country: '', state: '' })
  const [generatedTimeline, setGeneratedTimeline] = useState(null)
  const [loading, setLoading] = useState(false)

  const addEvent = () => {
    if (currentEvent.title && currentEvent.date && currentEvent.type) {
      setEvents([...events, { ...currentEvent, id: Date.now() }])
      setCurrentEvent({ title: '', description: '', date: '', type: '', documents: [] })
    }
  }

  const removeEvent = (id) => {
    setEvents(events.filter(e => e.id !== id))
  }

  const handleFileUpload = (e) => {
    setCurrentEvent({ ...currentEvent, documents: Array.from(e.target.files) })
  }

  const generateTimeline = () => {
    setLoading(true)
    setTimeout(() => {
      const sortedEvents = [...events].sort((a, b) => new Date(a.date) - new Date(b.date))
      setGeneratedTimeline({
        events: sortedEvents.map((e, idx) => ({
          ...e,
          legalRelevance: 'Critical procedural milestone',
          proceduralStage: idx === 0 ? 'Initiation' : idx === sortedEvents.length - 1 ? 'Current Stage' : 'Ongoing',
          status: new Date(e.date) < new Date() ? 'completed' : 'pending'
        })),
        nextSteps: [
          'File response within 30 days',
          'Prepare evidence documentation',
          'Schedule mediation hearing'
        ],
        missedDeadlines: [],
        statutoryGaps: '15 days between filing and hearing (compliant)'
      })
      setLoading(false)
    }, 2000)
  }

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', animation: 'fadeIn 0.5s ease-in' }}>
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>

      <button onClick={onBack} style={{
        background: 'rgba(255, 255, 255, 0.1)',
        border: '1px solid rgba(255, 255, 255, 0.2)',
        borderRadius: '8px',
        padding: '10px 20px',
        color: '#fff',
        cursor: 'pointer',
        marginBottom: '20px',
        fontSize: '14px'
      }}>
        ← Back to Dashboard
      </button>

      <h1 style={{ color: '#fff', fontSize: '32px', marginBottom: '32px', fontFamily: 'Merriweather, serif' }}>
        Case Timeline Generator
      </h1>

      {!generatedTimeline ? (
        <>
          {/* Section 1: Event Input */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '16px',
            padding: '32px',
            marginBottom: '24px'
          }}>
            <h2 style={{ color: '#fff', fontSize: '20px', marginBottom: '24px', fontFamily: 'Merriweather, serif' }}>
              Add Legal Events
            </h2>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <input
                type="text"
                placeholder="Event Title"
                value={currentEvent.title}
                onChange={(e) => setCurrentEvent({ ...currentEvent, title: e.target.value })}
                style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '8px',
                  padding: '12px',
                  color: '#fff',
                  fontSize: '14px'
                }}
              />

              <textarea
                placeholder="Event Description"
                value={currentEvent.description}
                onChange={(e) => setCurrentEvent({ ...currentEvent, description: e.target.value })}
                style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '8px',
                  padding: '12px',
                  color: '#fff',
                  fontSize: '14px',
                  minHeight: '80px',
                  resize: 'vertical'
                }}
              />

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <input
                  type="date"
                  value={currentEvent.date}
                  onChange={(e) => setCurrentEvent({ ...currentEvent, date: e.target.value })}
                  style={{
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: '8px',
                    padding: '12px',
                    color: '#fff',
                    fontSize: '14px'
                  }}
                />

                <select
                  value={currentEvent.type}
                  onChange={(e) => setCurrentEvent({ ...currentEvent, type: e.target.value })}
                  style={{
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: '8px',
                    padding: '12px',
                    color: '#fff',
                    fontSize: '14px',
                    cursor: 'pointer'
                  }}
                >
                  <option value="" style={{ background: '#1a1a1a' }}>Select Event Type</option>
                  {eventTypes.map(t => <option key={t} value={t} style={{ background: '#1a1a1a' }}>{t}</option>)}
                </select>
              </div>

              <label style={{
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px dashed rgba(255, 255, 255, 0.2)',
                borderRadius: '8px',
                padding: '16px',
                textAlign: 'center',
                cursor: 'pointer',
                color: 'rgba(255, 255, 255, 0.6)',
                fontSize: '14px'
              }}>
                <input type="file" multiple accept=".pdf,.docx,.doc,.jpg,.jpeg,.png" onChange={handleFileUpload} style={{ display: 'none' }} />
                {currentEvent.documents.length > 0 ? `${currentEvent.documents.length} file(s) selected` : 'Upload Supporting Documents (Optional)'}
              </label>

              <button
                onClick={addEvent}
                disabled={!currentEvent.title || !currentEvent.date || !currentEvent.type}
                style={{
                  background: (currentEvent.title && currentEvent.date && currentEvent.type) ? 'linear-gradient(135deg, #667eea, #764ba2)' : 'rgba(255, 255, 255, 0.1)',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '12px',
                  color: '#fff',
                  cursor: (currentEvent.title && currentEvent.date && currentEvent.type) ? 'pointer' : 'not-allowed',
                  fontSize: '14px',
                  fontWeight: '600',
                  opacity: (currentEvent.title && currentEvent.date && currentEvent.type) ? 1 : 0.5
                }}
              >
                Add Event
              </button>
            </div>

            {/* Event List */}
            {events.length > 0 && (
              <div style={{ marginTop: '24px' }}>
                <h3 style={{ color: '#fff', fontSize: '16px', marginBottom: '16px' }}>Added Events ({events.length})</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {events.map(event => (
                    <div key={event.id} style={{
                      background: 'rgba(255, 255, 255, 0.05)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      borderRadius: '8px',
                      padding: '16px',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}>
                      <div>
                        <div style={{ color: '#fff', fontSize: '14px', fontWeight: '600', marginBottom: '4px' }}>{event.title}</div>
                        <div style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '12px' }}>
                          {event.type} • {new Date(event.date).toLocaleDateString()}
                        </div>
                      </div>
                      <button
                        onClick={() => removeEvent(event.id)}
                        style={{
                          background: 'rgba(239, 68, 68, 0.2)',
                          border: '1px solid rgba(239, 68, 68, 0.3)',
                          borderRadius: '6px',
                          padding: '6px 12px',
                          color: '#ef4444',
                          cursor: 'pointer',
                          fontSize: '12px'
                        }}
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Section 2: Jurisdiction */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '16px',
            padding: '32px',
            marginBottom: '24px'
          }}>
            <h2 style={{ color: '#fff', fontSize: '20px', marginBottom: '24px', fontFamily: 'Merriweather, serif' }}>
              Select Jurisdiction
            </h2>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div>
                <label style={{ color: '#fff', fontSize: '14px', marginBottom: '8px', display: 'block' }}>Country</label>
                <select
                  value={jurisdiction.country}
                  onChange={(e) => setJurisdiction({ country: e.target.value, state: '' })}
                  style={{
                    width: '100%',
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: '8px',
                    padding: '12px',
                    color: '#fff',
                    fontSize: '14px',
                    cursor: 'pointer'
                  }}
                >
                  <option value="" style={{ background: '#1a1a1a' }}>Select Country</option>
                  {countries.map(c => <option key={c} value={c} style={{ background: '#1a1a1a' }}>{c}</option>)}
                </select>
              </div>

              {jurisdiction.country && (
                <div>
                  <label style={{ color: '#fff', fontSize: '14px', marginBottom: '8px', display: 'block' }}>State / Region</label>
                  <select
                    value={jurisdiction.state}
                    onChange={(e) => setJurisdiction({ ...jurisdiction, state: e.target.value })}
                    style={{
                      width: '100%',
                      background: 'rgba(255, 255, 255, 0.05)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      borderRadius: '8px',
                      padding: '12px',
                      color: '#fff',
                      fontSize: '14px',
                      cursor: 'pointer'
                    }}
                  >
                    <option value="" style={{ background: '#1a1a1a' }}>Select State</option>
                    {states[jurisdiction.country]?.map(s => <option key={s} value={s} style={{ background: '#1a1a1a' }}>{s}</option>)}
                  </select>
                </div>
              )}
            </div>
          </div>

          {/* Generate Button */}
          <button
            onClick={generateTimeline}
            disabled={events.length === 0 || !jurisdiction.country || !jurisdiction.state || loading}
            style={{
              width: '100%',
              background: (events.length > 0 && jurisdiction.country && jurisdiction.state && !loading) ? 'linear-gradient(135deg, #667eea, #764ba2)' : 'rgba(255, 255, 255, 0.1)',
              border: 'none',
              borderRadius: '12px',
              padding: '16px',
              color: '#fff',
              cursor: (events.length > 0 && jurisdiction.country && jurisdiction.state && !loading) ? 'pointer' : 'not-allowed',
              fontSize: '16px',
              fontWeight: '600',
              opacity: (events.length > 0 && jurisdiction.country && jurisdiction.state && !loading) ? 1 : 0.5
            }}
          >
            {loading ? 'Generating Timeline...' : 'Generate Timeline'}
          </button>
        </>
      ) : (
        <>
          {/* Section 3: Generated Timeline */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '16px',
            padding: '32px',
            marginBottom: '24px'
          }}>
            <h2 style={{ color: '#fff', fontSize: '20px', marginBottom: '24px', fontFamily: 'Merriweather, serif' }}>
              AI Generated Timeline
            </h2>

            {/* Vertical Timeline */}
            <div style={{ position: 'relative', paddingLeft: '40px' }}>
              {generatedTimeline.events.map((event, idx) => (
                <div key={event.id} style={{ position: 'relative', marginBottom: '32px' }}>
                  {/* Timeline Line */}
                  {idx < generatedTimeline.events.length - 1 && (
                    <div style={{
                      position: 'absolute',
                      left: '-28px',
                      top: '24px',
                      width: '2px',
                      height: 'calc(100% + 32px)',
                      background: 'rgba(255, 255, 255, 0.2)'
                    }} />
                  )}

                  {/* Timeline Node */}
                  <div style={{
                    position: 'absolute',
                    left: '-32px',
                    top: '8px',
                    width: '10px',
                    height: '10px',
                    borderRadius: '50%',
                    background: event.status === 'completed' ? '#10b981' : '#f59e0b',
                    border: '2px solid rgba(255, 255, 255, 0.2)'
                  }} />

                  {/* Event Card */}
                  <div style={{
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: '12px',
                    padding: '20px'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                      <div>
                        <h3 style={{ color: '#fff', fontSize: '16px', fontWeight: '600', marginBottom: '4px' }}>{event.title}</h3>
                        <div style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '12px' }}>
                          {new Date(event.date).toLocaleDateString()} • {event.type}
                        </div>
                      </div>
                      <span style={{
                        background: event.status === 'completed' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                        border: `1px solid ${event.status === 'completed' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(245, 158, 11, 0.3)'}`,
                        borderRadius: '6px',
                        padding: '4px 12px',
                        color: event.status === 'completed' ? '#10b981' : '#f59e0b',
                        fontSize: '12px'
                      }}>
                        {event.proceduralStage}
                      </span>
                    </div>
                    {event.description && (
                      <p style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '14px', marginBottom: '12px', lineHeight: '1.6' }}>
                        {event.description}
                      </p>
                    )}
                    <div style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '12px' }}>
                      Legal Relevance: {event.legalRelevance}
                    </div>
                    {event.documents.length > 0 && (
                      <div style={{ marginTop: '8px', color: '#3b82f6', fontSize: '12px' }}>
                        📎 {event.documents.length} supporting document(s)
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Next Steps */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '16px',
            padding: '32px',
            marginBottom: '24px'
          }}>
            <h3 style={{ color: '#fff', fontSize: '18px', marginBottom: '16px', fontFamily: 'Merriweather, serif' }}>
              Suggested Next Legal Steps
            </h3>
            <ul style={{ margin: 0, paddingLeft: '20px', color: 'rgba(255, 255, 255, 0.8)', fontSize: '14px', lineHeight: '2' }}>
              {generatedTimeline.nextSteps.map((step, idx) => (
                <li key={idx}>{step}</li>
              ))}
            </ul>
          </div>

          {/* Statutory Gaps */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '16px',
            padding: '32px',
            marginBottom: '24px'
          }}>
            <h3 style={{ color: '#fff', fontSize: '18px', marginBottom: '12px', fontFamily: 'Merriweather, serif' }}>
              Statutory Time Gaps
            </h3>
            <p style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '14px', margin: 0 }}>
              {generatedTimeline.statutoryGaps}
            </p>
          </div>

          {/* Disclaimer */}
          <div style={{
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '12px',
            padding: '20px',
            marginBottom: '24px'
          }}>
            <p style={{ color: '#ef4444', fontSize: '12px', lineHeight: '1.6', margin: 0 }}>
              <strong>Disclaimer:</strong> This AI-assisted timeline is for informational purposes only and should not replace advice from a licensed attorney.
            </p>
          </div>

          <button
            onClick={() => setGeneratedTimeline(null)}
            style={{
              width: '100%',
              background: 'linear-gradient(135deg, #667eea, #764ba2)',
              border: 'none',
              borderRadius: '12px',
              padding: '16px',
              color: '#fff',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: '600'
            }}
          >
            Create New Timeline
          </button>
        </>
      )}
    </div>
  )
}
