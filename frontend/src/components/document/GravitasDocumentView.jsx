/**
 * GravitasDocumentView.jsx
 *
 * Parent orchestrator for the Gravitas formal legal decision document.
 * Ingests a single `casePayload` object and renders all 9 required fields
 * in the exact logical flow defined by Vedant's formatter contract:
 *
 *   1. Metadata & Verification  → DecisionHeader  (trace_id, enforcement_status, jurisdiction)
 *   2. Case Context             → CaseContext     (case_summary, legal_route)
 *   3. Procedure & Execution    → ProceduralSteps (procedural_steps)
 *                               → DecisionTimeline (timeline)
 *   4. Final Determination      → Determination   (decision, reasoning)
 *
 * Rendering rules:
 *   - Enforcement gating is handled upstream by EnforcementGatekeeper.
 *     GravitasDocumentView always renders all 9 fields when called directly.
 *   - Empty procedural_steps / timeline: formal empty state, never blank space
 *
 * @param {{ casePayload: import('../../lib/gravitas.types').CasePayload, onFeedback?: Function }} props
 */
import React from 'react'
import './GravitasDocumentView.css'
import DecisionHeader from './DecisionHeader.jsx'
import CaseContext from './CaseContext.jsx'
import ProceduralSteps from './ProceduralSteps.jsx'
import DecisionTimeline from './DecisionTimeline.jsx'
import Determination from './Determination.jsx'
import SkeletonLoader from '../SkeletonLoader.jsx'
import ApiErrorState from '../ApiErrorState.jsx'

// ─── Prop validation (runtime) ────────────────────────────────────────────────

const REQUIRED_FIELDS = [
  'trace_id', 'enforcement_status', 'jurisdiction',
  'case_summary', 'legal_route',
  'procedural_steps', 'timeline',
  'decision', 'reasoning'
]

function validatePayload(payload) {
  if (!payload || typeof payload !== 'object') {
    return 'casePayload is null or not an object'
  }
  for (const field of REQUIRED_FIELDS) {
    if (payload[field] == null) {
      return `casePayload missing required field: "${field}"`
    }
  }
  if (!payload.enforcement_status?.verdict) {
    return 'casePayload.enforcement_status missing required field: "verdict"'
  }
  return null
}

// ─── Component ────────────────────────────────────────────────────────────────

const GravitasDocumentView = ({ casePayload, loading = false, onFeedback }) => {
  if (loading) {
    return (
      <div className="gdv-document" style={{ padding: '40px' }}>
        <SkeletonLoader type="card" count={5} />
      </div>
    )
  }

  const validationError = validatePayload(casePayload)
  if (validationError) {
    return (
      <ApiErrorState
        title="Decision Document Unavailable"
        message={validationError}
        traceId={casePayload?.trace_id ?? null}
      />
    )
  }

  const {
    trace_id,
    enforcement_status,
    jurisdiction,
    case_summary,
    legal_route,
    procedural_steps,
    timeline,
    decision,
    reasoning
  } = casePayload

  const handleExport = () => {
    const blob = new Blob([JSON.stringify(casePayload, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `gravitas-decision-${trace_id.substring(0, 8)}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <article className="gdv-document">

      {/* ── 1. Metadata & Verification ── */}
      <DecisionHeader
        traceId={trace_id}
        enforcementStatus={enforcement_status}
        jurisdiction={jurisdiction}
      />

      <div className="gdv-body">
        {/* ── 2. Case Context ── */}
        <CaseContext
          caseSummary={case_summary}
          legalRoute={legal_route}
        />

        {/* ── 3. Procedure & Execution ── */}
        <ProceduralSteps proceduralSteps={procedural_steps} />
        <DecisionTimeline timeline={timeline} />

        {/* ── 4. Final Determination ── */}
        <Determination decision={decision} reasoning={reasoning} />
      </div>

      {/* ── Document Footer ── */}
      <footer className="gdv-footer">
        <span className="gdv-footer-trace">
          UUID: {trace_id}
        </span>
        <div className="gdv-footer-actions">
          {onFeedback && (
            <button
              className="gdv-btn gdv-btn-feedback"
              onClick={() => onFeedback(trace_id)}
            >
              Provide Feedback
            </button>
          )}
          <button
            className="gdv-btn gdv-btn-export"
            onClick={handleExport}
          >
            Export Document
          </button>
        </div>
      </footer>
    </article>
  )
}

export default GravitasDocumentView
