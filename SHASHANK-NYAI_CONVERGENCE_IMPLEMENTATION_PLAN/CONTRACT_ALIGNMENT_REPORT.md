# CONTRACT ALIGNMENT REPORT

**Sprint:** NYAI Canonical Convergence Build  
**Date:** 11 June 2026  
**Contract:** `final_decision_contract.json` v2.0.0 / `tantra_v3`

---

## Schema Sources Table

| Source | Path | Version | Status |
|--------|------|---------|--------|
| JSON Contract | `final_decision_contract.json` | 2.0.0 / tantra_v3 | **ALIGNED** |
| Pydantic Schema | `backend/api/schemas.py` | tantra_v3 | **ALIGNED** |
| Response Builder | `backend/api/response_builder.py` | 3.0.0 | **ALIGNED** |
| Observer Pipeline | `backend/observer/pipeline.py` | tantra_v3 | **ALIGNED** |
| Frontend Validator | `frontend/src/lib/casePayloadValidator.js` | tantra_v3 | **ALIGNED** |
| Gravitas Transformer | `frontend/src/lib/GravitasResponseTransformer.js` | tantra_v3 | **ALIGNED** |

---

## Contradiction Register

| Claim | Reality | Evidence | Resolution |
|-------|---------|----------|------------|
| Contract requires `enforcement_decision` | Field deleted from live API | v1.0.0 line 27 | Updated to v2.0.0 with `recommendation` |
| ALLOW/BLOCK gating is canonical | Advisory-only model | `schemas.py:108-112` | Contract + frontend migrated to INFORM/REVIEW/ESCALATE/INSUFFICIENT_DATA |
| HMAC enforcement signing active | No HMAC code exists | Audit grep | Removed HMAC refs from enforcement_rules |
| Frontend renders enforcement badges | UI drifted from API | Pre-sprint grep | Renamed to RecommendationStatusCard / RecommendationGatekeeper |

---

## Field Migration Map (v1.0.0 → v2.0.0)

| Old Field (v1.0.0) | New Field (v2.0.0) | Notes |
|--------------------|--------------------|-------|
| `enforcement_decision` (ALLOW/RESTRICT) | `recommendation.type` (INFORM/REVIEW/ESCALATE/INSUFFICIENT_DATA) | Advisory only |
| — | `schema_version` | const `tantra_v3` |
| — | `answer_disclaimer` | Advisory disclaimer string |
| — | `request_id` | Deterministic from input_hash |
| — | `input_hash` | SHA256 canonical input |
| — | `determinism_proof` | input_hash + output_hash + version |
| — | `timestamp` | UTC ISO8601 |

**Semantic migration:** ALLOW→INFORM, RESTRICT→ESCALATE, SAFE_REDIRECT→REVIEW

---

## Verification Checklist

- [x] `final_decision_contract.json` version == `2.0.0`
- [x] `enforcement_decision` removed from contract required/properties
- [x] `recommendation` schema added with 4 canonical types
- [x] `schema_version: tantra_v3` in contract
- [x] `grep enforcement_decision backend/api/schemas.py` → 0 results
- [x] `grep enforcement_decision backend/api/response_builder.py` → 0 results
- [x] `grep enforcement_decision backend/observer/pipeline.py` → 0 results
- [x] Frontend migrated to `recommendation.type`
- [x] Metadata ownership/compatibility blocks present
