/**
 * gravitas.types.js
 * Prop interfaces for the GravitasDocumentView component hierarchy.
 * Maps exactly to Vedant's formatter casePayload contract — 9 required fields.
 *
 * TypeScript equivalent interfaces are provided as JSDoc for IDE support.
 */

/**
 * @typedef {'INFORM' | 'REVIEW' | 'ESCALATE' | 'INSUFFICIENT_DATA'} RecommendationType
 */

/**
 * @typedef {Object} Recommendation
 * @property {RecommendationType} type       - Advisory recommendation type
 * @property {number}             confidence  - Confidence score 0-1
 * @property {string}             rationale   - Human-readable advisory rationale
 * @property {boolean}            [urgency_flag] - Whether urgent professional review is advised
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
 * @property {string}           trace_id       - UUID audit identifier
 * @property {Recommendation}   recommendation - Advisory recommendation object
 * @property {string}           jurisdiction   - e.g. 'India', 'UK', 'UAE'
 * @property {string}           case_summary   - Findings of fact narrative
 * @property {string[]}         legal_route    - Statutory/regulatory framework applied
 * @property {ProceduralStep[]} procedural_steps - Ordered execution steps (may be empty)
 * @property {TimelineEvent[]}  timeline       - Chronological deadlines (may be empty)
 * @property {string}           decision       - The ultimate ruling text
 * @property {string}           reasoning      - Logical justification connecting facts to decision
 */

export {}
