/**
 * EnforcementGatekeeper.jsx
 *
 * Intercepts enforcement_status.state and routes to the correct render path.
 * Acts as the single point of control between the backend payload and the UI.
 *
 * State → Render mapping:
 *
 *   'clear'         (ALLOW)         → Full GravitasDocumentView with all 9 fields
 *   'block'         (BLOCK)         → ComplianceBarrier only. decision + reasoning
 *                                     are destructured out and NEVER passed to any child.
 *   'escalate'      (ESCALATE)      → EscalationNotice with context + steps only.
 *                                     decision + reasoning withheld from DOM.
 *   'soft_redirect' (SOFT_REDIRECT) → Full GravitasDocumentView + RedirectModal overlay.
 *   'conditional'                   → Full GravitasDocumentView (treated as ALLOW).
 *
 * No CSS-only hiding is used for BLOCK or ESCALATE states.
 * The decision string does not enter the React virtual DOM in those paths.
 *
 * @param {{
 *   casePayload: import('../../lib/gravitas.types').CasePayload,
 *   onFeedback?: Function
 * }} props
 */
import React from 'react'
import GravitasDocumentView from './GravitasDocumentView.jsx'
import ComplianceBarrier from './ComplianceBarrier.jsx'
import EscalationNotice from './EscalationNotice.jsx'
import RedirectModal from './RedirectModal.jsx'
import ApiErrorState from '../ApiErrorState.jsx'

// ─── State → handler map ──────────────────────────────────────────────────────

const GATEKEEPER_MAP = {
  // ALLOW: full document, all 9 fields
  clear: 'ALLOW',
  conditional: 'ALLOW',

  // BLOCK: hard stop, decision withheld
  block: 'BLOCK',

  // ESCALATE: context + steps only, decision withheld
  escalate: 'ESCALATE',

  // SOFT_REDIRECT: full document + non-blocking modal
  soft_redirect: 'SOFT_REDIRECT'
}

// ─── Component ────────────────────────────────────────────────────────────────

const EnforcementGatekeeper = ({ casePayload, onFeedback }) => {
  if (!casePayload?.enforcement_status?.state) {
    return (
      <ApiErrorState
        title="Enforcement State Unavailable"
        message="Cannot render document: enforcement_status.state is missing from the payload."
        traceId={casePayload?.trace_id ?? null}
      />
    )
  }

  const { enforcement_status, trace_id } = casePayload
  const gate = GATEKEEPER_MAP[enforcement_status.state] ?? 'BLOCK'

  switch (gate) {

    // ── ALLOW ─────────────────────────────────────────────────────────────────
    case 'ALLOW':
      return (
        <GravitasDocumentView
          casePayload={casePayload}
          onFeedback={onFeedback}
        />
      )

    // ── BLOCK ─────────────────────────────────────────────────────────────────
    // Destructure decision + reasoning out of scope — they never reach the DOM.
    case 'BLOCK': {
      // eslint-disable-next-line no-unused-vars
      const { decision, reasoning, ...safePayload } = casePayload
      return (
        <ComplianceBarrier
          traceId={trace_id}
          reason={enforcement_status.reason}
          blockedPath={enforcement_status.blocked_path}
          barriers={enforcement_status.barriers}
          safeExplanation={enforcement_status.safe_explanation}
        />
      )
    }

    // ── ESCALATE ──────────────────────────────────────────────────────────────
    // decision + reasoning are destructured out and never passed to EscalationNotice.
    case 'ESCALATE': {
      // eslint-disable-next-line no-unused-vars
      const { decision, reasoning, ...safePayload } = casePayload
      return (
        <EscalationNotice
          traceId={trace_id}
          enforcementStatus={enforcement_status}
          jurisdiction={safePayload.jurisdiction}
          caseSummary={safePayload.case_summary}
          legalRoute={safePayload.legal_route}
          proceduralSteps={safePayload.procedural_steps}
          timeline={safePayload.timeline}
        />
      )
    }

    // ── SOFT_REDIRECT ─────────────────────────────────────────────────────────
    // Full document renders; non-blocking modal overlays it.
    case 'SOFT_REDIRECT':
      return (
        <>
          <GravitasDocumentView
            casePayload={casePayload}
            onFeedback={onFeedback}
          />
          <RedirectModal
            redirectSuggestion={enforcement_status.redirect_suggestion}
            safeExplanation={enforcement_status.safe_explanation}
            traceId={trace_id}
          />
        </>
      )

    // ── Unknown state — treat as BLOCK, never render decision ─────────────────
    default:
      return (
        <ComplianceBarrier
          traceId={trace_id}
          reason={`Unknown enforcement state: "${enforcement_status.state}"`}
          barriers={['Unrecognised enforcement state — rendering blocked as a precaution']}
          safeExplanation="The system received an unrecognised enforcement state. The decision cannot be displayed until this is resolved."
        />
      )
  }
}

export default EnforcementGatekeeper
