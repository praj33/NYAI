# NYAI — AUDIT REPORT
**Auditor:** Independent Forensic Sprint (Shashank)
**Date:** 09 Jun 2026
**Codebase Commit Context:** Jun 3 2026 — main branch
**Document Status:** FINAL

---

## EXECUTIVE SUMMARY

NYAI is a multi-jurisdiction legal AI that has undergone a **major architectural transition**: its enforcement engine has been deleted and replaced with an advisory-only recommendation system. The codebase is **partially converged** with TANTRA. Core query processing is functional and schema-compliant. However, critical gaps remain between the canonical contract (`final_decision_contract.json`), the TANTRA module integration state, and the live API.

**Final Readiness Classification: INTEGRATION READY (NOT PRODUCTION READY)**

---

## PHASE 1 — ARCHITECTURE AUDIT

### Real Entry Point
- **File:** `backend/api/main.py`
- **Framework:** FastAPI 0.104+, uvicorn
- **Routers included:** `api.router` (12 routes, `/nyaya` prefix), `api.procedure_router` (7 routes, try/except import), debug/enhanced endpoints via optional try/except imports
- **Middleware:** HTTP trace_id middleware (generates `str(uuid.uuid4())` per request, stores in `request.state.trace_id`), CORSMiddleware
- **Global exception handler:** Present — returns `{"error_code": "INTERNAL_ERROR", "message": "TANTRA FAIL CLOSED: ...", "trace_id": ...}`
- **CORS config:** `allowed_origins or ["*"]` — if `FRONTEND_URL` env var is unset, falls back to wildcard `*`

### Real Execution Path (POST /nyaya/query)
```
HTTP Request
  → add_trace_id_middleware (generates middleware_trace_id — ORPHANED)
  → query_legal() handler
      → clean_query()
      → _temp_trace = f"trace_{timestamp}_{uuid4().hex[:6]}"   ← HANDLER'S OWN trace_id
      → ObserverPipeline(trace_id=_temp_trace)
      → analyze_query()
      → expand_query()
      → get_hybrid_retriever().hybrid_search()   ← ThreadPoolExecutor, 12s timeout
      → rerank_sections()                         ← ThreadPoolExecutor, 8s timeout
      → apply_reasoning_rules()
      → JurisdictionDetector.detect()
      → LegalQuery(trace_id=_temp_trace)          ← _temp_trace PASSED to advisor
      → EnhancedLegalAdvisor.provide_legal_advice()
          → returns advice.trace_id == _temp_trace (advisor reuses it)
      → CaseLawRetriever.retrieve()
      → build base_response["trace_id"] = advice.trace_id  ← same as _temp_trace
      → enrich_response()
      → compute input_hash, output_hash (SHA256)
      → build LegalContext, Facts, AnalysisBlock, Recommendation, ExplanationChain
      → ObserverPipeline.validate_response(enriched)   ← FAIL CLOSED
          → checks all 11 canonical fields
          → checks recommendation.type ∈ {INFORM,REVIEW,ESCALATE,INSUFFICIENT_DATA}
          → checks hash formats (64-char hex)
          → checks trace_id == self.trace_id (_temp_trace)
      → ResponseBuilder.build(enriched)           ← FAIL CLOSED, same 11 fields + structural
      → trace_guard: final_trace == _temp_trace OR advice.trace_id  ← lenient OR
      → output_bucket.store(enriched)             ← disk-persisted JSONL
      → response_cache.set(trace_id, enriched)    ← in-memory LRU (500 cap)
      → return NyayaResponse(**enriched)
```

### Module Existence Map (Verified)

| Module | Path | Exists | Called from Router |
|--------|------|--------|--------------------|
| EnhancedLegalAdvisor | `backend/clean_legal_advisor.py` | ✅ Yes | ✅ Yes |
| ObserverPipeline | `backend/observer/pipeline.py` | ✅ Yes | ✅ Yes |
| ResponseBuilder | `backend/api/response_builder.py` | ✅ Yes | ✅ Yes |
| OutputBucket | `backend/tantra/output_bucket.py` | ✅ Yes | ✅ Yes (imported, called) |
| TANTRA flow.py | `backend/tantra/flow.py` | ✅ Yes | ❌ Standalone script only |
| SovereignCoreMock | `backend/tantra/sovereign_core_mock.py` | ✅ Yes | ❌ Not imported by router |
| GovernedExecutionPipeline | `backend/governed_execution/pipeline.py` | ✅ Yes | ❌ Not imported by router |
| RajReasoningIntegrator | `backend/raj_adapter/enforcement_integration.py` | ✅ Yes | ❌ Not imported by router |
| RewardEngine | `backend/rl_engine/reward_engine.py` | ✅ Yes | ✅ Yes (lazy import in /rl_signal) |
| SovereignAgents (base/legal/constitutional) | `backend/sovereign_agents/` | ✅ Yes | ❌ Not imported anywhere |
| enforcement_engine/ | N/A | ❌ ABSENT | N/A |

### Actual vs Claimed Architecture Delta

| Claim | Reality |
|-------|---------|
| 25 total endpoints | 12 (nyaya router) + 7 (procedure router) + 2 (root/health) = **21 confirmed** |
| enforcement_engine with 9 rules | **ABSENT** — directory does not exist |
| HMAC signing of enforcement decisions | **ABSENT** — no HMAC found in router |
| SovereignAgents integrated | **Present but disconnected** — never imported in router |
| GovernedExecutionPipeline in query path | **Not in query path** — module exists, not wired |
| RajReasoningIntegrator integrated | **Exists, not imported** by any active endpoint |
| Sovereign Core integration | **MOCK ONLY** — not called from live API |

---

## PHASE 2 — CONTRACT & SCHEMA AUDIT

### The Central Schema Split — CONFIRMED CRITICAL

**`final_decision_contract.json` (versioned 1.0.0):**
```json
"required": ["domain", "jurisdiction", "confidence", "statutes", "enforcement_decision", "trace_id"]
"enforcement_decision": { "enum": ["ALLOW", "ALLOW_INFORMATIONAL", "SAFE_REDIRECT", "RESTRICT"] }
```

**`backend/api/schemas.py` — `NyayaResponse` (current truth):**
- Field `enforcement_decision` → **DOES NOT EXIST**
- Field `recommendation: Recommendation` → **EXISTS**, type = `RecommendationType.{INFORM,REVIEW,ESCALATE,INSUFFICIENT_DATA}`
- **No HMAC field, no enforcement signature field**

**Verdict:** `final_decision_contract.json` is **stale**. It describes an architecture that no longer exists. Every system that validates against this contract (downstream consumers, Raj's adapter, TANTRA gateways) will reject or misread NYAI output.

### ResponseBuilder REQUIRED_FIELDS (Verified Against Code)
The `REVIEW_PACKET.md` claim that `REQUIRED_FIELDS` contained `enforcement_decision` is **FALSE**. Actual `response_builder.py`:
```python
CANONICAL_FIELDS = ["trace_id","request_id","input_hash","legal_context","facts",
                    "analysis","recommendation","explanation_chain","risk_flags",
                    "determinism_proof","timestamp"]
STRUCTURAL_FIELDS = ["domain","jurisdiction","confidence","legal_route"]
VALID_RECOMMENDATION_TYPES = {"INFORM","REVIEW","ESCALATE","INSUFFICIENT_DATA"}
```
`enforcement_decision` does not appear. The builder correctly aligns with current `schemas.py`.

### All 11 TANTRA Canonical Fields — Verified Present in NyayaResponse

| Field | In schemas.py | Set in router.py | Notes |
|-------|--------------|-----------------|-------|
| trace_id | ✅ Required | ✅ `advice.trace_id` | Same as `_temp_trace` |
| request_id | ✅ Required | ✅ `f"req_{input_hash[:12]}"` | Deterministic from input |
| input_hash | ✅ Required | ✅ SHA256 of canonical input | 64-char hex |
| legal_context | ✅ Required | ✅ `LegalContext(...)` | |
| facts | ✅ Required | ✅ 5 structured `Fact` objects | |
| analysis | ✅ Required | ✅ `AnalysisBlock(...)` | |
| recommendation | ✅ Required | ✅ `Recommendation(type=rec_type,...)` | Advisory only |
| explanation_chain | ✅ Required | ✅ 8 `ExplanationStep` objects | |
| risk_flags | ✅ Default `[]` | ✅ Populated conditionally | |
| determinism_proof | ✅ Required | ✅ `DeterminismProof(input_hash, output_hash, version)` | Both hex64 validated |
| timestamp | ✅ Required | ✅ `datetime.utcnow().isoformat() + "Z"` | |

**All 11 fields verified present and populated correctly.**

### DeterminismProof Validator — Verified
`schemas.py` line ~110: `@validator('input_hash','output_hash') def must_be_hex64` — confirmed present and active. Both router.py and response_builder.py independently validate hex64 format.

### Frontend Schema (vercel.json) — CORRECTED (Previously Flagged)
`frontend/vercel.json` uses `"VITE_API_URL"` — correct for a Vite project. **CF-006 from pre-loaded flags is FALSE**. This was a pre-audit false positive.

### `casePayloadValidator.js` — No enforcement_decision reference
Zero occurrences of `enforcement_decision`, `ALLOW`, `BLOCK`, or `RESTRICT` in the frontend validator. Frontend is already aligned to the new schema.

---

## PHASE 3 — TRACE & REPLAY AUDIT

### trace_id Count — THREE IDs IN PLAY

| ID | Generated At | Value | Used Where |
|----|-------------|-------|-----------|
| `middleware_trace_id` | `main.py` middleware | `str(uuid.uuid4())` | `request.state.trace_id` — **NEVER READ by router** |
| `_temp_trace` | `router.py` line 118 | `f"trace_{timestamp}_{uuid4().hex[:6]}"` | ObserverPipeline, LegalQuery |
| `advice.trace_id` | `clean_legal_advisor.py` line 1995 | `legal_query.trace_id` (reuses `_temp_trace`) | `base_response["trace_id"]` |

**Result:** `_temp_trace` == `advice.trace_id` (advisor reuses the passed value). `middleware_trace_id` is **completely orphaned** — generated, stored in `request.state`, never read again, never appears in any response.

**Trace continuity WITHIN the query handler is maintained** (`_temp_trace` flows through consistently). **Trace continuity at the HTTP layer is broken** — the middleware and the response carry different IDs.

### trace_guard Analysis
```python
if final_trace != _temp_trace and final_trace != advice.trace_id:
    raise TraceContinuityError(...)
```
This guard uses `OR` logic — it passes if `final_trace` matches EITHER `_temp_trace` OR `advice.trace_id`. Since both are the same value, the guard is effectively checking `final_trace == _temp_trace`. **The guard is correctly preventing trace mutation during the pipeline**, but it is not guarding against the middleware orphan.

### Replay Capability

**GET /nyaya/trace/{trace_id}:**
```python
return TraceResponse(trace_id=trace_id, event_chain=[], agent_routing_tree={},
                     jurisdiction_hops=[], rl_reward_snapshot={},
                     context_fingerprint="mock_fingerprint", ...)
```
**This endpoint is a STUB.** It returns hardcoded empty data. It does NOT query `response_cache` or `output_bucket`. Full replay from this endpoint: **NOT POSSIBLE**.

**GET /nyaya/case_summary?trace_id=...:**
This endpoint DOES query `response_cache.get(trace_id)` and returns real data — statutes, recommendation, confidence. Partial replay via case_summary is possible **within the same process lifetime**.

**OutputBucket (disk-persisted JSONL):**
- Writes to `backend/output_logs/nyai_output_log.jsonl`
- Persists across restarts
- Has `retrieve(trace_id)` and `verify(trace_id)` methods
- **Not exposed via any API endpoint** — only accessible internally

**Provenance chain:** `hash_chain_ledger.py` exists in `backend/provenance_chain/` but is **not imported or called** anywhere in `router.py`. The `provenance_chain` field in `NyayaResponse` is built inline in the router from `observer.get_provenance_entry()` — it is a single-entry dict, not the hash-chained ledger.

---

## PHASE 4 — OBSERVER AUDIT

### Classification: PURE WITNESS (with one trace flexibility caveat)

**Evidence:**

1. **Never modifies data:** Zero occurrences of `[field] =` or `.update()` in `observer/pipeline.py`. The `record()` method only appends to `self._steps`. The `validate_response()` method only reads and validates.

2. **Is blocking:** When `observer_result.passed == False`, router raises `SchemaValidationError` → HTTP 500. No bypass path exists.

3. **Double-gate with ResponseBuilder:** Observer validates first (`validate_response()`), then `ResponseBuilder.build()` validates again. Both use identical 11-field canonical list and same `VALID_RECOMMENDATION_TYPES`. If observer passes, builder will almost certainly pass (same logic). However, builder adds the `metadata` stamp — the only field-additive action in the pipeline.

4. **Trace continuity check:** Observer checks `response_trace == self.trace_id`. This will **always pass** because `self.trace_id = _temp_trace` and `base_response["trace_id"] = advice.trace_id = _temp_trace`.

5. **No authority:** Observer cannot make routing decisions, modify recommendations, or alter any field.

**One nuance:** The observer is instantiated with `_temp_trace` but the trace guard in the router uses `OR` logic (`_temp_trace OR advice.trace_id`). This is slightly more lenient than strict identity. Not a violation of observer purity, but worth noting as a future tightening point.

---

## PHASE 5 — CONSTITUTIONAL AUDIT

### Authority Matrix Summary

**A. What NYAI OWNS:**
- Legal information retrieval (BM25 + FAISS + cross-encoder reranking)
- Structured response generation conforming to TANTRA canonical schema
- Trace lifecycle management within a single HTTP request
- Output logging to disk (OutputBucket)
- Advisory recommendation classification (INFORM/REVIEW/ESCALATE/INSUFFICIENT_DATA)
- Schema validation gating (fail-closed via Observer + ResponseBuilder)

**B. What NYAI DOES NOT OWN:**
- Legal decisions (no enforcement_decision field exists)
- Blocking user access (NYAI can return HTTP 500 on schema violations, not on legal content)
- Jurisdiction authority (detection only, advisory)
- Enforcement (module deleted — governed_execution is advisory-only per its own docstring)
- RL model updates (reward is computed but not written back to any persistent model)

**C. Authority Ceiling:**
Advisory only. `RecommendationType` is explicitly documented as "NOT a decision gate." The recommendation affects display only.

**D. Governance Risks:**
- RL `RewardEngine` computes rewards (+0.05/-0.08 base deltas, capped at ±0.15 per update, ±0.03 per delta) but the computed `reward` value is **returned to the caller** — it is not applied to any persistent confidence store. **No authority drift from RL** in the current implementation.
- `answer` field: free-text Groq LLM output. If a frontend displays this as authoritative guidance, it could de facto function as a legal decision even though structurally it is advisory. This is a **presentation-layer governance risk**, not a code-level authority.

**E. Hidden Authority Risks:**
- The Groq LLM answer field has no constitutional guardrail or disclaimer in the schema. Downstream consumers could misuse it.
- `CORS: allowed_origins or ["*"]` — if `FRONTEND_URL` is unset in production, ALL origins can query NYAI. An unauthorized consumer could request legal information without governance oversight.

**F. Drift Risks:**
- RL rewards are stateless per-request — no cumulative drift is possible in current code. A future persistent reward store would reintroduce this risk.
- Schema drift between `final_decision_contract.json` (stale v1.0.0) and live `schemas.py` (tantra_v3) is already present and will cause downstream integration failures.

**CAN NYAI ACCIDENTALLY BECOME AUTHORITY? → NO (in current code)**
The enforcement engine is deleted. The recommendation field is advisory-only by both schema definition and explicit docstring. The RL reward is not applied to any persistent store. However, **presentation-layer authority** (Groq answer displayed as decision) is a real risk outside NYAI's code boundary.

---

## PHASE 6 — TANTRA CONVERGENCE AUDIT

### TANTRA Stage Mapping

| Stage | NYAI Module | Status | Notes |
|-------|-------------|--------|-------|
| Signal | `POST /nyaya/query` | ✅ LIVE | Fully active |
| Intelligence | EnhancedLegalAdvisor + Groq + BM25 + FAISS | ✅ LIVE | Groq optional, local fallback exists |
| Decision | `Recommendation` (advisory) | ✅ LIVE (advisory) | Not a gate; `enforcement_decision` deleted |
| Contract | `NyayaResponse` Pydantic schema | ✅ LIVE | 11 canonical fields, fail-closed validation |
| Enforcement | ~~enforcement_engine~~ → deleted | ❌ ABSENT | `governed_execution` is advisory-only |
| Execution | ResponseBuilder + OutputBucket | ✅ PARTIAL | OutputBucket is disk-persistent; no external push |
| Truth | DeterminismProof + SHA256 hashes | ✅ LIVE | Both hashes verified; provenance ledger disconnected |
| Observability | ObserverPipeline + output_logs/ | ✅ PARTIAL | Observer active; trace endpoint is stub; no dashboard |

### TANTRA Module Integration State

| Module | Integration State | Evidence |
|--------|------------------|----------|
| `tantra/output_bucket.py` | ✅ **LIVE** — called in query handler | `output_bucket.store(enriched)` — router line 644 |
| `tantra/flow.py` | ❌ **STANDALONE SCRIPT** — `if __name__ == "__main__":` | Not imported by any API endpoint |
| `tantra/sovereign_core_mock.py` | ❌ **NOT WIRED** to live API | Only used by `flow.py` (standalone script) |
| `governed_execution/pipeline.py` | ❌ **DISCONNECTED** | Not imported by router |
| `raj_adapter/` | ❌ **DISCONNECTED** | Not imported by router |
| `sovereign_agents/` | ❌ **DISCONNECTED** | Not imported anywhere active |

### Broken Links Before TANTRA Convergence

1. **Sovereign Core push is missing** — NYAI stores outputs locally but never forwards to a real TANTRA sovereign core. `sovereign_core_mock.py` validates correctly but is never called from the live API.
2. **`tantra/flow.py` is the integration runner but is a standalone script** — there is no HTTP endpoint or scheduler that invokes the TANTRA flow programmatically.
3. **`final_decision_contract.json` must be updated** — downstream TANTRA consumers validating against this contract will reject NYAI output (missing `enforcement_decision`, unexpected `recommendation` field).
4. **`GET /nyaya/trace/{trace_id}` returns stub data** — TANTRA observability requires real event chain replay; this is currently hardcoded empty.
5. **No API endpoint exposes `output_bucket.retrieve()`** — TANTRA auditors cannot query the output log via the API.

---

## PHASE 7 — PRODUCTION READINESS AUDIT

### Fail-Closed Behavior
- Global exception handler: ✅ present — returns structured JSON with trace_id
- SchemaValidationError → HTTP 500: ✅ confirmed
- TraceContinuityError → HTTP 500: ✅ confirmed
- HashMismatchError → HTTP 500: ✅ confirmed
- CORS: ⚠️ Falls back to `["*"]` if `FRONTEND_URL` unset — open in production if misconfigured

### Groq Dependency Failure
- `GROQ_ENABLED` env flag: checked in `services/explainer.py`
- If Groq unavailable: falls back to `local_fallback` answer generation
- Hybrid retriever and reranker: wrapped in `ThreadPoolExecutor` with 12s/8s timeouts — graceful degradation to top-5 candidates on timeout

### ML Stack Cold Start
- `requirements.txt` includes: `torch==2.1.2`, `faiss-cpu`, `sentence-transformers`
- Combined install: ~2–3 GB; cold start on Render Free (512MB RAM): **will OOM**
- Render Starter (2GB RAM): minimum viable; Render Standard recommended
- No lazy loading — models load at startup

### Security
- `GROQ_API_KEY`: accessed via `os.getenv("GROQ_API_KEY")` — not hardcoded in any committed file
- `HMAC_SECRET_KEY`: referenced in `final_decision_contract.json` `enforcement_rules` but **no HMAC signing code exists in the current codebase** — the enforcement rules listing HMAC are stale documentation from the deleted enforcement engine
- `.env.example` present; actual `.env` not committed

### CI/CD
- GitHub Actions workflow: `pip install -r requirements.txt` → `python -c "import api.main"` → `pytest || echo "No tests found"`
- **CI does not fail if there are no tests.** `pytest || echo "No tests found"` silently passes with zero test coverage.
- No TANTRA integration tests in CI

### Deployment Config
- `vercel.json` uses `VITE_API_URL` pointing to `https://nyaya-ai-0f02.onrender.com` — correct
- `backend/.env.example` present for backend secrets
- Render deployment: requires Starter plan minimum for ML stack RAM

---

## TOP 20 FINDINGS

| # | Finding | Severity | Phase |
|---|---------|----------|-------|
| F-001 | `final_decision_contract.json` still requires `enforcement_decision` (ALLOW/RESTRICT enum) — field deleted from live schema | CRITICAL | 2 |
| F-002 | `tantra/flow.py` is a standalone script, not wired to any API endpoint — TANTRA flow not executable via the API | CRITICAL | 6 |
| F-003 | `SovereignCoreMock` never called from live API — TANTRA sovereign core push is completely disconnected | CRITICAL | 6 |
| F-004 | `GET /nyaya/trace/{trace_id}` returns hardcoded stub data — real event chain replay is impossible | HIGH | 3 |
| F-005 | `middleware_trace_id` (from `main.py` HTTP middleware) is orphaned — never read by the query handler; 3 distinct trace IDs circulate | HIGH | 3 |
| F-006 | `enforcement_engine/` directory does not exist — architectural documentation (ARCHITECTURE.md, system_map.md) describes a ghost module | HIGH | 1 |
| F-007 | `sovereign_agents/`, `governed_execution/`, `raj_adapter/` all exist but are not imported by any active endpoint — documented as integrated but disconnected | HIGH | 1 |
| F-008 | `hash_chain_ledger.py` (`provenance_chain/`) is not imported or called from `router.py` — provenance_chain field in response is built inline, not from the ledger | HIGH | 3 |
| F-009 | CORS fallback to `["*"]` when `FRONTEND_URL` env var is unset — production deployment is open to all origins by default | HIGH | 7 |
| F-010 | `TRACE_PROOF_EXAMPLES.md` documents `decision: ALLOW/BLOCK` and HMAC signatures — these structures no longer exist in the codebase | HIGH | 2 |
| F-011 | CI pipeline: `pytest || echo "No tests found"` — zero tests pass CI silently; no TANTRA integration tests | MEDIUM | 7 |
| F-012 | `OutputBucket.retrieve()` has no HTTP endpoint — TANTRA auditors cannot query the disk log via the API | MEDIUM | 6 |
| F-013 | `DETERMINISM_GUARD_ENABLED` env flag defaults to `false` — determinism guard is off by default in production | MEDIUM | 3 |
| F-014 | RL `RewardEngine.compute_reward()` returns a reward value but does not write it to any persistent store — RL loop is compute-only, no actual learning | MEDIUM | 5 |
| F-015 | `MultiJurisdictionResponse.comparative_analysis: Dict[str, NyayaResponse]` — the `/multi_jurisdiction` endpoint returns an empty dict stub | MEDIUM | 7 |
| F-016 | Raj schemas (`failure_paths_v2.json`, `evidence_readiness_v2.json`, `system_compliance_v2.json`) exist on disk but `RajReasoningIntegrator` is not imported by any active endpoint | MEDIUM | 1 |
| F-017 | `request_id` is deterministic from `input_hash[:12]` — same query always yields same `request_id`; two requests with identical inputs are indistinguishable by `request_id` alone | LOW | 2 |
| F-018 | `output_bucket` singleton is initialized at module import — if `backend/output_logs/` directory creation fails at startup, the entire import chain fails silently | LOW | 7 |
| F-019 | `GovernedExecutionPipeline` always sets `governance_approved: True` — it never rejects anything; its authority boundary is purely advisory with no actual gating | LOW | 5 |
| F-020 | `explain_reasoning` and `feedback` endpoints return hardcoded stub responses — no real functionality | LOW | 7 |

---

## FINAL READINESS CLASSIFICATION

**INTEGRATION READY**

**Justification:**
- Core query logic is functional and schema-compliant (11 canonical TANTRA fields, fail-closed validation, disk-persisted output)
- The TANTRA output_bucket is live and wired
- Observer and ResponseBuilder are both active as strict validation gates
- Schema is internally consistent (NyayaResponse ↔ Observer ↔ ResponseBuilder all agree)
- The enforcement layer was deliberately deleted and advisory-only recommendation correctly implemented

**Cannot be classified PRODUCTION READY because:**
1. `final_decision_contract.json` is stale — downstream consumers will fail
2. TANTRA sovereign core push is disconnected
3. Trace endpoint is a stub — no replay capability
4. No test coverage in CI
5. Three endpoints (`multi_jurisdiction`, `explain_reasoning`, `feedback`) are stubs
6. CORS open-by-default risk
7. RAM requirements exceed Render Free tier

