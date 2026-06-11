# SHASHANK — NYAI Convergence Implementation Plan (Deliverables)

Sprint documentation for the NYAI Canonical Convergence Build.

| | |
|--|--|
| **Status** | TANTRA-CONVERGENCE READY |
| **Branch** | `feature/tantra-convergence-ready` |
| **Last updated** | 11 June 2026 |
| **Checklist** | 20/20 passed · 8/8 gaps PASS · phases 1–8 PASS |
| **Tests** | `backend/tests/test_tantra_convergence.py` — 5/5 pass |
| **Contract** | `final_decision_contract.json` v2.0.0 · `schema_version` `tantra_v3` |

---

## Planning Docs (repo root)

| Document | Role |
|----------|------|
| [`NYAI_CONVERGENCE_REMEDIATION_GUIDE.md`](../NYAI_CONVERGENCE_REMEDIATION_GUIDE.md) | Primary gap analysis + phased implementation guide |
| [`NYAI_CONVERGENCE_IMPLEMENTATION_PLAN.md`](../NYAI_CONVERGENCE_IMPLEMENTATION_PLAN.md) | Index plan + phased agent execution guide |
| [`NYAI Full Convergence Remediation Sprint (NYAI__ Canonical Convergence Build).md`](../NYAI%20Full%20Convergence%20Remediation%20Sprint%20(NYAI__%20Canonical%20Convergence%20Build).md) | Original sprint brief |

**Operational review:** [`REVIEW_PACKET.md`](../REVIEW_PACKET.md) (authoritative, 12 sections, project root)

---

## Deliverable Inventory

| Deliverable | File | Phase |
|-------------|------|-------|
| Contract alignment | [CONTRACT_ALIGNMENT_REPORT.md](./CONTRACT_ALIGNMENT_REPORT.md) | 1 — Contract convergence |
| Trace continuity | [TRACE_CONTINUITY_PROOF.md](./TRACE_CONTINUITY_PROOF.md) | 2 — Trace convergence |
| Replay & provenance | [REPLAY_PROOF_REPORT.md](./REPLAY_PROOF_REPORT.md) | 4 — Replay hardening |
| Authority boundaries | [AUTHORITY_MATRIX_V2.md](./AUTHORITY_MATRIX_V2.md) | 5 — TANTRA participation |
| End-to-end proof | [TANTRA_CONVERGENCE_PROOF.md](./TANTRA_CONVERGENCE_PROOF.md) | 6 — Live API evidence |
| Handover | [NYAI_CONVERGENCE_HANDOVER.md](./NYAI_CONVERGENCE_HANDOVER.md) | 8 — Developer handover |
| Post-sprint audit | [CONVERGENCE_AUDIT_REPORT.md](./CONVERGENCE_AUDIT_REPORT.md) | Audit sign-off |

---

## Runtime Evidence (Phase 6)

Captured 11 June 2026 · example `trace_id`: `f5618054-e78a-4815-9aaf-553c477d5208`

| File | Endpoint | Description |
|------|----------|-------------|
| [tantra_flow_proof.json](./tantra_flow_proof.json) | `POST /nyaya/tantra_flow` | Full TANTRA flow capture (`flow_status: PASS`) |
| [trace_replay_proof.json](./trace_replay_proof.json) | `GET /nyaya/trace/{trace_id}` | Trace replay with non-empty `event_chain` |
| [output_proof.json](./output_proof.json) | `GET /nyaya/output/{trace_id}` | Output bucket verification |

> **Note:** On Windows, use port **8001** if 8000 is blocked: `uvicorn api.main:app --reload --port 8001`

---

## Quick Verification

```bash
cd backend && pytest tests/test_tantra_convergence.py -v
cd backend && uvicorn api.main:app --reload --port 8000
curl -s -X POST http://localhost:8000/nyaya/tantra_flow \
  -H "Content-Type: application/json" \
  -d '{"query":"theft of mobile phone","jurisdiction_hint":"India","user_context":{"role":"citizen","confidence_required":true}}'
```
