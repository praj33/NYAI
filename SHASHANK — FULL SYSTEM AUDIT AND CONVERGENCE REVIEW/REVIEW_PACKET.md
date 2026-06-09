# NYAI — REVIEW PACKET
**Audit Sprint:** NYAI Independent Forensic Audit
**Date:** 09 June 2026
**Prepared for:** TANTRA Convergence Review Board
**Classification:** INTEGRATION READY — Not Production Ready

---

## SECTION 1 — ENTRY POINT

**Primary entry point:** `backend/api/main.py`
**Server:** uvicorn, port from `PORT` env (default 8000), host from `HOST` env (default 0.0.0.0)
**Application:** FastAPI, title "Nyaya Legal AI API Gateway", version 1.0.0
**Startup sequence:**
1. Load `.env` via `python-dotenv`
2. Create FastAPI app
3. Apply CORS middleware (localhost:3000/5173 + FRONTEND_URL env)
4. Register global exception handler
5. Register HTTP trace_id middleware
6. Include `api.router` (12 routes, `/nyaya` prefix)
7. Include `api.procedure_router` (7 routes, try/except — optional)
8. Register `/health` and `/` endpoints
9. At import: `EnhancedLegalAdvisor()`, `JurisdictionDetector()`, `CaseLawLoader()` instantiated
10. At import: `output_bucket = OutputBucket()` singleton created — rebuilds JSONL index from disk

---

## SECTION 2 — REAL EXECUTION FLOW

**Endpoint:** `POST /nyaya/query`

| Step | Code Location | Action | Fail Mode |
|------|-------------|--------|-----------|
| 1 | `router.py:115` | `clean_query(request.query)` | Returns original on failure |
| 2 | `router.py:118` | Generate `_temp_trace` (does not read `request.state.trace_id` from `main.py:72`) | Never fails |
| 3 | `router.py:119` | `ObserverPipeline(_temp_trace)` | Never fails |
| 4 | `router.py:122` | `analyze_query(cleaned_query)` | Falls back to domain="civil" |
| 5 | `router.py:130` | `expand_query()` | Falls back to original query |
| 6 | `router.py:141` | `hybrid_retriever.hybrid_search()` in ThreadPoolExecutor (12s) | Timeout → empty candidates |
| 7 | `router.py:159` | `rerank_sections()` in ThreadPoolExecutor (8s) | Timeout → top-5 unranked |
| 8 | `router.py:173` | `apply_reasoning_rules()` | Returns unmodified sections |
| 9 | `router.py:227` | `advisor.provide_legal_advice(LegalQuery(trace_id=_temp_trace))` | Raises → HTTP 500 |
| 10 | `router.py:336` | `case_retriever.retrieve()` | Returns empty list on failure |
| 11 | `router.py:466` | Compute `input_hash` (SHA256) | Never fails |
| 12 | `router.py:482-546` | Build Facts, Analysis, Recommendation, ExplanationChain | Never fails |
| 13 | `router.py:567` | Compute `output_hash` (SHA256) | Never fails |
| 14 | `router.py:569-573` | `DeterminismProof(input_hash, output_hash, "3.0.0")` | Raises if not hex64 → HTTP 500 |
| 15 | `router.py:623` | `observer.validate_response(enriched)` | Raises SchemaValidationError → HTTP 500 |
| 16 | `router.py:632-633` | `ResponseBuilder().build(enriched)` | Raises SchemaValidationError → HTTP 500 |
| 17 | `router.py:636-638` | trace_guard check | Raises TraceContinuityError → HTTP 500 |
| 18 | `router.py:642` | `output_bucket.store(enriched)` | Warning logged, never blocks response |
| 19 | `router.py:647` | `response_cache.set(trace_id, enriched)` | Never fails |
| 20 | `router.py:649` | `return NyayaResponse(**enriched)` | Raises Pydantic ValidationError → HTTP 500 |

---

## SECTION 3 — ACTUAL SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────┐
│                    NYAI (Live API)                       │
│                                                         │
│  HTTP Layer                                             │
│  ├─ CORS Middleware (localhost + FRONTEND_URL)           │
│  ├─ trace_id Middleware (uuid4 → request.state) ⚠️ORPHAN │
│  └─ Global Exception Handler (FAIL CLOSED JSON)         │
│                                                         │
│  Query Pipeline (POST /nyaya/query)                     │
│  ├─ QueryCleaner → QueryUnderstanding → QueryExpander    │
│  ├─ HybridRetriever (BM25 + FAISS, 12s timeout)         │
│  ├─ CrossEncoderReranker (8s timeout)                   │
│  ├─ LegalReasoningEngine                                │
│  ├─ EnhancedLegalAdvisor (9129 sections, 99 acts)       │
│  ├─ CaseLawRetriever (domain + jurisdiction filtered)   │
│  ├─ ResponseEnricher (timeline, glossary, evidence)     │
│  ├─ SHA256 Hash Computation (input + output)            │
│  ├─ ObserverPipeline.validate_response() [FAIL CLOSED]  │
│  ├─ ResponseBuilder.build() [FAIL CLOSED]               │
│  ├─ trace_guard check [FAIL CLOSED]                     │
│  ├─ OutputBucket.store() → output_logs/nyai_output_log.jsonl ✅
│  └─ NyayaResponse (11 canonical TANTRA fields) ✅       │
│                                                         │
│  Disconnected Modules (exist, not wired)                │
│  ├─ tantra/flow.py [STANDALONE SCRIPT] ❌               │
│  ├─ tantra/sovereign_core_mock.py ❌                    │
│  ├─ governed_execution/pipeline.py ❌                   │
│  ├─ raj_adapter/ ❌                                     │
│  └─ sovereign_agents/ ❌                                │
│                                                         │
│  Ghost Modules (documented, absent)                     │
│  └─ enforcement_engine/ ❌ DOES NOT EXIST               │
└─────────────────────────────────────────────────────────┘
         │
         │  output_bucket stores to disk ✅
         │  sovereign_core push: MISSING ❌
         ▼
┌─────────────────────┐
│ output_logs/*.jsonl │  (local disk only — not API-accessible)
└─────────────────────┘
```

### Module Status Table

| Module | Path | Exists | Imported by `router.py` | Query path | Status |
|--------|------|--------|----------------------|------------|--------|
| ObserverPipeline | `observer/pipeline.py` | ✅ | ✅ `router.py:57` | ✅ validate + record | LIVE |
| ResponseBuilder | `api/response_builder.py` | ✅ | ✅ `router.py:58` | ✅ build gate | LIVE |
| OutputBucket | `tantra/output_bucket.py` | ✅ | ✅ `router.py:59` | ✅ store | LIVE |
| RewardEngine | `rl_engine/reward_engine.py` | ✅ | ✅ lazy `router.py:952` | `/rl_signal` only | LIVE (partial) |
| tantra/flow.py | `tantra/flow.py` | ✅ | ❌ | ❌ | STANDALONE (`flow.py:100`) |
| SovereignCoreMock | `tantra/sovereign_core_mock.py` | ✅ | ❌ | ❌ | DISCONNECTED |
| governed_execution | `governed_execution/pipeline.py` | ✅ | ❌ | ❌ | DISCONNECTED |
| raj_adapter | `raj_adapter/` | ✅ | ❌ | ❌ | DISCONNECTED |
| sovereign_agents | `sovereign_agents/` | ✅ | ❌ | ❌ | DISCONNECTED |
| enforcement_engine | N/A | ❌ | N/A | N/A | ABSENT |
| hash_chain_ledger | `provenance_chain/hash_chain_ledger.py` | ✅ | ❌ | ❌ | DISCONNECTED |

---

## SECTION 4 — SCHEMA AUDIT RESULTS

**Summary:** Internal schema (schemas.py ↔ Observer ↔ ResponseBuilder) is fully aligned on 11 TANTRA canonical fields. External contract (`final_decision_contract.json`) is critically drifted.

- `NyayaResponse`: 34 fields, 11 canonical required, all populated correctly
- `enforcement_decision`: ABSENT from schemas.py — deleted; replaced by `recommendation: Recommendation`
- `RecommendationType`: advisory-only (INFORM/REVIEW/ESCALATE/INSUFFICIENT_DATA)
- `DeterminismProof`: both hash validators active (hex64 pattern in schema + observer + builder)
- `final_decision_contract.json`: STALE v1.0.0 — requires immediate update to v2.0.0
- Frontend validator (`casePayloadValidator.js`): aligned — no `enforcement_decision` references
- Frontend UI (`LegalQueryCard.jsx`, `LegalDecisionDocument.jsx`, `nyayaBackendApi.js`): **drifted** — still expects `enforcement_decision`

**Verdict:** Schema PASS (internal backend) / FAIL (external contract + frontend UI)

---

## SECTION 5 — TRACE AUDIT RESULTS

**Summary:** Trace continuity is maintained within the query handler scope. The HTTP middleware trace is orphaned. The format of `_temp_trace` is non-standard (timestamp+hex6 rather than UUID4).

- `_temp_trace` propagates from handler → ObserverPipeline → LegalQuery → NyayaResponse.trace_id ✅
- `middleware_trace_id` (main.py) is never read by any handler ❌
- trace_guard prevents mutation within pipeline ✅
- 2 effective trace IDs on happy path (`middleware_trace_id` orphaned; `_temp_trace` == `advice.trace_id`) ⚠️

**Verdict:** Trace PARTIAL — internal continuity PASS, HTTP layer FAIL

---

## SECTION 6 — REPLAY AUDIT RESULTS

**Summary:** Full replay is not supported via API. Partial replay is available in-process via `case_summary`. Full data is on disk but not API-accessible.

- `GET /nyaya/trace/{trace_id}`: hardcoded stub, returns empty data ❌
- `GET /nyaya/case_summary?trace_id=...`: reads ResponseCache (in-memory, max 500, FIFO eviction) ⚠️
- `output_bucket`: disk-persisted, tamper-verifiable, full response stored — but no HTTP endpoint ⚠️
- `hash_chain_ledger.py`: not called from query handler ❌

**Verdict:** Replay NOT READY for TANTRA — trace endpoint is stub, ledger disconnected

---

## SECTION 7 — OBSERVER AUDIT RESULTS

**Summary:** Observer is a pure witness. It records pipeline steps, validates 11 canonical fields, validates hash formats, validates trace continuity, and blocks on failure. It never modifies data.

- Classification: **PURE WITNESS**
- Blocking: YES — FAIL → SchemaValidationError → HTTP 500
- Data modification: NONE (verified by code inspection)
- Double-gate with ResponseBuilder: YES — identical field list, both fail-closed
- Trace validation: checks `response_trace == self.trace_id` (= `_temp_trace`)

**Verdict:** Observer PASS — correctly implemented as audit/witness layer

---

## SECTION 8 — CONSTITUTIONAL AUDIT RESULTS

**Summary:** NYAI cannot accidentally become an authority in current code. The enforcement engine is deleted. All decision outputs are advisory. The RL engine is compute-only with no persistence. One presentation-layer risk exists via the Groq `answer` field.

- Authority ceiling: Advisory recommendation only
- `enforcement_decision` field: DELETED
- `GovernedExecutionPipeline`: always approves, advisory-only
- RL reward: computed but not persisted — no drift risk currently
- Hidden authority risk: `answer` field (Groq free-text) — presentation layer only, not code-level
- CAN NYAI ACCIDENTALLY BECOME AUTHORITY: **NO** (in current code)

**Verdict:** Constitutional PASS — advisory boundaries correctly enforced

---

## SECTION 9 — CONVERGENCE AUDIT RESULTS

**Summary:** NYAI sits at the Intelligence → Decision → Contract stages of TANTRA. Enforcement is absent by design. Execution stage is partially implemented (OutputBucket live, SovereignCore not wired). Truth and Observability stages are partially implemented.

| Stage | Status |
|-------|--------|
| Signal → Intelligence → Decision → Contract | ✅ LIVE |
| Enforcement | ❌ ABSENT (by design — advisory model) |
| Execution (SovereignCore push) | ❌ NOT WIRED |
| Execution (OutputBucket) | ✅ LIVE |
| Truth (DeterminismProof) | ✅ LIVE |
| Truth (HashChain) | ❌ DISCONNECTED |
| Observability (ObserverPipeline) | ✅ LIVE |
| Observability (Trace endpoint) | ❌ STUB |

**8 blockers must be resolved before TANTRA convergence approval** (see `CONVERGENCE_AUDIT.md` BL-001–BL-008). **TANTRA convergence: NOT APPROVED.**

---

## SECTION 10 — CRITICAL RISKS

| Priority | Risk | Fix |
|----------|------|-----|
| P1 | `final_decision_contract.json` is stale — blocks all downstream consumers | Update to v2.0.0 |
| P2 | SovereignCore push missing — TANTRA chain broken after NYAI | Wire `sovereign_core.receive()` |
| P3 | `/trace/` endpoint is stub — no event replay | Implement from `output_bucket.retrieve()` |
| P4 | HTTP middleware trace orphaned — HTTP layer correlation impossible | Use `request.state.trace_id` as `_temp_trace` |
| P5 | Zero test CI — regressions undetected | Add 3 minimum integration tests |
| P6 | Frontend UI expects `enforcement_decision` — badges won't render | Migrate to `recommendation.type` |

---

## SECTION 11 — EVIDENCE

All findings are based on direct code inspection of the following files:

| File | Lines Inspected | Key Findings |
|------|----------------|-------------|
| `backend/api/main.py` | Full (153 lines) | CORS fallback `main.py:47`, middleware orphan `main.py:71-72`, router inclusion `main.py:77` |
| `backend/api/router.py` | Full (975 lines) | `_temp_trace` `router.py:118`, query pipeline, trace_guard `router.py:636-638`, stub trace `router.py:771-783` |
| `backend/api/schemas.py` | Full (263 lines) | NyayaResponse `schemas.py:138-156`, RecommendationType `schemas.py:25-30`, validator `schemas.py:129-133` |
| `backend/api/response_builder.py` | Full (~130 lines) | CANONICAL_FIELDS list, VALID_RECOMMENDATION_TYPES, tantra_v3 stamp |
| `backend/observer/pipeline.py` | Full (~175 lines) | Pure witness classification, validate_response, blocking behavior |
| `backend/tantra/output_bucket.py` | Full (~100 lines) | Disk persistence, JSONL append, verify() tamper detection |
| `backend/tantra/flow.py` | First 80 lines | Standalone script confirmed (`if __name__ == "__main__":`) |
| `backend/tantra/sovereign_core_mock.py` | Full (~80 lines) | Mock status, in-memory receipts, validation logic |
| `backend/governed_execution/pipeline.py` | Full | Always approves, advisory-only, not imported by router |
| `backend/rl_engine/reward_engine.py` | Lines 1–130 | Delta bounds, volatility cap, no persistent write |
| `backend/clean_legal_advisor.py` | Lines 1990–2000 | trace_id reuse from legal_query |
| `final_decision_contract.json` | Full | `enforcement_decision` required at line 27, enum at 47-50 |
| `frontend/vercel.json` | Full | `VITE_API_URL` — correct |
| `frontend/src/lib/casePayloadValidator.js` | Full grep | No `enforcement_decision` references |
| `frontend/src/components/LegalQueryCard.jsx` | grep | Still references `enforcement_decision` — UI drift |
| `backend/api/dependencies.py` | Lines 9-11 | `get_trace_id()` generates new uuid4 — not middleware trace |
| `backend/.github/workflows/ci.yml` | Full | `pytest \|\| echo` — zero-test pass |
| `backend/requirements.txt` | Full | `torch==2.1.2`, `faiss-cpu`, `sentence-transformers` |
| `backend/raj_adapter/enforcement_integration.py` | Lines 1–60 | Advisory-only, not imported by router |
| ZIP listing | All 200+ files | `enforcement_engine/` confirmed absent; all other dirs confirmed present |

---

## SECTION 12 — FINAL VERDICT

### NYAI Readiness Classification: **INTEGRATION READY**

### TANTRA Convergence Approval: **NOT GRANTED**

**What NYAI actually is:**
A multi-jurisdiction legal AI backend that correctly implements the TANTRA canonical schema for its response output. The enforcement engine has been deleted by design and replaced with an advisory-only recommendation system. The TANTRA-facing outputs (11 canonical fields, SHA256 hash proofs, fail-closed validation) are correctly implemented and internally consistent.

**What NYAI is not:**
- Not production-ready (stale contract, stub endpoints, zero test coverage, CORS risk)
- Not TANTRA-converged (SovereignCore push missing, trace endpoint stub, hash chain disconnected)
- Not an enforcement authority (correctly — by design)

**What is proven:**
- Core query pipeline functional and schema-compliant
- ObserverPipeline correctly implemented as pure witness
- ResponseBuilder correctly implemented as fail-closed formatter
- OutputBucket correctly implemented with disk persistence and tamper detection
- DeterminismProof correctly computed and validated
- Advisory recommendation correctly typed and validated

**What is assumed (unproven):**
- EnhancedLegalAdvisor returns legally correct information (not audited — outside code scope)
- Groq LLM responses are accurate (not audited — model evaluation outside scope)
- BM25/FAISS retrieval quality (not evaluated)
- Render deployment RAM will be adequate on paid tier

**What must be fixed before TANTRA convergence approval:**
1. Update `final_decision_contract.json` to v2.0.0
2. Wire `SovereignCoreMock.receive()` into live query handler
3. Implement real `/nyaya/trace/{trace_id}` endpoint
4. Unify middleware and handler trace_id to eliminate orphan
5. Add minimum CI test coverage (3 integration tests)
6. Add `GET /nyaya/output/{trace_id}` endpoint for external auditors
7. Connect `hash_chain_ledger.py` to query handler
8. Migrate frontend UI from `enforcement_decision` to `recommendation.type`

