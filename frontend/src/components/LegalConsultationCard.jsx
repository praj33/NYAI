import React, { useState } from 'react'

const LegalConsultationCard = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    legalIssue: '',
    urgency: 'routine',
    preferredTime: '',
    jurisdiction: 'India'
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSubmitting(true)

    // Simulate API call
    try {
      setTimeout(() => {
        setSubmitted(true)
        setIsSubmitting(false)
      }, 2000)
    } catch (error) {
      console.error('Error:', error)
      setIsSubmitting(false)
    }
  }

  if (submitted) {
    return (
      <div className="consultation-card">
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <h2 style={{
            fontSize: '1.5rem',
            color: '#28a745',
            marginBottom: '15px'
          }}>
            Consultation Request Recorded
          </h2>
          <p style={{
            color: '#6c757d',
            marginBottom: '20px',
            lineHeight: '1.6'
          }}>
            Your consultation request has been logged. A legal representative will review your case details and contact you within 24 hours to coordinate the consultation.
          </p>
          <div style={{
            backgroundColor: '#f8f9fa',
            padding: '15px',
            borderRadius: '8px',
            border: '1px solid #e9ecef'
          }}>
            <strong>Next Steps:</strong>
            <ul style={{ textAlign: 'left', marginTop: '10px', paddingLeft: '20px' }}>
              <li>Our legal team will review your case details</li>
              <li>We'll reach out to coordinate a consultation time</li>
              <li>Please prepare any relevant documentation for our meeting</li>
            </ul>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="consultation-card">
      {/* Advisory-Style Heading */}
      <h2 style={{
        fontSize: '1.5rem',
        color: '#2c3e50',
        marginBottom: '20px',
        fontWeight: '400'
      }}>
        Arrange a Comprehensive Legal Consultation
      </h2>

      <p style={{
        color: '#6c757d',
        marginBottom: '25px',
        fontSize: '14px'
      }}>
        Comprehensive legal consultation for complex matters requiring jurisdiction-specific analysis and personalized legal strategy.
      </p>

      <form onSubmit={handleSubmit}>
        {/* Personal Information Section */}
        <div className="consultation-section">
          <div className="section-label">Your Contact Details</div>
          <div style={{ display: 'grid', gap: '15px', marginBottom: '20px' }}>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              placeholder="Full Name"
              required
              style={{
                padding: '12px',
                border: '1px solid #e9ecef',
                borderRadius: '6px',
                fontSize: '14px'
              }}
            />
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              placeholder="Email Address"
              required
              style={{
                padding: '12px',
                border: '1px solid #e9ecef',
                borderRadius: '6px',
                fontSize: '14px'
              }}
            />
            <input
              type="tel"
              name="phone"
              value={formData.phone}
              onChange={handleInputChange}
              placeholder="Phone Number"
              required
              style={{
                padding: '12px',
                border: '1px solid #e9ecef',
                borderRadius: '6px',
                fontSize: '14px'
              }}
            />
          </div>
        </div>

        {/* Legal Matter Section */}
        <div className="consultation-section">
          <div className="section-label">Describe Your Legal Issue</div>
          <textarea
            name="legalIssue"
            value={formData.legalIssue}
            onChange={handleInputChange}
            placeholder="Kindly provide a detailed account of your legal matter, including key facts, chronology, pertinent documents, and your desired outcome. This will enable me to prepare thoroughly for our discussion."
            required
            className="consultation-input"
            style={{ minHeight: '120px' }}
          />
        </div>

        {/* Additional Details */}
        <div style={{ display: 'grid', gap: '15px', marginBottom: '20px' }}>
          <div>
            <label style={{
              display: 'block',
              marginBottom: '5px',
              fontSize: '14px',
              fontWeight: '600',
              color: '#495057'
            }}>
              Level of Urgency
            </label>
            <select
              name="urgency"
              value={formData.urgency}
              onChange={handleInputChange}
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #e9ecef',
                borderRadius: '6px',
                fontSize: '14px'
              }}
            >
              <option value="routine">Standard - Within 7 days</option>
              <option value="urgent">Priority - Within 2-3 days</option>
              <option value="emergency">Immediate - Today if possible</option>
            </select>
          </div>

          <div>
            <label style={{
              display: 'block',
              marginBottom: '5px',
              fontSize: '14px',
              fontWeight: '600',
              color: '#495057'
            }}>
              Applicable Jurisdiction
            </label>
            <select
              name="jurisdiction"
              value={formData.jurisdiction}
              onChange={handleInputChange}
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #e9ecef',
                borderRadius: '6px',
                fontSize: '14px'
              }}
            >
              <option value="India">India</option>
              <option value="UK">United Kingdom</option>
              <option value="UAE">United Arab Emirates</option>
              <option value="Other">Other/Multiple</option>
            </select>
          </div>

          <div>
            <label style={{
              display: 'block',
              marginBottom: '5px',
              fontSize: '14px',
              fontWeight: '600',
              color: '#495057'
            }}>
              Preferred Appointment Time
            </label>
            <input
              type="datetime-local"
              name="preferredTime"
              value={formData.preferredTime}
              onChange={handleInputChange}
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #e9ecef',
                borderRadius: '6px',
                fontSize: '14px'
              }}
            />
          </div>
        </div>

        <button
          type="submit"
          className="consultation-btn"
          disabled={isSubmitting}
          style={{ width: '100%' }}
        >
          {isSubmitting ? 'Processing Your Request...' : 'Submit Consultation Request'}
        </button>
      </form>
    </div>
  )
}

export default LegalConsultationCard