# INPUT_VALIDATION_AUDIT.md
## NYAI Public Endpoint Input Validation Audit
**Sprint:** Production Hardening — ARYA Quadruped Physical Prototype Readiness  
**Date:** June 2026  
**Scope:** `backend/api/router.py`, `backend/api/procedure_router.py`

---

## Summary

| Classification | Count |
|----------------|-------|
| **PASS** | 18 |
| **WARN** | 14 |
| **FAIL** | 0 |

**Overall assessment:** All endpoints use Pydantic request models or typed path/query parameters. No endpoint accepts fully arbitrary unvalidated input. Primary gaps are missing length/format constraints on free-text fields and path parameters.

### Top 3 Recommendations (Next Sprint)

1. Add `min_length` / `max_length` on `QueryRequest.query` (e.g. 3–4000 chars) to prevent oversized payloads and empty queries after trim.
2. Validate `trace_id` path/query parameters with UUID or trace format regex across replay endpoints.
3. Constrain procedure `country` and `domain` path params to known enum values from `procedure_loader`.

---

## Endpoint Audit

### POST /nyaya/query

| Field | Type | Validation | Risk | Recommendation |
|-------|------|------------|------|----------------|
| `query` | `str` | Required, type only | **WARN** | Add `min_length=3`, `max_length=4000` |
| `jurisdiction_hint` | `JurisdictionHint` enum | Optional enum | **PASS** | — |
| `domain_hint` | `DomainHint` enum | Optional enum | **PASS** | — |
| `user_context.role` | `UserRole` enum | Required enum | **PASS** | — |
| `user_context.confidence_required` | `bool` | Default `True` | **PASS** | — |

---

### POST /nyaya/multi_jurisdiction

| Field | Type | Validation | Risk | Recommendation |
|-------|------|------------|------|----------------|
| `query` | `str` | Required, type only | **WARN** | Add length bounds |
| `jurisdictions` | `List[JurisdictionHint]` | `min_items=1`, `max_items=3` | **PASS** | — |

---

### POST /nyaya/explain_reasoning

| Field | Type | Validation | Risk | Recommendation |
|-------|------|------------|------|----------------|
| `trace_id` | `str` | Required, type only | **WARN** | Add UUID/trace format validator |
| `explanation_level` | `ExplanationLevel` enum | Required enum | **PASS** | — |

---

### POST /nyaya/feedback

| Field | Type | Validation | Risk | Recommendation |
|-------|------|------------|------|----------------|
| `trace_id` | `str` | Required | **WARN** | Add format validator |
| `rating` | `int` | `ge=1`, `le=5` | **PASS** | — |
| `feedback_type` | `FeedbackType` enum | Required enum | **PASS** | — |
| `comment` | `Optional[str]` | `max_length=1000` | **PASS** | — |

---

### POST /nyaya/tantra_flow

| Field | Type | Validation | Risk | Recommendation |
|-------|------|------------|------|----------------|
| Body | `Dict` / inline | Handler-specific | **WARN** | Document and schema-bind request body |

---

### POST /nyaya/rl_signal

| Field | Type | Validation | Risk | Recommendation |
|-------|------|------------|------|----------------|
| `trace_id` | `str` | Required (inline model) | **WARN** | Add format validator |
| `signal_type` | `str` | Default string | **WARN** | Constrain to enum |
| `user_feedback` | `Optional[str]` | Default string | **WARN** | `max_length` |
| `outcome_tag` | `Optional[str]` | Default string | **WARN** | Constrain to enum |

---

### GET /nyaya/trace/{trace_id}

| Field | Type | Validation | Risk | Recommendation |
|-------|------|------------|------|----------------|
| `trace_id` | path `str` | Type only | **WARN** | Format validator |

---

### GET /nyaya/output/{trace_id}

| Field | Type | Validation | Risk | Recommendation |
|-------|------|------------|------|----------------|
| `trace_id` | path `str` | Type only | **WARN** | Format validator |

---

### GET /nyaya/recommendation_status

| Field | Type | Validation | Risk | Recommendation |
|-------|------|------------|------|----------------|
| `trace_id` | query `str` | Required query param | **WARN** | Format validator |

---

### POST /nyaya/procedures/analyze

| Field | Type | Validation | Risk | Recommendation |
|-------|------|------------|------|----------------|
| `country` | `str` | Required | **WARN** | Enum from loader |
| `domain` | `str` | Required | **WARN** | Enum from loader |
| `current_step` | `Optional[str]` | Optional | **WARN** | Enum from taxonomy |

---

### GET /nyaya/procedures/summary/{country}/{domain}

| Field | Type | Validation | Risk | Recommendation |
|-------|------|------------|------|----------------|
| `country` | path `str` | Type only | **WARN** | Enum validation |
| `domain` | path `str` | Type only | **WARN** | Enum validation |

---

### POST /nyaya/procedures/evidence/assess

| Field | Type | Validation | Risk | Recommendation |
|-------|------|------------|------|----------------|
| `canonical_step` | `str` | Required | **WARN** | Taxonomy enum |
| `available_documents` | `List[str]` | Required list | **WARN** | `max_length` per item |

---

### POST /nyaya/procedures/failure/analyze

| Field | Type | Validation | Risk | Recommendation |
|-------|------|------------|------|----------------|
| `failure_code` | `str` | Required | **WARN** | Known failure code enum |

---

### POST /nyaya/procedures/compare

| Field | Type | Validation | Risk | Recommendation |
|-------|------|------------|------|----------------|
| `countries` | `List[str]` | `min_items=2`, `max_items=4` | **PASS** | Consider country enum |
| `domain` | `str` | Required | **WARN** | Domain enum |

---

### GET /nyaya/procedures/list

| Field | Type | Validation | Risk | Recommendation |
|-------|------|------------|------|----------------|
| (none) | — | No body | **PASS** | — |

---

### GET /nyaya/procedures/schemas

| Field | Type | Validation | Risk | Recommendation |
|-------|------|------------|------|----------------|
| (none) | — | No body | **PASS** | — |

---

*Audit performed against Pydantic schemas in `api/schemas.py` and route signatures in `router.py` / `procedure_router.py`. No `enforcement_decision` fields present.*
