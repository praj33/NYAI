# DAY 2 — Recommendation State Testing Guide

**Updated:** 11 June 2026 (TANTRA Convergence Sprint)  
**Status:** TANTRA-CONVERGENCE READY — all gaps PASS  
**Replaces:** Legacy enforcement gate testing (pre-convergence)  
**Deliverables:** [`SHASHANK-NYAI_CONVERGENCE_IMPLEMENTATION_PLAN/`](../../../SHASHANK-NYAI_CONVERGENCE_IMPLEMENTATION_PLAN/)

---

## Recommendation Types (Canonical)

| Type | Color | Meaning |
|------|-------|---------|
| INFORM | #28a745 | Statutes matched, high confidence — advisory information |
| REVIEW | #fd7e14 | Statutes found but low jurisdiction confidence |
| ESCALATE | #dc3545 | No statutes matched — consult a legal professional |
| INSUFFICIENT_DATA | #6c757d | Insufficient data for reliable guidance |

---

## Test Files

- `frontend/src/tests/recommendation-states.test.js` — 4 mock payloads (INFORM, REVIEW, ESCALATE, INSUFFICIENT_DATA)
- `frontend/src/components/RecommendationStatusCard.jsx` — status badge component
- `frontend/src/components/document/RecommendationGatekeeper.jsx` — renders full document for all types (no blocking)

---

## Validation

1. POST `/nyaya/query` with a legal query
2. Verify `recommendation.type` is one of: INFORM, REVIEW, ESCALATE, INSUFFICIENT_DATA
3. Verify `RecommendationGatekeeper` renders full document regardless of type
4. Verify no gating or content blocking occurs

---

## Critical Field

```json
{
  "recommendation": {
    "type": "INFORM",
    "confidence": 0.85,
    "rationale": "Query resolved with N statute(s)",
    "urgency_flag": false
  }
}
```
