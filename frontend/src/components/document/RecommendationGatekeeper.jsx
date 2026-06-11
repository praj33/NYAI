/**
 * RecommendationGatekeeper.jsx
 *
 * Advisory-only routing based on recommendation.type.
 * No content is withheld — NYAI is advisory only.
 *
 * INFORM            → Full document view
 * REVIEW            → Full document view + review notice banner
 * ESCALATE          → Full document view + escalation notice banner
 * INSUFFICIENT_DATA → Reduced view + clarification request
 */
import React from 'react'
import GravitasDocumentView from './GravitasDocumentView.jsx'
import ApiErrorState from '../ApiErrorState.jsx'

const RecommendationGatekeeper = ({ casePayload, onFeedback }) => {
  const recommendation = casePayload?.recommendation
  const recType = recommendation?.type || 'INSUFFICIENT_DATA'
  const traceId = casePayload?.trace_id ?? null

  if (!casePayload) {
    return (
      <ApiErrorState
        title="Payload Unavailable"
        message="Cannot render document: case payload is missing."
        traceId={traceId}
      />
    )
  }

  const reviewBanner = (message) => (
    <div style={{
      padding: '12px 16px',
      marginBottom: '16px',
      backgroundColor: 'rgba(255, 193, 7, 0.15)',
      border: '1px solid rgba(255, 193, 7, 0.4)',
      borderRadius: '8px',
      color: '#856404'
    }}>
      <strong>Advisory Notice:</strong> {message}
    </div>
  )

  switch (recType) {
    case 'INFORM':
      return (
        <GravitasDocumentView
          casePayload={casePayload}
          onFeedback={onFeedback}
        />
      )

    case 'REVIEW':
      return (
        <>
          {reviewBanner(recommendation?.rationale || 'Additional review is recommended before acting on this guidance.')}
          <GravitasDocumentView
            casePayload={casePayload}
            onFeedback={onFeedback}
          />
        </>
      )

    case 'ESCALATE':
      return (
        <>
          {reviewBanner(recommendation?.rationale || 'Consider consulting a qualified legal professional for this matter.')}
          <GravitasDocumentView
            casePayload={casePayload}
            onFeedback={onFeedback}
          />
        </>
      )

    case 'INSUFFICIENT_DATA':
    default:
      return (
        <div style={{ padding: '24px' }}>
          {reviewBanner(recommendation?.rationale || 'Insufficient data to provide reliable legal guidance. Please refine your query.')}
          <ApiErrorState
            title="Clarification Needed"
            message="The system could not produce a complete advisory response. Please provide more specific details about your legal question."
            traceId={traceId}
          />
        </div>
      )
  }
}

export default RecommendationGatekeeper
