# NYAI — RISK REGISTER
**Audit Sprint:** NYAI Independent Forensic Audit
**Date:** 09 June 2026

---

## TOP 10 CRITICAL RISKS

| ID | Risk | Severity | Likelihood | Impact | Evidence |
|----|------|----------|-----------|--------|----------|
| RISK-001 | `final_decision_contract.json` requires `enforcement_decision` field that no longer exists in NyayaResponse — all downstream TANTRA consumers validating against this contract will reject NYAI output | CRITICAL | CERTAIN | All TANTRA integrations fail silently or with explicit rejection | `final_decision_contract.json` line 11: `"required": [...,"enforcement_decision",...]`; `schemas.py`: no `enforcement_decision` field |
| RISK-002 | TANTRA sovereign core push never happens — NYAI stores outputs locally but never forwards to any downstream TANTRA node | CRITICAL | CERTAIN | TANTRA chain is broken after NYAI; no downstream system receives NYAI output | `router.py` has no `sovereign_core.receive()` call; `tantra/flow.py` is standalone script |
| RISK-003 | `GET /nyaya/trace/{trace_id}` is a hardcoded stub — TANTRA observability chain requires real event replay | HIGH | CERTAIN | TANTRA auditors cannot replay or verify any NYAI execution | `router.py` lines 771–783: hardcoded empty return |
| RISK-004 | HTTP middleware generates `trace_id` that is never used — middleware trace and handler trace differ on every request | HIGH | CERTAIN | HTTP-layer trace correlation impossible; middleware trace and response trace always differ | `main.py:71-72`: `request.state.trace_id`; `router.py:118`: `_temp_trace` — no cross-reference |
| RISK-005 | CORS falls back to `["*"]` when `FRONTEND_URL` env var unset — production deployment is open to all origins | HIGH | LIKELY in misconfiguration | Unauthorized consumers can query NYAI without governance oversight | `main.py:47`: `allowed_origins or ["*"]` |
| RISK-006 | CI pipeline silently passes with zero tests — `pytest \|\| echo "No tests found"` never fails | HIGH | CERTAIN | Code regressions in schema, observer, or trace logic will not be caught before deployment | `.github/workflows/ci.yml` |
| RISK-007 | `hash_chain_ledger.py` is not called from query handler — provenance chain in responses is a single-entry inline dict, not a real hash chain | HIGH | CERTAIN | Hash-chain integrity claims in documentation are false; chain audit is not possible | `router.py`: no import of `hash_chain_ledger`; provenance_chain built inline |
| RISK-008 | Frontend UI components still expect `enforcement_decision` but API returns `recommendation` — enforcement badges and decision UI will not render | MEDIUM | CERTAIN | Users see broken/missing enforcement state UI | `LegalQueryCard.jsx`, `LegalDecisionDocument.jsx`, `nyayaBackendApi.js:48` |
| RISK-009 | Render Free tier (512MB RAM) is insufficient for `torch==2.1.2 + faiss-cpu + sentence-transformers` ML stack — service will OOM on startup | MEDIUM | CERTAIN on Free tier | Service fails to start; all endpoints return 503 | `requirements.txt`: `torch==2.1.2`, `faiss-cpu`, `sentence-transformers` |
| RISK-010 | `MultiJurisdictionResponse.comparative_analysis` returns empty dict stub — the `/multi_jurisdiction` endpoint is non-functional | MEDIUM | CERTAIN | Any TANTRA consumer or frontend expecting multi-jurisdiction comparison receives empty data | `router.py:743-750` |

---

## FULL RISK REGISTER

### CRITICAL RISKS

**RISK-001 — Contract Drift (enforcement_decision)**
- **Category:** Schema / Interoperability
- **Description:** `final_decision_contract.json` version 1.0.0 declares `enforcement_decision` (ALLOW/ALLOW_INFORMATIONAL/SAFE_REDIRECT/RESTRICT) as required in the response. Current `NyayaResponse` has no such field. `recommendation: Recommendation` with `RecommendationType.{INFORM,REVIEW,ESCALATE,INSUFFICIENT_DATA}` is the replacement.
- **Affected systems:** All TANTRA downstream consumers, Raj integration, any system using the contract as a validation spec
- **Mitigation:** Publish `final_decision_contract.json` v2.0.0 removing `enforcement_decision`, adding `recommendation` schema

**RISK-002 — Sovereign Core Disconnected**
- **Category:** Integration / TANTRA Convergence
- **Description:** NYAI correctly computes and validates all TANTRA canonical fields, then stores them locally. No code path pushes NYAI output to the sovereign core during live API operation.
- **Affected systems:** TANTRA chain post-NYAI
- **Mitigation:** Add `sovereign_core.receive(enriched, expected_trace_id=trace_id)` call after `output_bucket.store()` in query handler; replace mock with real sovereign core for production

---

### HIGH RISKS

**RISK-003 — Trace Endpoint Stub**
- **Category:** Observability / Replay
- **Description:** `GET /nyaya/trace/{trace_id}` returns `event_chain=[]`, `context_fingerprint="mock_fingerprint"`, `nonce_verification=True` regardless of input. Real trace data exists in `output_bucket` but is not served.
- **Evidence:** `router.py:771-783`
- **Mitigation:** Implement endpoint to call `output_bucket.retrieve(trace_id)` and return real data

**RISK-004 — Middleware trace orphan**
- **Category:** Trace Continuity
- **Description:** HTTP middleware trace (`main.py:71-72`, UUID) and handler's `_temp_trace` (`router.py:118`, timestamp+hex6) differ on every request. `advice.trace_id` reuses `_temp_trace` (`clean_legal_advisor.py:1995`). HTTP-layer correlation is impossible.
- **Mitigation:** In query handler, read `request.state.trace_id` and use as `_temp_trace` instead of generating a new one. This collapses middleware and handler traces to one.

**RISK-005 — CORS Open Default**
- **Category:** Security
- **Description:** `allowed_origins or ["*"]` — if production deployment doesn't set `FRONTEND_URL`, all origins accepted
- **Mitigation:** Require `FRONTEND_URL` in deployment; remove wildcard fallback for production profiles

**RISK-006 — Zero Test CI**
- **Category:** Quality / Governance
- **Description:** CI passes with no tests. `pytest || echo "No tests found"` exit code is always 0.
- **Mitigation:** Add at least 3 integration tests: (1) schema validation passes for valid query, (2) observer blocks invalid schema, (3) trace_id appears in OutputBucket

**RISK-007 — Hash Chain Never Written**
- **Category:** Provenance / Truth
- **Description:** `hash_chain_ledger.py` is a full implementation of a hash-chained audit ledger but is never imported or called. Documentation implies it is active.
- **Mitigation:** Import `HashChainLedger` in router; call `ledger.append_entry(trace_id, input_hash, output_hash)` in query handler

**RISK-008 — Frontend UI Schema Drift**
- **Category:** Schema / Frontend
- **Description:** Backend `NyayaResponse` returns `recommendation.type` (INFORM/REVIEW/ESCALATE/INSUFFICIENT_DATA). Frontend UI components and tests still expect `enforcement_decision` (ALLOW/BLOCK/ESCALATE/SAFE_REDIRECT).
- **Evidence:** `casePayloadValidator.js` aligned; `LegalQueryCard.jsx`, `LegalDecisionDocument.jsx`, `nyayaBackendApi.js:48` still check `enforcement_decision`
- **Mitigation:** Migrate UI to read `recommendation.type`; update frontend tests

**RISK-021 — DETERMINISM_GUARD_ENABLED Dead Code**
- **Category:** Technical Debt
- **Description:** `DETERMINISM_GUARD_ENABLED` is defined at `router.py:48` but never referenced elsewhere. Determinism is enforced by Observer + ResponseBuilder + `schemas.py:129-133` regardless of this flag.
- **Severity:** LOW
- **Mitigation:** Remove dead flag or wire it to an actual guard

---

### MEDIUM RISKS

**RISK-009 — RAM OOM on Render Free**
- **Category:** Deployment / Infrastructure
- **Description:** ML stack requires ~1.5–2.5 GB RAM minimum. Render Free = 512 MB.
- **Mitigation:** Require Render Starter (2 GB) minimum; document in deployment guide

**RISK-010 — Multi-jurisdiction stub**
- **Category:** Feature Completeness
- **Description:** `POST /nyaya/multi_jurisdiction` returns `comparative_analysis={}`. Non-functional.
- **Mitigation:** Either implement or mark as `POST /nyaya/multi_jurisdiction [DEPRECATED — not implemented]`

**RISK-011 — answer field lacks constitutional guardrail**
- **Category:** Governance
- **Description:** Groq-generated free-text in `answer` field has no disclaimer, no confidence bound, and no constitutional constraint in the schema. Downstream consumers may display as authoritative.
- **Mitigation:** Add `answer_disclaimer` field to NyayaResponse; add to TANTRA contract v2.0.0

**RISK-012 — raj_adapter disconnected**
- **Category:** Integration Completeness
- **Description:** `RajReasoningIntegrator` with real schema files exists but is not called from any active endpoint. Raj's failure path analysis, evidence readiness, and compliance checks are never applied.
- **Mitigation:** Wire `RajReasoningIntegrator.analyze_context()` into the query handler as post-processing (advisory enrichment)

**RISK-013 — governed_execution always approves**
- **Category:** Governance
- **Description:** `GovernedExecutionPipeline.execute_with_governance()` always sets `governance_approved: True`. No condition causes rejection.
- **Mitigation:** If reconnected, implement actual governance checks before setting approval flag

---

### LOW RISKS

**RISK-014 — sovereign_agents disconnected**
- **Category:** Integration Completeness
- **Mitigation:** Requires constitutional review before reconnection — `jurisdiction_router_agent.py` may attempt routing decisions

**RISK-015 — request_id collision on identical queries**
- **Category:** Tracing Correctness
- **Description:** `request_id = f"req_{input_hash[:12]}"` — same query always gets same request_id
- **Mitigation:** Include trace_id in request_id derivation for uniqueness

**RISK-016 — OutputBucket not HTTP-accessible**
- **Category:** Observability
- **Mitigation:** Add `GET /nyaya/output/{trace_id}` endpoint

**RISK-017 — explain_reasoning and feedback are stubs**
- **Category:** Feature Completeness
- **Mitigation:** Implement or remove from documented API surface

**RISK-018 — SovereignCoreMock uses in-memory receipt list**
- **Category:** Production Readiness
- **Mitigation:** Replace with persistent store when moving to real sovereign core

**RISK-019 — No schema version field in NyayaResponse model**
- **Category:** Schema Versioning
- **Mitigation:** Add `schema_version: str = "tantra_v3"` as a declared field in NyayaResponse

**RISK-020 — TRACE_PROOF_EXAMPLES.md documents deleted architecture**
- **Category:** Documentation Drift
- **Mitigation:** Replace with examples showing recommendation + hash proof pattern

