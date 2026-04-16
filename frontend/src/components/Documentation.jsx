import React, { useState } from 'react'
import { procedureService } from '../services/nyayaApi.js'

const Documentation = ({ onBack }) => {
  const [activeSection, setActiveSection] = useState('overview')
  const [testResults, setTestResults] = useState({})
  const [testing, setTesting] = useState(false)

  const testEndpoint = async (name, testFn) => {
    setTesting(true)
    setTestResults(prev => ({ ...prev, [name]: 'Testing...' }))
    try {
      const result = await testFn()
      setTestResults(prev => ({ ...prev, [name]: result.success ? '✅ Success' : `❌ ${result.error}` }))
    } catch (error) {
      setTestResults(prev => ({ ...prev, [name]: `❌ ${error.message}` }))
    }
    setTesting(false)
  }

  const sections = {
    overview: {
      title: 'Platform Overview',
      content: [
        { heading: 'What is Nyaya AI?', text: 'Nyaya AI is a sovereign-compliant multi-agent legal intelligence platform that provides transparent, auditable legal analysis across India, UK, and UAE jurisdictions.' },
        { heading: 'Key Features', text: 'AI-powered legal question answering, jurisdiction-specific procedures, case timeline generation, and comprehensive legal glossary.' },
        { heading: 'How It Works', text: 'Ask your legal question, receive AI-powered analysis with confidence scores, get suggested next steps, and view jurisdiction-specific procedures.' }
      ]
    },
    features: {
      title: 'Features Guide',
      content: [
        { heading: 'Ask Legal Question', text: 'Submit your legal query and receive instant AI-powered analysis with confidence scores, suggested next steps, and jurisdiction-specific procedures tailored to your case type.' },
        { heading: 'Jurisdiction Procedure', text: 'Navigate through step-by-step legal procedures for India, UK, and UAE. Each procedure includes timelines, descriptions, and jurisdiction-specific requirements.' },
        { heading: 'Case Timeline', text: 'Generate comprehensive timelines for your legal case by adding events, milestones, and deadlines. Visualize your case progression with our interactive timeline tool.' },
        { heading: 'Legal Glossary', text: 'Search and explore legal terms across multiple jurisdictions. Filter by India, UK, or UAE to find relevant definitions and explanations.' }
      ]
    },
    laws: {
      title: 'Understanding Laws',
      content: [
        { heading: 'Indian Law', text: 'India follows a common law system with codified laws. Key acts include the Indian Contract Act 1872, Indian Penal Code 1860, and Constitution of India. The legal system has three tiers: District Courts, High Courts, and Supreme Court.' },
        { heading: 'UK Law', text: 'The UK operates under common law with parliamentary sovereignty. Key areas include contract law, tort law, and criminal law. The court system includes Magistrates Courts, Crown Courts, Court of Appeal, and Supreme Court.' },
        { heading: 'UAE Law', text: 'UAE follows a civil law system based on Sharia principles for personal matters and civil codes for commercial matters. The legal system includes Court of First Instance, Court of Appeal, and Court of Cassation.' },
        { heading: 'Legal Procedures', text: 'Each jurisdiction has specific procedures for filing cases, presenting evidence, and appealing decisions. Understanding these procedures is crucial for effective legal action.' }
      ]
    },
    howto: {
      title: 'How to Use',
      content: [
        { heading: 'Step 1: Ask Your Question', text: 'Click "Ask Legal Question" and describe your legal situation in detail. Include relevant facts, dates, and parties involved for better analysis.' },
        { heading: 'Step 2: Review Analysis', text: 'Read the AI-generated legal assessment, confidence score, and jurisdiction determination. Review suggested next steps with priority levels and timelines.' },
        { heading: 'Step 3: Follow Procedures', text: 'Check the jurisdiction-specific procedure section to understand the step-by-step process for your case type (contract, property, criminal, etc.).' },
        { heading: 'Step 4: Use Tools', text: 'Explore additional tools like Timeline Generator for case planning, Glossary for term definitions, and Procedure Navigator for detailed jurisdiction workflows.' },
        { heading: 'Step 5: Provide Feedback', text: 'Help improve the system by providing feedback on response helpfulness, clarity, and accuracy using the feedback buttons.' }
      ]
    },
    faq: {
      title: 'FAQ',
      content: [
        { heading: 'Is this legal advice?', text: 'No. Nyaya AI provides legal information and analysis, not legal advice. Always consult a qualified lawyer for specific legal advice on your situation.' },
        { heading: 'Which jurisdictions are supported?', text: 'Currently, Nyaya AI supports India, United Kingdom, and United Arab Emirates. Each jurisdiction has specific procedures and legal frameworks.' },
        { heading: 'How accurate is the AI?', text: 'The AI provides confidence scores with each analysis. Higher confidence (>80%) indicates stronger analysis, but always verify with legal professionals.' },
        { heading: 'Can I save my queries?', text: 'Each query generates a trace ID for tracking. You can reference this ID for follow-up questions or to retrieve analysis history.' },
        { heading: 'What case types are covered?', text: 'Contract disputes, property disputes, criminal matters, civil litigation, family law, employment law, and more across all supported jurisdictions.' }
      ]
    },
    api: {
      title: 'Test API Endpoints',
      content: [
        { heading: 'Procedure Endpoints', text: 'Test all backend procedure endpoints to verify connectivity and functionality.' }
      ]
    }
  }

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
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
        <h1 style={{ color: '#fff', fontSize: '32px', marginBottom: '12px' }}>Documentation</h1>
        <p style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '16px', marginBottom: '32px' }}>
          Learn how to use Nyaya AI and understand legal procedures across jurisdictions
        </p>

        {/* Navigation Tabs */}
        <div style={{ display: 'flex', gap: '12px', marginBottom: '32px', flexWrap: 'wrap' }}>
          {Object.keys(sections).map(key => (
            <button
              key={key}
              onClick={() => setActiveSection(key)}
              style={{
                padding: '10px 20px',
                border: activeSection === key ? '2px solid #3b82f6' : '2px solid rgba(255, 255, 255, 0.2)',
                borderRadius: '8px',
                background: activeSection === key ? 'rgba(59, 130, 246, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                color: '#fff',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '600',
                textTransform: 'capitalize'
              }}
            >
              {sections[key].title}
            </button>
          ))}
        </div>

        {/* Content Section */}
        <div>
          <h2 style={{ color: '#fff', fontSize: '24px', marginBottom: '24px', borderBottom: '2px solid rgba(59, 130, 246, 0.5)', paddingBottom: '12px' }}>
            {sections[activeSection].title}
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {sections[activeSection].content.map((item, idx) => (
              <div
                key={idx}
                style={{
                  padding: '24px',
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '12px'
                }}
              >
                <h3 style={{ color: '#fff', fontSize: '18px', marginBottom: '12px', fontWeight: '600' }}>
                  {item.heading}
                </h3>
                <p style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '15px', lineHeight: '1.7', margin: 0 }}>
                  {item.text}
                </p>
              </div>
            ))}
          </div>

          {/* API Testing Section */}
          {activeSection === 'api' && (
            <div style={{ marginTop: '24px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '12px' }}>
              <button onClick={() => testEndpoint('list', () => procedureService.listProcedures())} disabled={testing} style={{ padding: '12px', background: 'rgba(59, 130, 246, 0.2)', border: '1px solid rgba(59, 130, 246, 0.4)', borderRadius: '8px', color: '#fff', cursor: 'pointer', fontSize: '13px' }}>
                Test List Procedures {testResults.list}
              </button>
              <button onClick={() => testEndpoint('schemas', () => procedureService.getSchemas())} disabled={testing} style={{ padding: '12px', background: 'rgba(59, 130, 246, 0.2)', border: '1px solid rgba(59, 130, 246, 0.4)', borderRadius: '8px', color: '#fff', cursor: 'pointer', fontSize: '13px' }}>
                Test Get Schemas {testResults.schemas}
              </button>
              <button onClick={() => testEndpoint('summary', () => procedureService.getProcedureSummary('IN', 'civil'))} disabled={testing} style={{ padding: '12px', background: 'rgba(59, 130, 246, 0.2)', border: '1px solid rgba(59, 130, 246, 0.4)', borderRadius: '8px', color: '#fff', cursor: 'pointer', fontSize: '13px' }}>
                Test Procedure Summary {testResults.summary}
              </button>
              <button onClick={() => testEndpoint('enhanced', () => procedureService.getEnhancedAnalysis('IN', 'civil'))} disabled={testing} style={{ padding: '12px', background: 'rgba(59, 130, 246, 0.2)', border: '1px solid rgba(59, 130, 246, 0.4)', borderRadius: '8px', color: '#fff', cursor: 'pointer', fontSize: '13px' }}>
                Test Enhanced Analysis {testResults.enhanced}
              </button>
              <button onClick={() => testEndpoint('domain', () => procedureService.getDomainClassification('IN'))} disabled={testing} style={{ padding: '12px', background: 'rgba(59, 130, 246, 0.2)', border: '1px solid rgba(59, 130, 246, 0.4)', borderRadius: '8px', color: '#fff', cursor: 'pointer', fontSize: '13px' }}>
                Test Domain Classification {testResults.domain}
              </button>
              <button onClick={() => testEndpoint('sections', () => procedureService.getLegalSections('IN', 'civil'))} disabled={testing} style={{ padding: '12px', background: 'rgba(59, 130, 246, 0.2)', border: '1px solid rgba(59, 130, 246, 0.4)', borderRadius: '8px', color: '#fff', cursor: 'pointer', fontSize: '13px' }}>
                Test Legal Sections {testResults.sections}
              </button>
            </div>
          )}
        </div>

        {/* Quick Links */}
        <div style={{ marginTop: '40px', padding: '24px', background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.3)', borderRadius: '12px' }}>
          <h3 style={{ color: '#fff', fontSize: '18px', marginBottom: '16px' }}>Quick Links</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
            <div style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '14px' }}>→ Ask Legal Question</div>
            <div style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '14px' }}>→ Jurisdiction Procedure</div>
            <div style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '14px' }}>→ Case Timeline</div>
            <div style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '14px' }}>→ Legal Glossary</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Documentation
