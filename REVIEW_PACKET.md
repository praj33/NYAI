# NYAI — REVIEW PACKET (BHIV Submission)

**Sprint:** Constitutional Evidence Infrastructure — Phase IV Production Transition  
**Date:** 23 June 2026  
**Status:** COMPLETE — **34/34** tests PASS  
**Contract:** `final_decision_contract.json` v2.0.0 · `schema_version: tantra_v3` · `evidence_v1`

> **Authoritative operational review packet** (project root).  
> **Phase IV deliverables:** [`Shashank-Constitutional Evidence Infrastructure (NYAI__ Phase IV Production Transition)/`](./Shashank-Constitutional%20Evidence%20Infrastructure%20(NYAI__%20Phase%20IV%20Production%20Transition)/)  
> **Prior sprint proofs:** [`SHASHANK-NYAI_CONVERGENCE_IMPLEMENTATION_PLAN/`](./SHASHANK-NYAI_CONVERGENCE_IMPLEMENTATION_PLAN/)

---

## BHIV Onboarding Index

Every BHIV submission must include the six sections below. Start here.

| # | Section | Jump |
|---|---------|------|
| 1 | [Entry Points](#1-entry-points) | How to run the server, env vars, primary URLs |
| 2 | [Flow](#2-flow) | Request → evidence → replay → audit paths |
| 3 | [Files](#3-files) | Every new/changed file and its role |
| 4 | [Testing](#4-testing) | Suites, commands, what each test proves |
| 5 | [Failure Modes](#5-failure-modes) | HTTP codes, fail-closed behavior, degraded paths |
| 6 | [Evidence](#6-evidence) | Proof artifacts, live trace_ids, verification steps |

---

## 1. Entry Points

### Start the server

```bash
cd backend
export NYAI_API_KEY=your-secret-key        # required — both /nyaya/* and /evidence/*
export RATE_LIMIT_PER_MINUTE=60            # optional, default 60
uvicorn api.main:app --reload --port 8000
# Windows: use --port 8001 if 8000 is blocked
```

### Environment variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `NYAI_API_KEY` | **Yes** (production) | Fail-closed auth for `/nyaya/*` and `/evidence/*` |
| `RATE_LIMIT_PER_MINUTE` | No | Per-IP sliding window (default 60) |
| `RATE_LIMIT_BURST` | No | Burst cap per second (default 10) |
| `FRONTEND_URL` | No | CORS origin (wildcard if unset) |

### Application entry

| Item | Location |
|------|----------|
| FastAPI app | `backend/api/main.py` |
| Legal query router | `backend/api/router.py` — prefix `/nyaya` |
| Evidence router | `backend/api/evidence_router.py` — prefix `/evidence` |
| Trace middleware | `main.py` — `uuid4` → `request.state.trace_id` |
| Global fail-closed | `main.py` — unhandled errors → HTTP 500 |

### Middleware stack (order)

```
CORS → TraceIdMiddleware → StructuredLoggingMiddleware → RateLimiterMiddleware → APIKeyAuthMiddleware → Route Handler
```

**Protected prefixes:** `/nyaya/*`, `/evidence/*`  
**Exempt:** `/health`, `/health/live`, `/health/ready`, `/metrics`, `/docs`, `/redoc`, `/`

### Primary endpoints

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| `POST` | `/nyaya/query` | Yes | Primary legal query pipeline |
| `POST` | `/nyaya/tantra_flow` | Yes | TANTRA participation proof |
| `GET` | `/nyaya/trace/{trace_id}` | Yes | Observer replay + tamper check |
| `GET` | `/nyaya/output/{trace_id}` | Yes | Stored output + hash proof |
| `GET` | `/evidence/{trace_id}` | Yes | Canonical `EvidencePackage` |
| `GET` | `/evidence/search` | Yes | Multi-filter evidence search |
| `POST` | `/evidence/verify` | Yes | Entry integrity check |
| `POST` | `/evidence/compare` | Yes | Determinism comparison |
| `POST` | `/evidence/export` | Yes | JSON or summary export |
| `GET` | `/health/ready` | No | Readiness incl. `evidence_repository` |

Full evidence API: [`Evidence_API.md`](./Shashank-Constitutional%20Evidence%20Infrastructure%20(NYAI__%20Phase%20IV%20Production%20Transition)/Evidence_API.md) (12 routes).

### Frontend integration

`frontend/src/services/nyayaApi.js` → `GravitasResponseTransformer.js` → `RecommendationGatekeeper.jsx` / `RecommendationStatusCard.jsx`

---

## 2. Flow

### A. Query → Evidence (primary path)

```
Client POST /nyaya/query  [X-API-Key]
  → trace_id middleware (uuid4)
  → query_legal() deterministic pipeline
      Ingest → Retrieve → Reason → Assemble → Hash → Validate → Guard → Persist
  → output_bucket.store()          [JSONL append + entry_hash]
  → response_cache.set()           [L1 write-through]
  → NyayaResponse JSON returned
```

On demand, any stored entry reconstructs as `EvidencePackage` via `EvidenceRepository.get_by_trace_id()`.

### B. Evidence read path

```
Client GET /evidence/{trace_id}  [X-API-Key]
  → evidence_router → evidence_service
  → EvidenceRepository → FileSystemBackend → OutputBucket [O(1) line seek]
  → EvidencePackage.from_stored_entry()
  → JSON response
```

### C. Replay path (reconstruct, not re-execute)

```
trace_id
  → replay_service.replay_by_trace()
  → EvidenceRepository.get_by_trace_id()
  → verification_service.verify_by_trace_id()
  → {replayed: true, evidence: {...}, integrity_status, tamper_detected}
```

Replay does **not** call `POST /nyaya/query` again. Details: [`Replay_Architecture.md`](./Shashank-Constitutional%20Evidence%20Infrastructure%20(NYAI__%20Phase%20IV%20Production%20Transition)/Replay_Architecture.md).

### D. Secondary `/nyaya/*` read path (L1 → L2 fallback)

```
GET /nyaya/case_summary?trace_id=
  → resolve_cached_response(trace_id, response_cache)
      L1: response_cache.get()
      L2: evidence_repository.get_raw_by_trace_id()   [survives restart]
  → 200 with summary JSON  |  404 if not in bucket
```

Applies to: `case_summary`, `legal_routes`, `timeline`, `glossary`, `recommendation_status`.

### E. TANTRA participation (unchanged)

```
POST /nyaya/tantra_flow → run_tantra_flow() → POST /nyaya/query
  → SovereignCoreMock.receive() → bucket verify → flow_status PASS|FAIL
```

### F. Security gate

```
Request to /nyaya/* or /evidence/*
  → NYAI_API_KEY set?          No → 503 AUTH_CONFIGURATION_ERROR
  → X-API-Key present?         No → 401 UNAUTHORIZED
  → hmac.compare_digest?       No → 401 INVALID_API_KEY
  → Rate limit check           Over → 429 RATE_LIMIT_EXCEEDED
  → Proceed to handler
```

### G. Trace continuity (unchanged)

One `trace_id` from HTTP middleware through `ObserverPipeline` → `NyayaResponse` → `output_bucket.store()` → ledger append.

Proof: [`TRACE_CONTINUITY_PROOF.md`](./SHASHANK-NYAI_CONVERGENCE_IMPLEMENTATION_PLAN/TRACE_CONTINUITY_PROOF.md)

---

## 3. Files

### Phase IV — New files

| File | Role |
|------|------|
| `backend/evidence/__init__.py` | Package export: `EvidencePackage`, `EVIDENCE_SCHEMA_VERSION` |
| `backend/evidence/models.py` | Canonical `EvidencePackage` — 8 dataclasses, `from_stored_entry()` |
| `backend/evidence/storage_backend.py` | `EvidenceStorageBackend` Protocol; `FileSystemBackend`; Redis/S3 stubs |
| `backend/evidence/repository.py` | Single source of truth — read, search, date/version filters, ledger lookup |
| `backend/evidence/integrity.py` | Entry hash recomputation + ledger chain verification |
| `backend/evidence/replay_engine.py` | Replay by trace/hash/recommendation/jurisdiction/statute; `compare_evidence()` |
| `backend/evidence/search.py` | Multi-filter search with pagination |
| `backend/evidence/exporter.py` | JSON and summary export formats |
| `backend/api/evidence_router.py` | 12 `/evidence/*` routes — thin orchestration only |
| `backend/services/evidence_service.py` | API orchestration + `resolve_cached_response()` L2 helper |
| `backend/services/replay_service.py` | Replay and compare operations |
| `backend/services/verification_service.py` | Integrity and chain verification |
| `backend/services/query_executor.py` | Shared ThreadPoolExecutor pools (hybrid retrieval + reranker) |
| `backend/tests/test_evidence_infrastructure.py` | 13 evidence infrastructure tests |

### Phase IV — Patched files

| File | Change |
|------|--------|
| `backend/tantra/output_bucket.py` | O(1) line-number index; `retrieve_as_evidence()`; `list_all()` |
| `backend/api/router.py` | Shared thread pools; L2 fallback via `resolve_cached_response()` on 5 endpoints |
| `backend/api/main.py` | `include_router(evidence_router)` |
| `backend/api/health.py` | `evidence_repository` readiness check |
| `backend/api/security.py` | Auth extended to `/evidence/*` |
| `backend/api/rate_limiter.py` | Rate limit extended to `/evidence/*` |
| `backend/README.md` | Phase IV section added |

### Phase IV — Documentation deliverables

| File | Role |
|------|------|
| `Shashank-.../README.md` | Deliverables index + proof artifact links |
| `Shashank-.../Architecture.md` | Before/after, component map, security |
| `Shashank-.../Evidence_Model.md` | Dataclass reference + JSON example |
| `Shashank-.../Evidence_API.md` | Full API reference (12 routes) |
| `Shashank-.../Replay_Architecture.md` | Replay semantics and compare |
| `Shashank-.../Migration_Guide.md` | L1/L2 migration, no URL changes |
| `Shashank-.../Future_Extensibility.md` | Redis, S3, Governance Console paths |

### Protected — do not modify without review

`api/schemas.py`, `api/response_builder.py`, `observer/pipeline.py`, `tantra/flow.py`, recommendation semantics, `governed_execution`, `raj_adapter`, `sovereign_agents`.

### Runtime data (generated)

| Path | Content |
|------|---------|
| `backend/output_logs/nyai_output_log.jsonl` | Append-only evidence store |
| `backend/provenance_ledger.json` | Hash chain ledger |

---

## 4. Testing

### Run all sprint suites

```bash
cd backend
pytest tests/test_evidence_infrastructure.py tests/test_production_hardening.py tests/test_tantra_convergence.py -v
```

### Results (23 June 2026)

| Phase | Suite | Tests | Status |
|-------|-------|-------|--------|
| Phase I — TANTRA Convergence | `test_tantra_convergence.py` | 6/6 | PASS |
| Phase II — Production Hardening | `test_production_hardening.py` | 15/15 | PASS |
| Phase IV — Evidence Infrastructure | `test_evidence_infrastructure.py` | 13/13 | PASS |
| **Total** | | **34/34** | **PASS** |

### What each evidence test proves

| Test | Proves |
|------|--------|
| `test_1_evidence_package_model` | `EvidencePackage.from_stored_entry()` builds all required fields |
| `test_2_evidence_repository_get_by_trace_id` | Repository reads from persistent OutputBucket |
| `test_3_get_evidence_endpoint` | `GET /evidence/{id}` returns 200 + canonical package |
| `test_4_evidence_search` | `GET /evidence/search` returns paginated results |
| `test_5_evidence_integrity_verify` | `POST /evidence/verify` returns integrity status |
| `test_6_replay_by_trace` | Replay reconstructs evidence with integrity check |
| `test_7_secondary_endpoints_use_persistent_storage` | `/case_summary` works after cache clear (L2) |
| `test_8_evidence_export` | JSON and summary export formats |
| `test_9_evidence_authentication_enforced` | `/evidence/*` returns 401 without key |
| `test_10_evidence_authentication_invalid_key` | Wrong key returns 401 `INVALID_API_KEY` |
| `test_11_evidence_compare` | `POST /evidence/compare` returns determinism diff |
| `test_12_evidence_search_date_and_version` | Date-range and version filters work |
| `test_13_get_ledger_entry_for_trace` | Ledger cross-reference helper callable |

### CI

`backend/.github/workflows/ci.yml` — convergence + production suites; hard-fail on any failure.

### Manual smoke (requires running server + `NYAI_API_KEY`)

```bash
# Must return 401 without key
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/evidence/search?limit=1
# Expected: 401

# With key — replace TRACE_ID from output_logs
curl -H "X-API-Key: $NYAI_API_KEY" http://localhost:8000/evidence/TRACE_ID
curl -X POST -H "X-API-Key: $NYAI_API_KEY" -H "Content-Type: application/json" \
  -d '{"trace_id":"TRACE_ID"}' http://localhost:8000/evidence/verify
```

---

## 5. Failure Modes

### Legal query pipeline (`/nyaya/query`)

| Condition | HTTP | Behavior |
|-----------|------|----------|
| Observer / ResponseBuilder schema fail | 500 | Fail-closed (`SCHEMA_VALIDATION_ERROR`) |
| Hash mismatch | 500 | Fail-closed |
| Trace ID mutated mid-pipeline | 500 | `TRACE_CONTINUITY_ERROR` |
| Invalid payload | 422 | Rejected before pipeline |
| Unhandled exception | 500 | `TANTRA FAIL CLOSED` (global handler) |
| Bucket / ledger store fail | — | Warning logged; HTTP response still returned |

### Replay endpoints (`/nyaya/trace`, `/nyaya/output`)

| Condition | HTTP | Behavior |
|-----------|------|----------|
| Trace not in bucket | 404 | `trace_id not found in output bucket` |
| Entry hash mismatch on verify | 200 | `tamper_detected: true` in response body |

### Evidence endpoints (`/evidence/*`)

| Condition | HTTP | `error_code` |
|-----------|------|--------------|
| Missing `X-API-Key` | 401 | `UNAUTHORIZED` |
| Wrong API key | 401 | `INVALID_API_KEY` |
| `NYAI_API_KEY` not configured | 503 | `AUTH_CONFIGURATION_ERROR` |
| Rate limit exceeded | 429 | `RATE_LIMIT_EXCEEDED` |
| Evidence not found | 404 | `EVIDENCE_NOT_FOUND` |
| Invalid recommendation filter | 400 | `INVALID_RECOMMENDATION_TYPE` |
| Integrity tamper detected | 200 | `integrity_status: TAMPERED` (fail-open for audit visibility) |

### Secondary read endpoints (post-restart)

| Condition | HTTP | Behavior |
|-----------|------|----------|
| In L1 cache | 200 | Fast path |
| Cache miss, in OutputBucket | 200 | L2 `EvidenceRepository` fallback |
| Not in cache or bucket | 404 | `trace_id not found` |

### Health readiness

| Dependency | Degraded signal |
|------------|-----------------|
| `evidence_repository` | `DEGRADED` in `/health/ready` |
| `output_bucket` / ledger / retriever | `FAIL` → 503 unavailable |

NYAI fails closed on schema and trace integrity — not on legal content. All recommendation types deliver the full advisory document.

---

## 6. Evidence

### Proof artifacts (Phase IV)

Located in [`Shashank-Constitutional Evidence Infrastructure (NYAI__ Phase IV Production Transition)/`](./Shashank-Constitutional%20Evidence%20Infrastructure%20(NYAI__%20Phase%20IV%20Production%20Transition)/):

| Artifact | Proves | Live trace_id |
|----------|--------|---------------|
| [`smoke_test_evidence.json`](./Shashank-Constitutional%20Evidence%20Infrastructure%20(NYAI__%20Phase%20IV%20Production%20Transition)/smoke_test_evidence.json) | GET evidence → verify → search chain (all 200) | `b5c037ef-c877-4972-8517-3d212b4e6220` |
| [`replay_proof.json`](./Shashank-Constitutional%20Evidence%20Infrastructure%20(NYAI__%20Phase%20IV%20Production%20Transition)/replay_proof.json) | `replay_by_trace()` with `integrity_status: VERIFIED` | `b5c037ef-c877-4972-8517-3d212b4e6220` |
| [`example_exported_evidence.json`](./Shashank-Constitutional%20Evidence%20Infrastructure%20(NYAI__%20Phase%20IV%20Production%20Transition)/example_exported_evidence.json) | Full `POST /evidence/export` JSON response | `b5c037ef-c877-4972-8517-3d212b4e6220` |

### Prior sprint proofs (TANTRA convergence)

| Artifact | Proves |
|----------|--------|
| [`tantra_flow_proof.json`](./SHASHANK-NYAI_CONVERGENCE_IMPLEMENTATION_PLAN/tantra_flow_proof.json) | TANTRA flow PASS — trace `e20fb600-7104-43c5-9869-9c4aa8423d82` |
| [`trace_replay_proof.json`](./SHASHANK-NYAI_CONVERGENCE_IMPLEMENTATION_PLAN/trace_replay_proof.json) | Observer replay + tamper verification |
| [`output_proof.json`](./SHASHANK-NYAI_CONVERGENCE_IMPLEMENTATION_PLAN/output_proof.json) | Output bucket hash proof |
| [`CONVERGENCE_AUDIT_REPORT.md`](./SHASHANK-NYAI_CONVERGENCE_IMPLEMENTATION_PLAN/CONVERGENCE_AUDIT_REPORT.md) | 8/8 convergence gaps PASS |

### Acceptance criteria sign-off

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Runtime replay no longer depends on cache alone | PASS | `test_7_secondary_endpoints_use_persistent_storage` |
| Every response produces canonical evidence | PASS | `EvidencePackage.from_stored_entry()` on all bucket entries |
| Evidence independently replayable | PASS | `replay_proof.json` + `test_6_replay_by_trace` |
| Evidence integrity verifiable | PASS | `smoke_test_evidence.json` verify step + `test_5` |
| Replay deterministic | PASS | `test_11_evidence_compare` |
| `/evidence/*` auth enforced | PASS | `test_9`, `test_10` |
| APIs backward compatible | PASS | All `/nyaya/*` tests still PASS (6/6) |
| Documentation enables onboarding | PASS | This packet + 7 deliverable docs |

### Contract verification

```bash
grep -rn "enforcement_decision" backend/api/ frontend/src/
# Expected: 0 results in active paths
```

---

## Appendix A — Contract & Recommendation Semantics

| Property | Value |
|----------|-------|
| Contract file | `final_decision_contract.json` v2.0.0 |
| Schema | `tantra_v3` |
| Evidence schema | `evidence_v1` / format `1.0.0` |
| Recommendation types | INFORM · REVIEW · ESCALATE · INSUFFICIENT_DATA (advisory only) |

**11 API fields:** `trace_id`, `request_id`, `input_hash`, `legal_context`, `facts`, `analysis`, `recommendation`, `explanation_chain`, `risk_flags`, `determinism_proof`, `timestamp`

---

## Appendix B — Known Limitations

| Limitation | Status |
|------------|--------|
| `SovereignCoreMock` in-memory | Deferred |
| OutputBucket local filesystem only | Deferred (S3 stub in `storage_backend.py`) |
| EvidenceSearch sequential scan | Open — no inverted index |
| Rate limiter in-memory (no Redis) | Open |
| `governed_execution` / `raj_adapter` / `sovereign_agents` | Intentionally disconnected |

---

## Appendix C — Next Recommended Sprint

1. Redis for rate limiter and evidence index
2. Persistent sovereign receipt layer
3. Distributed OutputBucket (S3/GCS)
4. Evidence stream for downstream real-time consumers

---

## Verdict

**PHASE IV CONSTITUTIONAL EVIDENCE INFRASTRUCTURE — BHIV SUBMISSION COMPLETE.**

TANTRA convergence preserved (6/6). Production controls preserved (15/15). Evidence infrastructure operational (13/13). Every query execution is a permanent, replayable evidence object. Legal reasoning semantics, trace lifecycle, and advisory posture unchanged.

**Start onboarding here:** Sections [1](#1-entry-points) → [6](#6-evidence) above.
