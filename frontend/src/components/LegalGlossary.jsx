import React, { useState } from 'react'

const glossaryTerms = [
  { term: 'Breach of Contract', definition: 'Violation of any term or condition of a contract without lawful excuse', jurisdiction: 'India' },
  { term: 'Force Majeure', definition: 'A clause that frees parties from liability when extraordinary events occur', jurisdiction: 'India' },
  { term: 'Specific Performance', definition: 'Court-ordered remedy requiring a party to perform contractual obligations', jurisdiction: 'India' },
  { term: 'Limitation Period', definition: 'Maximum time period to initiate legal action after cause of action arises', jurisdiction: 'India' },
  { term: 'Arbitration', definition: 'Binding dispute resolution through private arbitration tribunal', jurisdiction: 'India' },
  { term: 'Tort', definition: 'Civil wrong that causes harm or loss to another person', jurisdiction: 'UK' },
  { term: 'Injunction', definition: 'Court order requiring a party to do or refrain from doing specific acts', jurisdiction: 'UK' },
  { term: 'Damages', definition: 'Monetary compensation awarded for loss or injury', jurisdiction: 'UAE' }
]

const LegalGlossary = ({ onBack }) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedJurisdiction, setSelectedJurisdiction] = useState('All')

  const filteredTerms = glossaryTerms.filter(item => {
    const matchesSearch = item.term.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.definition.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesJurisdiction = selectedJurisdiction === 'All' || item.jurisdiction === selectedJurisdiction
    return matchesSearch && matchesJurisdiction
  })

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <button
        onClick={onBack}
        style={{
          background: 'rgba(255, 255, 255, 0.1)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderRadius: '8px',
          padding: '10px 20px',
          color: '#fff',
          cursor: 'pointer',
          marginBottom: '20px',
          fontSize: '14px'
        }}
      >
        ← Back to Dashboard
      </button>

      <div style={{
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '16px',
        padding: '32px'
      }}>
        <h2 style={{ color: '#fff', fontSize: '24px', marginBottom: '24px' }}>Legal Glossary</h2>

        {/* Search and Filter */}
        <div style={{ marginBottom: '24px' }}>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search legal terms..."
            style={{
              width: '100%',
              padding: '12px 16px',
              background: 'rgba(255, 255, 255, 0.1)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '8px',
              color: '#fff',
              fontSize: '14px',
              marginBottom: '12px'
            }}
          />
          <div style={{ display: 'flex', gap: '12px' }}>
            {['All', 'India', 'UK', 'UAE'].map(jurisdiction => (
              <button
                key={jurisdiction}
                onClick={() => setSelectedJurisdiction(jurisdiction)}
                style={{
                  padding: '8px 16px',
                  border: selectedJurisdiction === jurisdiction ? '2px solid #f59e0b' : '2px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '8px',
                  background: selectedJurisdiction === jurisdiction ? 'rgba(245, 158, 11, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                  color: '#fff',
                  cursor: 'pointer',
                  fontSize: '13px',
                  fontWeight: '600'
                }}
              >
                {jurisdiction}
              </button>
            ))}
          </div>
        </div>

        {/* Terms List */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {filteredTerms.length > 0 ? (
            filteredTerms.map((item, idx) => (
              <div
                key={idx}
                style={{
                  padding: '20px',
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '12px'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '8px' }}>
                  <h3 style={{ color: '#fff', fontSize: '18px', margin: 0 }}>{item.term}</h3>
                  <span style={{
                    padding: '4px 12px',
                    background: 'rgba(245, 158, 11, 0.2)',
                    border: '1px solid rgba(245, 158, 11, 0.4)',
                    borderRadius: '12px',
                    color: '#f59e0b',
                    fontSize: '12px',
                    fontWeight: '600'
                  }}>
                    {item.jurisdiction}
                  </span>
                </div>
                <p style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '14px', lineHeight: '1.6', margin: 0 }}>
                  {item.definition}
                </p>
              </div>
            ))
          ) : (
            <div style={{ textAlign: 'center', padding: '40px', color: 'rgba(255, 255, 255, 0.5)' }}>
              No terms found matching your search
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default LegalGlossary
