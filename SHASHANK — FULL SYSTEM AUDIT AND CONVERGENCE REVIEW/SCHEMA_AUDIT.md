# NYAI — SCHEMA AUDIT
**Audit Sprint:** NYAI Independent Forensic Audit
**Date:** 09 June 2026

---

## SCHEMA SOURCES INVENTORY

| Source | Path | Format | Version | Status |
|--------|------|--------|---------|--------|
| Python Pydantic schema | `backend/api/schemas.py` | Python class | tantra_v3 (implicit) | **CURRENT TRUTH** |
| JSON contract | `final_decision_contract.json` | JSON Schema draft 2020-12 | 1.0.0 | **STALE — DRIFTED** |
| TANTRA canonical taxonomy | `backend/procedures/schemas/canonical_taxonomy_v1.2.json` | JSON | v1.2 | Present, not validated in query path |
| Frontend types | `frontend/src/lib/gravitas.types.js` | JS module | unknown | Aligned to current schema |
| Frontend validator | `frontend/src/lib/casePayloadValidator.js` | JS module | unknown | No `enforcement_decision` references (grep verified) |
| Frontend UI components | `frontend/src/components/LegalQueryCard.jsx`, `LegalDecisionDocument.jsx`, etc. | JSX | legacy | **DRIFTED** — still expect `enforcement_decision` |
| ResponseBuilder | `backend/api/response_builder.py` | Python | 3.0.0 | **CURRENT — aligned to schemas.py** |
| ObserverPipeline | `backend/observer/pipeline.py` | Python | — | **CURRENT — aligned to schemas.py** |

---

## CRITICAL FINDING: enforcement_decision vs recommendation SPLIT

### Contract (stale — `final_decision_contract.json:27,47-50`)
```json
"required": ["domain","jurisdiction","confidence","statutes","enforcement_decision","trace_id"],
"enforcement_decision": {
  "enum": ["ALLOW","ALLOW_INFORMATIONAL","SAFE_REDIRECT","RESTRICT"],
  "description": "Sovereign enforcement decision — SINGLE SOURCE OF TRUTH for gating"
}
```

### Current Reality (`backend/api/schemas.py:108-112,138-156` — NyayaResponse)
```python
# NO enforcement_decision field exists in NyayaResponse
recommendation: Recommendation  # Advisory only — schemas.py:156
# Recommendation.type: RecommendationType.{INFORM, REVIEW, ESCALATE, INSUFFICIENT_DATA} — schemas.py:25-30
```

### Verdict
**SCHEMA SPLIT: CONFIRMED CRITICAL**
The contract describes a field that does not exist. Any system validating NYAI responses against `final_decision_contract.json` will:
- Reject responses as missing required field `enforcement_decision`
- Fail to find a gating decision value
- Have no path to interpret `recommendation` as a substitute

---

## NyayaResponse — Full Field Audit

| Field | Pydantic Type | Required? | Set in router.py? | Validated by Observer? | Validated by Builder? |
|-------|--------------|-----------|-------------------|----------------------|----------------------|
| trace_id | str | ✅ | ✅ advice.trace_id | ✅ trace continuity check | ✅ CANONICAL |
| request_id | str | ✅ | ✅ `f"req_{input_hash[:12]}"` | ✅ presence check | ✅ CANONICAL |
| input_hash | str | ✅ | ✅ SHA256 hex64 | ✅ hex64 format check | ✅ CANONICAL |
| timestamp | str | ✅ | ✅ utcnow().isoformat() | ✅ presence check | ✅ CANONICAL |
| legal_context | LegalContext | ✅ | ✅ LegalContext(...) | ✅ presence check | ✅ CANONICAL |
| domain | str | ✅ | ✅ | ❌ not in CANONICAL_FIELDS | ✅ STRUCTURAL |
| domains | List[str] | default [] | ✅ | ❌ | ❌ |
| jurisdiction | str | ✅ | ✅ | ❌ | ✅ STRUCTURAL |
| jurisdiction_detected | str | ✅ | ✅ | ❌ | ❌ |
| jurisdiction_confidence | float | ✅ | ✅ | ❌ | ❌ |
| confidence | ConfidenceSchema | ✅ | ✅ | ❌ | ✅ STRUCTURAL |
| facts | List[Fact] | ✅ | ✅ 5 Fact objects | ✅ structure validated | ✅ CANONICAL (non-empty, keys) |
| analysis | AnalysisBlock | ✅ | ✅ | ✅ presence | ✅ CANONICAL (rule_application) |
| recommendation | Recommendation | ✅ | ✅ | ✅ type enum check | ✅ CANONICAL (type enum) |
| explanation_chain | List[ExplanationStep] | ✅ | ✅ 8 steps | ✅ presence | ✅ CANONICAL (non-empty) |
| risk_flags | List[str] | default [] | ✅ conditional | ✅ presence | ✅ CANONICAL |
| determinism_proof | DeterminismProof | ✅ | ✅ SHA256 both hashes | ✅ hex64 both hashes | ✅ CANONICAL (hex64 pattern) |
| legal_route | List[str] | ✅ | ✅ 8-step list | ❌ | ✅ STRUCTURAL |
| statutes | List[StatuteSchema] | default [] | ✅ | ❌ | ❌ |
| case_laws | List[CaseLawSchema] | default [] | ✅ | ❌ | ❌ |
| answer | Optional[str] | default None | ✅ Groq or fallback | ❌ | ❌ |
| observer_validation | Optional[Dict] | default None | ✅ auto-appended | — | ❌ |
| metadata | Optional[Dict] | default None | ✅ added by builder | — | — |

---

## DeterminismProof Validator — Verified

`schemas.py:129-133`:
```python
@validator('input_hash', 'output_hash')
def must_be_hex64(cls, v):
    if len(v) != 64 or not all(c in '0123456789abcdef' for c in v):
        raise ValueError(f"Hash must be 64-char lowercase hex, got: {v[:20]}...")
    return v
```
**Status: ACTIVE** — `router.py` correctly computes both hashes with `hashlib.sha256(...).hexdigest()`.

### What is hashed

**input_hash** — SHA256 of:
```json
{"domain_hint": "<value>", "jurisdiction_hint": "<value>", "query": "<cleaned_query>"}
```
(sorted keys, UTF-8 encoded)

**output_hash** — SHA256 of:
```json
{"domain": "...", "facts": [...], "jurisdiction": "...", "recommendation": "...",
 "rule_application": [...], "statutes": [...]}
```
(sorted keys, UTF-8 encoded)

**Note:** `output_hash` does NOT include `answer` (Groq LLM text), `timestamp`, `trace_id`, or `observer_steps`. This is correct — LLM output and runtime values should not be in the determinism hash. However, it means the determinism proof does not cover the full response payload.

---

## Schema Parity Matrix

| Pair | Parity | Drift |
|------|--------|-------|
| `schemas.py` ↔ `response_builder.py` | ✅ ALIGNED | Same 11 CANONICAL_FIELDS, same VALID_RECOMMENDATION_TYPES |
| `schemas.py` ↔ `observer/pipeline.py` | ✅ ALIGNED | Same 11 CANONICAL_FIELDS, same VALID_RECOMMENDATION_TYPES |
| `schemas.py` ↔ `final_decision_contract.json` | ❌ DRIFTED | Contract requires `enforcement_decision`; schema has `recommendation` |
| `schemas.py` ↔ `casePayloadValidator.js` | ✅ ALIGNED | No `enforcement_decision` in frontend validator |
| `schemas.py` ↔ frontend UI components | ❌ DRIFTED | `LegalQueryCard.jsx`, `LegalDecisionDocument.jsx`, `nyayaBackendApi.js` still expect `enforcement_decision` |
| `schemas.py` ↔ `TRACE_PROOF_EXAMPLES.md` | ❌ DRIFTED | Examples show ALLOW/BLOCK/HMAC; none exist in schema |
| `schemas.py` ↔ root `REVIEW_PACKET.md` (Apr 23) | ❌ DRIFTED | Root review packet describes legacy `enforcement_decision` REQUIRED_FIELDS |
| `response_builder.py` ↔ `observer/pipeline.py` | ✅ ALIGNED | Double-gate uses identical field list |

---

## Versioning & Provenance Metadata

| Claim | Reality |
|-------|---------|
| Schema stamped as `tantra_v3` | Only in `metadata.schema` added by `ResponseBuilder.build()` — not in `NyayaResponse` model itself |
| `canonical_taxonomy_v1.2.json` referenced | Present at `backend/procedures/schemas/` but not imported or validated in the query path |
| Schema version field in NyayaResponse | ABSENT — no `schema_version` field |

---

## Hidden / Undocumented Fields

| Field | Location | Documented? | Risk |
|-------|----------|-------------|------|
| `confidence_sources` | `NyayaResponse` | Not in contract | Low — internal diagnostic |
| `observer_steps` | `NyayaResponse` | Not in contract | Low — internal diagnostic |
| `observer_validation` | `NyayaResponse` | Not in contract | Low — internal diagnostic |
| `metadata` | `NyayaResponse` | Not in contract | LOW — added by builder |
| `answer_source` | `NyayaResponse` | Not in contract | MEDIUM — affects trust model |
| `answer_model` | `NyayaResponse` | Not in contract | MEDIUM — affects trust model |

---

## Schema Audit Verdict

| Dimension | Status |
|-----------|--------|
| Internal schema consistency (schemas.py ↔ Observer ↔ Builder) | ✅ PASS |
| All 11 TANTRA canonical fields present and validated | ✅ PASS |
| DeterminismProof hex64 validation active | ✅ PASS |
| Frontend validator alignment | ✅ PASS |
| Frontend UI alignment | ❌ FAIL — components still use `enforcement_decision` |
| Contract alignment (final_decision_contract.json) | ❌ FAIL — CRITICAL DRIFT |
| Schema versioning | ⚠️ PARTIAL — only in metadata stamp, not in model |
| Undocumented fields | ⚠️ 6 fields not in contract |

