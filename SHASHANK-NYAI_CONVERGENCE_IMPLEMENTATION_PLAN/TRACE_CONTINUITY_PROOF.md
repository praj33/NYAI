# TRACE CONTINUITY PROOF

**Sprint:** NYAI Canonical Convergence Build  
**Branch:** `feature/tantra-convergence-ready`  
**Date:** 12 June 2026  
**Live trace_id:** `e20fb600-7104-43c5-9869-9c4aa8423d82`  
**Audit:** [CONVERGENCE_AUDIT_REPORT.md](./CONVERGENCE_AUDIT_REPORT.md)

---

## Before / After: Trace ID Unification

### Before (Partial Convergence)

```
HTTP Request
    │
    ├─► middleware (main.py:71) → request.state.trace_id = uuid4()  [ORPHAN]
    │
    └─► query handler (router.py:118) → _temp_trace = trace_YYYYMMDD_hex6  [USED]
            │
            ├─► ObserverPipeline(trace_id=_temp_trace)
            ├─► LegalQuery(trace_id=_temp_trace)
            └─► NyayaResponse.trace_id = advice.trace_id (= _temp_trace)

Result: 2 effective trace IDs per request (middleware orphan + handler trace)
```

### After (TANTRA-Convergence Ready)

```
HTTP Request
    │
    ├─► middleware (main.py:71) → request.state.trace_id = uuid4()
    │
    └─► query handler (router.py) → _temp_trace = request.state.trace_id || fallback
            │
            ├─► ObserverPipeline(trace_id=_temp_trace)
            ├─► LegalQuery(trace_id=_temp_trace)
            ├─► trace_guard: final_trace == _temp_trace
            ├─► output_bucket.store(enriched)
            ├─► HashChainLedger.append_event({trace_id: ...})
            └─► NyayaResponse.trace_id = _temp_trace

Result: 1 unified trace ID from HTTP layer through sovereign receipt
```

---

## Propagation Chain Table

| Stage | File:Line | trace_id Source | Status |
|-------|-----------|-----------------|--------|
| HTTP Middleware | `backend/api/main.py:71-72` | `uuid.uuid4()` → `request.state.trace_id` | LIVE |
| Handler Init | `backend/api/router.py` (~120) | `request.state.trace_id` with fallback | **FIXED** |
| Observer Pipeline | `backend/api/router.py` (~122) | `_temp_trace` | LIVE |
| Legal Query | `backend/api/router.py` (~228) | `_temp_trace` | LIVE |
| Response | `backend/api/router.py` (~454) | `advice.trace_id` (= `_temp_trace`) | LIVE |
| trace_guard | `backend/api/router.py` (~651) | Validates `final_trace == _temp_trace` | LIVE |
| Output Bucket | `backend/api/router.py` (~645) | `enriched.trace_id` | LIVE |
| Hash Chain | `backend/api/router.py` (~653) | `enriched.trace_id` | **ACTIVATED** |
| TANTRA Flow | `backend/tantra/flow.py:46` | From NYAI response | LIVE |

---

## Code Citations

**Middleware trace assignment:**

```python
# backend/api/main.py
trace_id = str(uuid.uuid4())
request.state.trace_id = trace_id
```

**Handler reads middleware trace:**

```python
# backend/api/router.py
_temp_trace = (
    getattr(http_request, 'state', None) and getattr(http_request.state, 'trace_id', None)
) or f"trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
observer = ObserverPipeline(trace_id=_temp_trace)
```

**trace_guard continuity check:**

```python
final_trace = enriched.get('trace_id', '')
if final_trace != _temp_trace and final_trace != advice.trace_id:
    raise TraceContinuityError(_temp_trace, final_trace)
```

---

## Runtime Evidence

**Sprint re-run (12 June 2026):** trace `e20fb600-7104-43c5-9869-9c4aa8423d82`

| Checkpoint | trace_id | Match |
|------------|----------|-------|
| POST /nyaya/query response | `e20fb600-7104-43c5-9869-9c4aa8423d82` | ✅ |
| output_bucket stored | `e20fb600-7104-43c5-9869-9c4aa8423d82` | ✅ |
| GET /nyaya/trace event_chain (all steps) | `e20fb600-7104-43c5-9869-9c4aa8423d82` | ✅ |
| SovereignCoreMock receipt | `e20fb600-7104-43c5-9869-9c4aa8423d82` | ✅ |
| HashChainLedger reconstruct | 1 event for trace | ✅ |

JSON: [`trace_replay_proof.json`](./trace_replay_proof.json), [`tantra_flow_proof.json`](./tantra_flow_proof.json)

Full API evidence: [`TANTRA_CONVERGENCE_PROOF.md`](./TANTRA_CONVERGENCE_PROOF.md) (Phase 6).
