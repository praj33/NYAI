# NYAI — AUTHORITY MATRIX
**Audit Sprint:** NYAI Independent Forensic Audit
**Date:** 09 June 2026
**Classification:** CONSTITUTIONAL AUDIT OUTPUT

---

## DIMENSION A — What NYAI OWNS

| Capability | Evidence | Scope |
|-----------|----------|-------|
| Legal information retrieval | BM25 + FAISS + cross-encoder reranking in `router.py` lines 135–175 | All 3 jurisdictions (India/UK/UAE) |
| Structured response generation | `NyayaResponse` Pydantic model, 11 canonical TANTRA fields, all populated in `router.py` | Single-request lifecycle |
| Trace lifecycle management | `_temp_trace` generated at handler start, passed to ObserverPipeline and LegalQuery, validated in trace_guard | Within a single HTTP request |
| Schema validation gating | ObserverPipeline (fail-closed) + ResponseBuilder (fail-closed) — two independent validators | Every response |
| Advisory recommendation classification | `RecommendationType.{INFORM,REVIEW,ESCALATE,INSUFFICIENT_DATA}` — rules in `router.py` lines 530–544 | Per-query output |
| Output logging to disk | `OutputBucket` writes to `backend/output_logs/nyai_output_log.jsonl` — append-only, hash-verified entries | Per-query |
| RL signal acceptance | `POST /nyaya/rl_signal` — computes reward, returns to caller, no persistence | Per-signal |
| Jurisdiction detection | `JurisdictionDetector.detect()` — deterministic keyword scoring, confidence score | Per-query |
| Domain classification | `analyze_query()` — keyword + LLM classification, fallback to "civil" | Per-query |

---

## DIMENSION B — What NYAI DOES NOT OWN

| Capability | Evidence | Why |
|-----------|----------|-----|
| Legal decisions | `enforcement_decision` field ABSENT from `NyayaResponse`; `enforcement_engine/` directory does not exist | Deleted per `raj_convergence_task.md` |
| Blocking user access on legal grounds | No enforcement rule applies a BLOCK to a query based on content; HTTP 500 is only for schema violations | Schema guard ≠ content authority |
| Jurisdiction authority | JurisdictionDetector returns `confidence` float — advisory detection, not binding assignment | `Recommendation.type != BIND` |
| Enforcement actions | `GovernedExecutionPipeline` always sets `governance_approved: True`, never rejects | `governed_execution/pipeline.py` line 29 |
| Persistent RL model updates | `RewardEngine.compute_reward()` returns reward value to endpoint caller; no write to any persistent store | `router.py` lines 960–964 |
| TANTRA sovereign receipt | `SovereignCoreMock` is not called from the live API | `router.py` — no import of sovereign_core |
| Downstream contract enforcement | `final_decision_contract.json` v1.0.0 is stale; no code enforces the contract's `enforcement_decision` requirement | Schema mismatch confirmed |

---

## DIMENSION C — Authority Ceiling

```
NYAI's maximum authority is: ADVISORY RECOMMENDATION

The highest action NYAI can take unilaterally:
  - Return HTTP 500 if its own schema validation fails
  - Classify a query as ESCALATE or INSUFFICIENT_DATA (advisory only)
  - Log to local disk (output_logs/)

NYAI cannot:
  - Block a legally valid request from reaching a user
  - Issue an enforcement decision
  - Modify a TANTRA sovereign ruling
  - Persist RL reward changes that affect future queries
```

---

## DIMENSION D — Governance Risks

| Risk | Description | Severity |
|------|-------------|----------|
| D-001 | `CORS fallback ["*"]` — if `FRONTEND_URL` env unset, all origins can query NYAI with no governance oversight | HIGH |
| D-002 | `answer` field (Groq free-text) has no disclaimer or constitutional guardrail in `NyayaResponse` | MEDIUM |
| D-003 | `final_decision_contract.json` still describes enforcement_decision as "SINGLE SOURCE OF TRUTH for gating" — any downstream system reading this contract believes NYAI has enforcement authority it no longer has | HIGH |
| D-004 | `RecommendationType.ESCALATE` could be misinterpreted by a downstream consumer as a hard block rather than an advisory escalation | MEDIUM |
| D-005 | CI allows zero tests to pass — governance drift in code can go undetected | MEDIUM |

---

## DIMENSION E — Hidden Authority Risks

| Risk | Vector | Evidence | Verdict |
|------|--------|----------|---------|
| E-001 | LLM Answer Field | `answer: Optional[str]` — Groq generates free text; frontend displays it; no code constraint on content | **REAL RISK at presentation layer** |
| E-002 | HTTP 500 as content gate | Observer schema failure raises HTTP 500 — de facto content blocking | **ACCEPTABLE** — this is schema enforcement, not legal authority |
| E-003 | `request_id` determinism | Same query always yields same `request_id = req_{input_hash[:12]}` — two identical requests share a request_id | **MINOR** — tracing ambiguity, not authority |
| E-004 | GovernedExecutionPipeline rubber-stamps | Always sets `governance_approved: True` — if connected to a real gating system, it would approve everything | **LATENT RISK** — safe now because it's disconnected |

---

## DIMENSION F — Drift Risks

| Risk | Timeline | Evidence | Mitigation Status |
|------|----------|----------|-------------------|
| F-001 | Immediate | `final_decision_contract.json` schema is already drifted from live `NyayaResponse` — downstream contract consumers will fail today | NONE |
| F-002 | On reconnection | `governed_execution/` and `raj_adapter/` will be reconnected in future sprints; their advisory-only status must be preserved | DOCUMENTED |
| F-003 | On RL persistence | If a future sprint adds persistent reward storage, RL drift becomes a real governance risk (±0.15 per-update cap, ±0.03 per-delta cap) | CAPS IN PLACE but not tested |
| F-004 | On SovereignCore activation | When `sovereign_core_mock.py` is replaced with a real core, the mock's in-memory receipt store (`self._receipts: List`) must be replaced with a persistent audit log | NOT ADDRESSED |

---

## VERDICT: CAN NYAI ACCIDENTALLY BECOME AUTHORITY?

### **NO — in current deployed code**

**Reasoning chain:**
1. `enforcement_decision` field → **deleted from schema** (schemas.py confirmed)
2. `enforcement_engine/` → **directory does not exist** (ZIP listing confirmed)
3. `Recommendation` field → **advisory-only by schema definition and explicit docstring**: `"Advisory-only recommendation. NOT a decision gate."`
4. `GovernedExecutionPipeline` → **always approves, never rejects**
5. `RewardEngine` → **stateless per-request, no persistent write**
6. `ObserverPipeline` → **pure witness, never modifies data**
7. `SovereignCoreMock` → **not called from live API**

### **YES — as a presentation-layer risk (outside code boundary)**

The `answer` field (Groq free-text LLM output) appears in `NyayaResponse` as `Optional[str]`. If a frontend or downstream consumer presents this field as a legal decision rather than an informational summary, NYAI's output becomes de facto authoritative in the user's eyes — even though no enforcement mechanism exists in the code.

**This risk is outside NYAI's code boundary but within TANTRA's governance boundary.**

