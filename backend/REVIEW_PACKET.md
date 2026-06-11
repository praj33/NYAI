# NYAI — REVIEW PACKET (Post-Convergence)

**Sprint:** NYAI Canonical Convergence Build  
**Date:** 11 June 2026  
**Classification:** TANTRA-CONVERGENCE READY

---

## 1. Entry Point

**Primary entry point:** `backend/api/main.py`  
**Server:** uvicorn, port from `PORT` env (default 8000)  
**Trace middleware:** `main.py:71-72` generates `uuid4` → `request.state.trace_id` — **now canonical trace source** read by query handler.

---

## 2. Core Flow (20 Steps)

| Step | Location | Action | Fail Mode |
|------|----------|--------|-----------|
| 1 | `router.py` | `clean_query()` | Returns original on failure |
| 2 | `router.py:~124` | `_temp_trace = request.state.trace_id` | Fallback to timestamp+hex6 |
| 3 | `router.py` | `ObserverPipeline(_temp_trace)` | Never fails |
| 4 | `router.py` | `analyze_query()` | Falls back to domain="civil" |
| 5 | `router.py` | `expand_query()` | Falls back to original |
| 6 | `router.py` | `hybrid_search()` (12s timeout) | Timeout → empty candidates |
| 7 | `router.py` | `rerank_sections()` (8s timeout) | Timeout → top-5 unranked |
| 8 | `router.py` | `apply_reasoning_rules()` | Returns unmodified |
| 9 | `router.py` | `provide_legal_advice(LegalQuery(trace_id=_temp_trace))` | HTTP 500 |
| 10 | `router.py` | `case_retriever.retrieve()` | Empty list on failure |
| 11 | `router.py` | Compute `input_hash` (SHA256) | Never fails |
| 12 | `router.py` | Build Facts, Analysis, Recommendation | Never fails |
| 13 | `router.py` | Compute `output_hash` (SHA256) | Never fails |
| 14 | `router.py` | `DeterminismProof` | HTTP 500 if invalid hex |
| 15 | `router.py` | `observer.validate_response()` | SchemaValidationError → 500 |
| 16 | `router.py` | `ResponseBuilder.build()` | SchemaValidationError → 500 |
| 17 | `router.py` | trace_guard check | TraceContinuityError → 500 |
| 18 | `router.py` | `output_bucket.store()` | Warning logged, never blocks |
| 19 | `router.py` | `ledger.append_event()` | Warning logged, never blocks |
| 20 | `router.py` | `return NyayaResponse(**enriched)` | Pydantic error → 500 |

---

## 3. Live Flow — POST /nyaya/tantra_flow

1. Receive `QueryRequest` payload
2. `asyncio.to_thread(run_tantra_flow, ...)` — avoids event loop deadlock
3. `run_tantra_flow` POSTs to `/nyaya/query` (same server)
4. Forward output to `SovereignCoreMock.receive()`
5. Store in `OutputBucket`
6. Verify via `OutputBucket.verify()`
7. Return flow proof with `authority_note` (advisory only)

---

## 4. Contract Version

- **Contract:** `final_decision_contract.json` v2.0.0
- **Schema:** `tantra_v3`
- **Recommendation types:** INFORM, REVIEW, ESCALATE, INSUFFICIENT_DATA
- **Removed:** `enforcement_decision`, HMAC enforcement refs

---

## 5. Trace Lifecycle

```
request.state.trace_id (middleware)
    → _temp_trace (handler)
    → ObserverPipeline
    → LegalQuery
    → NyayaResponse.trace_id
    → output_bucket
    → HashChainLedger
    → SovereignCoreMock receipt (via tantra_flow)
```

**Unified:** 1 trace ID from HTTP layer through sovereign receipt.

---

## 6. Replay Lifecycle

```
OutputBucket.store()
    → GET /nyaya/trace/{trace_id}  (observer_steps → event_chain)
    → GET /nyaya/output/{trace_id} (full stored output + verification)
    → HashChainLedger (provenance_ledger.json)
```

---

## 7. Output Bucket Lifecycle

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Store | `output_bucket.store(enriched)` | Automatic on /query |
| Retrieve | `output_bucket.retrieve(trace_id)` | GET /output/{id} |
| Verify | `output_bucket.verify(trace_id)` | Included in /trace/ and /output/ |
| Chain append | `ledger.append_event({...})` | Automatic on /query |

---

## 8. Sovereign Participation

- **Endpoint:** `POST /nyaya/tantra_flow`
- **Flow:** NYAI → SovereignCoreMock → OutputBucket → Verify
- **Authority:** Advisory only — `authority_note` in response
- **Proof:** `sovereign_receipt.accepted: true` (live evidence in [`tantra_flow_proof.json`](../SHASHANK-NYAI_CONVERGENCE_IMPLEMENTATION_PLAN/tantra_flow_proof.json))

---

## 9. Failure Modes

| Condition | Response | Code |
|-----------|----------|------|
| Schema validation failure | `SCHEMA_VALIDATION_ERROR` | 500 |
| Trace continuity violation | `TRACE_CONTINUITY_ERROR` | 500 |
| Invalid request payload | Pydantic validation error | 422 |
| Trace not in bucket | `trace_id not found` | 404 |
| TANTRA flow failure | `TANTRA flow failed` | 500 |
| Global unhandled exception | `TANTRA FAIL CLOSED` | 500 |

---

## 10. Testing Proof

| Test | Verifies |
|------|----------|
| `test_canonical_schema_valid_response` | 11 fields + recommendation.type, no enforcement_decision |
| `test_observer_blocks_invalid_schema` | Empty payload → 422 fail-closed |
| `test_trace_id_same_across_all_stages` | output_bucket trace_id == response trace_id |
| `test_trace_endpoint_returns_real_data` | Non-empty event_chain, tamper_verified |
| `test_output_bucket_retrieval_and_hash_verification` | verification.verified, no tamper |

**Result:** 5/5 passed (local run 11 June 2026)

---

## 11. Convergence Proof

All sprint deliverables: [`SHASHANK-NYAI_CONVERGENCE_IMPLEMENTATION_PLAN/`](../SHASHANK-NYAI_CONVERGENCE_IMPLEMENTATION_PLAN/)

See: [`TANTRA_CONVERGENCE_PROOF.md`](../SHASHANK-NYAI_CONVERGENCE_IMPLEMENTATION_PLAN/TANTRA_CONVERGENCE_PROOF.md) · [`NYAI_CONVERGENCE_HANDOVER.md`](../SHASHANK-NYAI_CONVERGENCE_IMPLEMENTATION_PLAN/NYAI_CONVERGENCE_HANDOVER.md)

Live evidence (in `SHASHANK-NYAI_CONVERGENCE_IMPLEMENTATION_PLAN/`):
- [`tantra_flow_proof.json`](../SHASHANK-NYAI_CONVERGENCE_IMPLEMENTATION_PLAN/tantra_flow_proof.json) — flow_status: PASS
- [`trace_replay_proof.json`](../SHASHANK-NYAI_CONVERGENCE_IMPLEMENTATION_PLAN/trace_replay_proof.json) — 7 event_chain stages
- [`output_proof.json`](../SHASHANK-NYAI_CONVERGENCE_IMPLEMENTATION_PLAN/output_proof.json) — verified, no tamper
- `provenance_ledger.json` index 15 — matching trace_id

---

## 12. Known Limitations

1. **SovereignCoreMock** — in-memory, not persistent
2. **CORS wildcard** — if `FRONTEND_URL` unset
3. **RAM** — 9723-section BM25 index at startup
4. **RL stateless** — no persistent reward storage
5. **Hash chain local** — disk only, no remote replication

---

## Final Verdict

**TANTRA CONVERGENCE READY** — All 8 gaps resolved. Contract, trace, replay, provenance, frontend, testing, and TANTRA participation proven with live API evidence.
