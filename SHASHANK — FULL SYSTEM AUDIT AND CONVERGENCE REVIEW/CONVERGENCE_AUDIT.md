# NYAI — TANTRA CONVERGENCE AUDIT
**Audit Sprint:** NYAI Independent Forensic Audit
**Date:** 09 June 2026

---

## TANTRA SIGNAL CHAIN — NYAI POSITION MAP

```
TANTRA Chain:
Signal → Intelligence → Decision → Contract → Enforcement → Execution → Truth → Observability

NYAI Position:
  Signal       ✅ LIVE      POST /nyaya/query receives user queries
  Intelligence ✅ LIVE      EnhancedLegalAdvisor + BM25 + FAISS + Groq + CrossEncoder
  Decision     ⚠️ ADVISORY  Recommendation (INFORM/REVIEW/ESCALATE/INSUFFICIENT_DATA) — not a gate
  Contract     ✅ LIVE      NyayaResponse Pydantic schema — 11 canonical fields, fail-closed
  Enforcement  ❌ ABSENT    enforcement_engine/ deleted; governed_execution advisory-only
  Execution    ⚠️ PARTIAL   OutputBucket live; SovereignCore push disconnected
  Truth        ⚠️ PARTIAL   DeterminismProof live; hash_chain_ledger disconnected
  Observability⚠️ PARTIAL   ObserverPipeline live; /trace/ endpoint is stub
```

---

## TANTRA MODULE-BY-MODULE STATUS

### tantra/output_bucket.py — ✅ LIVE & INTEGRATED

**Integration point:** `router.py` imports `from tantra.output_bucket import output_bucket` at line 59
**Called at:** `router.py` line 644: `output_bucket.store(enriched)`
**Storage:** `backend/output_logs/nyai_output_log.jsonl` — disk-persisted, append-only
**Persistence:** Survives process restarts; rebuilds in-memory index from JSONL on startup
**Verification:** `output_bucket.verify(trace_id)` recomputes entry_hash — tamper detection works
**Gap:** Not accessible via any HTTP endpoint — TANTRA auditors cannot query it externally

### tantra/flow.py — ❌ STANDALONE SCRIPT ONLY

**Status:** `if __name__ == "__main__":` block — must be run manually as `python tantra/flow.py`
**Not imported** by any API endpoint, router, or scheduled job
**What it does:** Full TANTRA pipeline simulation:
  1. POST query to NYAI (HTTP call to 127.0.0.1:8000)
  2. Forward response to SovereignCoreMock
  3. Store in OutputBucket
  4. Verify from OutputBucket
**Gap:** No scheduler, no webhook, no API endpoint triggers this flow automatically

### tantra/sovereign_core_mock.py — ❌ MOCK, NOT WIRED TO LIVE API

**Status:** Mock implementation — `sovereign_core: str = "MOCK"` in receipt
**Validation it performs:**
  - Checks all 11 CANONICAL_FIELDS present
  - Checks trace_id continuity (expected vs actual)
  - Checks determinism_proof has both hashes
**Storage:** In-memory `self._receipts: List[Dict]` — lost on process restart
**Critical gap:** `sovereign_core_mock` is only called from `tantra/flow.py` (standalone script), NOT from the live API. NYAI never pushes to any sovereign core during normal operation.

### governed_execution/pipeline.py — ❌ DISCONNECTED

**Status:** File exists, module works, but is not imported by `router.py` or any active endpoint
**Advisory behavior confirmed:** Always sets `governance_approved: True`, always returns INFORM/ESCALATE advisory
**No actual gating logic** — rubber stamp
**Gap:** Cannot be connected without architecture decision on whether it should gate anything

### raj_adapter/ — ❌ DISCONNECTED

**Status:** `enforcement_integration.py` (now `RajReasoningIntegrator`) and `schema_consumer.py` exist
**Real schema files present:** `raj_schemas/failure_paths_v2.json`, `evidence_readiness_v2.json`, `system_compliance_v2.json` — all valid JSON, loaded when `RajSchemaConsumer` is instantiated
**Gap:** `RajReasoningIntegrator` is not imported by `router.py` or any active endpoint
**When reconnected:** Will provide advisory failure path analysis, evidence readiness, compliance checks — all advisory only per module docstring

### sovereign_agents/ — ❌ DISCONNECTED

**Status:** `base_agent.py`, `legal_agent.py`, `constitutional_agent.py`, `jurisdiction_router_agent.py` — all present
**Gap:** Not imported by any active endpoint
**Risk:** If reconnected without review, `jurisdiction_router_agent.py` may attempt routing decisions — requires constitutional review before reconnection

---

## BROKEN LINKS — MUST FIX BEFORE TANTRA CONVERGENCE APPROVAL

| # | Broken Link | Impact | Fix Required |
|---|------------|--------|-------------|
| BL-001 | `final_decision_contract.json` requires `enforcement_decision` — not in NyayaResponse | ALL downstream TANTRA consumers reject NYAI output | Update contract to v2.0.0 reflecting recommendation schema |
| BL-002 | `tantra/flow.py` not callable from the API | TANTRA end-to-end flow cannot be triggered programmatically | Expose `run_tantra_flow()` as an endpoint OR create a scheduler |
| BL-003 | `SovereignCoreMock` not called from live API | NYAI never pushes outputs to TANTRA sovereign core | Wire `sovereign_core.receive(enriched, expected_trace_id=trace_id)` into query handler |
| BL-004 | `GET /nyaya/trace/{trace_id}` returns stub | TANTRA observability chain is broken — no event chain replay | Implement endpoint to read from `output_bucket.retrieve(trace_id)` |
| BL-005 | `hash_chain_ledger.py` not called | Hash-chain provenance is never written | Import and call `ledger.append_entry()` in the query handler |
| BL-006 | No HTTP endpoint for `output_bucket.retrieve()` | External TANTRA auditors cannot access the output log | Add `GET /nyaya/output/{trace_id}` endpoint |
| BL-007 | Middleware trace_id orphaned | HTTP layer trace cannot be correlated with response trace | Read `request.state.trace_id` in handler and use as `_temp_trace` |
| BL-008 | `DETERMINISM_GUARD_ENABLED` defaults to false | Determinism guard is off; hash mismatches silently pass | Set default to true or make it required in deployment config |

---

## WHAT NYAI CURRENTLY DELIVERS TO TANTRA

When `POST /nyaya/query` completes successfully, TANTRA receives:

```json
{
  "trace_id":          "trace_20260510_143022_a1b2c3",
  "request_id":        "req_abc123def456",
  "input_hash":        "<64-char sha256 hex>",
  "output_hash":       "<64-char sha256 hex>",
  "timestamp":         "2026-05-10T14:30:22.000000Z",
  "legal_context":     { "jurisdiction": "India", "domain": "civil", "applicable_laws": [...] },
  "facts":             [5 structured Fact objects],
  "analysis":          { "issues_identified": [...], "rule_application": [...], "conflicts": [...] },
  "recommendation":    { "type": "INFORM", "confidence": 0.82, "rationale": "..." },
  "explanation_chain": [8 structured ExplanationStep objects],
  "risk_flags":        ["NO_STATUTES: ..."] or [],
  "determinism_proof": { "input_hash": "...", "output_hash": "...", "version": "3.0.0" },
  "observer_validation": { "validation_status": "PASS", "determinism_verified": true, ... },
  "metadata":          { "schema": "tantra_v3", "formatter_version": "3.0.0", ... },
  "statutes":          [...],
  "answer":            "LLM explanation text",
  ...
}
```

This output is **pushed only to `output_logs/nyai_output_log.jsonl` locally**. It is NOT forwarded to any external TANTRA sovereign core.

---

## CONVERGENCE READINESS BY STAGE

| Stage | Current State | Gap to Convergence |
|-------|-------------|-------------------|
| Signal | LIVE | None |
| Intelligence | LIVE | None — Groq fallback exists |
| Decision | ADVISORY LIVE | Semantic gap: advisory ≠ enforcement; contract must be updated |
| Contract | LIVE internally | `final_decision_contract.json` must be updated to v2.0.0 |
| Enforcement | ABSENT | Must define whether TANTRA requires enforcement or accepts advisory |
| Execution | PARTIAL | SovereignCore push must be wired; output_bucket HTTP endpoint needed |
| Truth | PARTIAL | hash_chain_ledger must be connected; determinism guard must be enabled |
| Observability | PARTIAL | /trace/ endpoint must be implemented; observer_steps accessible but not queryable |

---

## CONVERGENCE APPROVAL BLOCKERS

Before TANTRA convergence approval can be granted, these items must be resolved:

1. **BL-001 (CRITICAL):** Update `final_decision_contract.json` to v2.0.0 — remove `enforcement_decision`, add `recommendation` schema
2. **BL-003 (HIGH):** Wire `SovereignCoreMock.receive()` call into live query handler
3. **BL-004 (HIGH):** Implement real `/nyaya/trace/{trace_id}` endpoint (reads from `output_bucket`)
4. **BL-006 (HIGH):** Add `GET /nyaya/output/{trace_id}` endpoint for external TANTRA auditor access
5. **Contract clarity (HIGH):** Formally document that `Recommendation.type` replaces `enforcement_decision` for TANTRA purposes — update TANTRA integration spec

