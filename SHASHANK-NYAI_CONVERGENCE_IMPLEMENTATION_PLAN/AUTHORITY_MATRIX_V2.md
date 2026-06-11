# NYAI — AUTHORITY MATRIX V2

**Sprint:** NYAI Canonical Convergence Build  
**Branch:** `feature/tantra-convergence-ready`  
**Date:** 11 June 2026  
**Contract:** `final_decision_contract.json` v2.0.0 / `tantra_v3`  
**Audit:** [CONVERGENCE_AUDIT_REPORT.md](./CONVERGENCE_AUDIT_REPORT.md)

---

## DIMENSION A — Authority Owned

| Capability | Evidence | Scope |
|-----------|----------|-------|
| Legal information retrieval | `router.py` hybrid retrieval + BM25 | India/UK/UAE |
| Structured response generation | `NyayaResponse` 11 canonical fields | Per-request |
| Unified trace lifecycle | `main.py` middleware → `router.py` `_temp_trace` | HTTP → sovereign receipt |
| Schema validation gating | ObserverPipeline + ResponseBuilder (fail-closed) | Every response |
| Advisory recommendation | `RecommendationType.{INFORM,REVIEW,ESCALATE,INSUFFICIENT_DATA}` | Per-query |
| Output logging | `OutputBucket` → `output_logs/nyai_output_log.jsonl` | Per-query |
| Provenance chain | `HashChainLedger.append_event()` after store | Per-query |
| TANTRA flow participation | `POST /nyaya/tantra_flow` → `run_tantra_flow()` | On-demand |

---

## DIMENSION B — Authority NOT Owned

| Capability | Evidence | Why |
|-----------|----------|-----|
| Legal enforcement decisions | `enforcement_decision` deleted; `enforcement_engine/` absent | By design |
| Content blocking on legal grounds | No BLOCK/RESTRICT in schema or UI | Advisory model |
| Binding jurisdiction assignment | `JurisdictionDetector` returns confidence float | Advisory detection |
| Persistent RL model updates | `RewardEngine` stateless per-request | No drift path |
| Real sovereign core authority | `SovereignCoreMock` only — in-memory receipts | Mock participation |

---

## DIMENSION C — Execution Rights

**NYAI MAY:**
- Return HTTP 500 on schema validation failure (fail-closed)
- Classify queries as INFORM/REVIEW/ESCALATE/INSUFFICIENT_DATA (advisory)
- Log to disk (output bucket + hash chain ledger)
- Forward output to SovereignCoreMock via `/tantra_flow`
- Replay traces via `/trace/` and `/output/` endpoints

**NYAI MAY NOT:**
- Block legally valid requests based on content policy
- Issue enforcement decisions (ALLOW/BLOCK/RESTRICT)
- Modify TANTRA sovereign rulings
- Persist RL rewards that affect future queries

---

## DIMENSION D — Authority Ceiling

```
Maximum unilateral authority: ADVISORY RECOMMENDATION

Highest actions:
  - HTTP 500 on own schema failure
  - Classify as ESCALATE or INSUFFICIENT_DATA (advisory only)
  - Append to local provenance ledger
```

---

## DIMENSION E — Hidden State Disclosure

| Risk | Vector | Status |
|------|--------|--------|
| LLM answer field | Groq free-text in `answer` | Presentation layer — no code constraint |
| CORS wildcard | `allowed_origins or ["*"]` if FRONTEND_URL unset | Documented limitation |
| RL stateless | No persistent reward storage | Safe currently |
| SovereignCoreMock in-memory | Receipts lost on restart | Documented limitation |
| Hash chain local file | `provenance_ledger.json` on disk only | No remote replication |

---

## DIMENSION F — Governance Drift Risks

| Risk | Timeline | Mitigation |
|------|----------|------------|
| Contract drift | Immediate | **RESOLVED** — v2.0.0 aligned |
| governed_execution reconnection | Future sprint | Constitutional review required |
| RL persistence addition | Future sprint | Caps documented, not yet tested |
| SovereignCoreMock → real core | Future sprint | Requires persistent audit log |
| Frontend enforcement semantics | Immediate | **RESOLVED** — recommendation model |

---

## VERDICT

### NYAI CANNOT ACCIDENTALLY BECOME AUTHORITY

**Evidence chain:**
1. `enforcement_decision` → deleted from contract, schema, frontend
2. `Recommendation` → advisory-only by schema definition
3. `RecommendationGatekeeper` → no content withholding
4. `GovernedExecutionPipeline` → disconnected, always approves when connected
5. `POST /tantra_flow` → `authority_note` explicitly states no authority transfer
6. Live proof: `sovereign_receipt.accepted: true`, `trace_continuity: true`, `flow_status: PASS`
