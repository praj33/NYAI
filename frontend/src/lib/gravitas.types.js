/**
 * gravitas.types.js
 * Prop interfaces for the GravitasDocumentView component hierarchy.
 * Maps exactly to Vedant's formatter casePayload contract — 9 required fields.
 *
 * TypeScript equivalent interfaces are provided as JSDoc for IDE support.
 */

/**
 * @typedef {'ENFORCEABLE' | 'PENDING_REVIEW' | 'NON_ENFORCEABLE'} EnforcementVerdict
 * @typedef {'clear' | 'block' | 'escalate' | 'soft_redirect' | 'conditional'} EnforcementState
 */

/**
 * @typedef {Object} EnforcementStatus
 * @property {EnforcementState}   state                - Granular enforcement state
 * @property {EnforcementVerdict} verdict              - Gatekeeper verdict (primary UI gate)
 * @property {string}             reason               - Human-readable reason
 * @property {string[]}           barriers             - Specific blockers (NON_ENFORCEABLE only)
 * @property {string|null}        blocked_path         - Blocked pathway description
 * @property {boolean}            escalation_required  - Whether escalation is needed
 * @property {string|null}        escalation_target    - Target authority for escalation
 * @property {string|null}        redirect_suggestion  - Alternative pathway suggestion
 * @property {string}             safe_explanation     - User-facing explanation
 * @property {string}             trace_id             - Mirrors parent trace_id
 */

/**
 * @typedef {Object} ProceduralStep
 * @property {number}                          step_number  - 1-based step index
 * @property {string}                          title        - Step title
 * @property {string}                          description  - Step description
 * @property {'required'|'optional'|'conditional'} type    - Step classification
 * @property {string|null}                     deadline     - ISO date string or null
 * @property {string[]}                        documents    - Required documents list
 */

/**
 * @typedef {Object} TimelineEvent
 * @property {string}                                    id          - Unique event ID
 * @property {string}                                    date        - ISO date string
 * @property {string}                                    title       - Event title
 * @property {string}                                    description - Event description
 * @property {'event'|'deadline'|'milestone'|'step'}    type        - Event classification
 * @property {'completed'|'pending'|'overdue'}          status      - Event status
 */

/**
 * @typedef {Object} CasePayload
 * The single object ingested by GravitasDocumentView.
 * Maps exactly to Vedant's formatter output — all 9 fields required.
 *
 * @property {string}            trace_id          - UUID audit identifier
 * @property {EnforcementStatus} enforcement_status - Gatekeeper verdict object
 * @property {string}            jurisdiction      - e.g. 'India', 'UK', 'UAE'
 * @property {string}            case_summary      - Findings of fact narrative
 * @property {string[]}          legal_route       - Statutory/regulatory framework applied
 * @property {ProceduralStep[]}  procedural_steps  - Ordered execution steps (may be empty)
 * @property {TimelineEvent[]}   timeline          - Chronological deadlines (may be empty)
 * @property {string}            decision          - The ultimate ruling text
 * @property {string}            reasoning         - Logical justification connecting facts to decision
 */

export {}
