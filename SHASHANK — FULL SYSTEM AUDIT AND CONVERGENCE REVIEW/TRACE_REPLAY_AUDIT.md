# NYAI — TRACE & REPLAY AUDIT
**Audit Sprint:** NYAI Independent Forensic Audit
**Date:** 09 June 2026

---

## TRACE ID LIFECYCLE — FULL MAP

### Three Distinct IDs Generated Per Request

```
HTTP Request arrives at NYAI
│
├─► [ID-1] middleware_trace_id
│       Generated: `main.py:71-72` — str(uuid.uuid4())
│       Stored:    request.state.trace_id
│       Fate:      ORPHANED — `query_legal()` never reads `request.state.trace_id`
│       Used in:   `main.py:57` global_exception_handler fallback only
│
└─► query_legal() handler begins
    │
    ├─► [ID-2] _temp_trace
    │       Generated: `router.py:118`
    │                  f"trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    │       Format:    "trace_20260510_143022_a1b2c3"  (NOT a standard UUID)
    │       Passed to: ObserverPipeline(trace_id=_temp_trace)
    │       Passed to: LegalQuery(trace_id=_temp_trace)
    │
    └─► EnhancedLegalAdvisor.provide_legal_advice(legal_query)
        │
        └─► [ID-3] advice.trace_id
                Generated: `clean_legal_advisor.py:1995`
                           legal_query.trace_id or f"trace_{timestamp_%f}"
                Value:     == _temp_trace (reuses passed value since it was provided)
                Placed in: `router.py:451` base_response["trace_id"] = advice.trace_id

[ID-2] == [ID-3]  →  CONTINUOUS within handler (happy path: 2 effective IDs, not 3)
[ID-1] != [ID-2]  →  ORPHANED at HTTP layer
```

### Trace Continuity Verdict

| Scope | Continuous? | Evidence |
|-------|------------|----------|
| Within query handler (router → advisor → observer → response) | ✅ YES | _temp_trace == advice.trace_id; observer initialized with same value |
| Across HTTP middleware boundary | ❌ NO | middleware_trace_id never read by handler |
| Across process restarts | ✅ YES (via OutputBucket) | Disk-persisted JSONL with trace_id key |
| Via GET /nyaya/trace/{trace_id} | ❌ NO | Endpoint returns hardcoded empty stub |

---

## TRACE_GUARD ANALYSIS

```python
# router.py:635-638 — after ResponseBuilder.build()
final_trace = enriched.get('trace_id', '')
if final_trace != _temp_trace and final_trace != advice.trace_id:
    raise TraceContinuityError(_temp_trace, final_trace)
```

**Logic:** OR condition — passes if `final_trace` equals EITHER `_temp_trace` OR `advice.trace_id`.
**Practical effect:** Since `_temp_trace == advice.trace_id` in all normal cases, this is equivalent to checking `final_trace == _temp_trace`.
**What it prevents:** Any middleware, enricher, or builder step from overwriting `trace_id` in the response dict.
**What it does NOT prevent:** The orphaned HTTP middleware trace_id — that mismatch is never detected.

---

## REPLAY CAPABILITY ASSESSMENT

### GET /nyaya/trace/{trace_id} — STUB (`router.py:771-783`)
```python
@router.get("/trace/{trace_id}", response_model=TraceResponse)
async def get_trace(trace_id: str):
    return TraceResponse(
        trace_id=trace_id,
        event_chain=[],              # HARDCODED EMPTY
        agent_routing_tree={},       # HARDCODED EMPTY
        jurisdiction_hops=[],        # HARDCODED EMPTY
        rl_reward_snapshot={},       # HARDCODED EMPTY
        context_fingerprint="mock_fingerprint",  # HARDCODED
        nonce_verification=True,
        signature_verification=True
    )
```
**Replay from this endpoint: NOT POSSIBLE.**
The endpoint accepts a trace_id but does not query `response_cache`, `output_bucket`, or `hash_chain_ledger`. It returns fabricated data.

### GET /nyaya/case_summary?trace_id= — PARTIAL REPLAY
- Queries `response_cache.get(trace_id)` — in-memory LRU (500 entries, FIFO eviction)
- Returns: statutes, recommendation, confidence, domain, jurisdiction, risk_flags, timeline, glossary, evidence_requirements
- **Limitation:** Cache is in-memory. After process restart or >500 queries, the trace_id is gone.
- **Replay capability:** Partial (no event chain, no hash proof, no observer steps)

### OutputBucket — DISK REPLAY (Internal Only)
- File: `backend/output_logs/nyai_output_log.jsonl` (append-only JSONL)
- Stores: full `NyayaResponse` dict + `input_hash` + `output_hash` + `entry_hash` (tamper-detection)
- `bucket.verify(trace_id)` recomputes `entry_hash` and checks for tampering
- **Not exposed via any HTTP endpoint**
- **Full replay data is present** — but inaccessible to external TANTRA consumers

### hash_chain_ledger.py — DISCONNECTED
- File: `backend/provenance_chain/hash_chain_ledger.py`
- Status: EXISTS but is **not imported** by `router.py` or any active endpoint
- The `provenance_chain` field in `NyayaResponse` is a single-entry list built inline at `router.py:400-408` via `observer.get_provenance_entry()` — it is NOT the hash-chained ledger
- The actual hash chain is never written to during query processing

---

## END-TO-END TRACE PROOF SCENARIOS

### Scenario A: Trace Proof (Happy Path)
```
1. POST /nyaya/query → response contains:
   trace_id: "trace_20260510_143022_a1b2c3"
   determinism_proof.input_hash: "abc123...64chars"
   determinism_proof.output_hash: "def456...64chars"
   observer_validation.validation_status: "PASS"
   metadata.schema: "tantra_v3"

2. output_logs/nyai_output_log.jsonl → entry added:
   trace_id: "trace_20260510_143022_a1b2c3"
   entry_hash: sha256 of entry
   full_response: {...}

3. GET /nyaya/case_summary?trace_id=trace_20260510_143022_a1b2c3
   → Returns statutes + recommendation + confidence (partial replay ✅)

4. GET /nyaya/trace/trace_20260510_143022_a1b2c3
   → Returns EMPTY STUB (full replay ❌)
```

### Scenario B: Same Input, Determinism Check
```
Same query submitted twice:
- input_hash is IDENTICAL (deterministic SHA256 of canonical input)
- request_id is IDENTICAL (f"req_{input_hash[:12]}")
- output_hash MAY differ if statutes change (BM25 index mutable) or Groq LLM returns different answer
- trace_id WILL differ (new uuid4 per request)

→ Determinism proof covers: statutes, jurisdiction, domain, recommendation type, facts, rule_application
→ Determinism proof EXCLUDES: answer (Groq text), timestamp, trace_id, observer_steps
```

---

## REPLAY AUDIT VERDICT

| Capability | Status | Gap |
|-----------|--------|-----|
| trace_id in response | ✅ Present | — |
| trace_id continuity (handler scope) | ✅ Continuous | — |
| trace_id continuity (HTTP scope) | ❌ Broken | Middleware trace orphaned |
| trace_id on disk (OutputBucket) | ✅ Persisted | Not API-accessible |
| Full event chain replay | ❌ Not possible | /trace/ endpoint is stub |
| Partial case replay | ✅ Possible (in-process) | Only while in ResponseCache |
| Hash-chain provenance | ❌ Disconnected | hash_chain_ledger not called |
| Tamper detection | ✅ Possible (OutputBucket.verify) | Internal only |
| TANTRA sovereign trace handoff | ❌ Not wired | SovereignCoreMock disconnected |

