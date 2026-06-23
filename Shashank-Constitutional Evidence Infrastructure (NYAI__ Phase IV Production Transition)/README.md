# Phase IV Deliverables — Constitutional Evidence Infrastructure

**Sprint:** NYAI Phase IV Production Transition  
**Date:** 23 June 2026  
**Status:** COMPLETE — 34/34 tests PASS

> **Authoritative onboarding document:** [`../REVIEW_PACKET.md`](../REVIEW_PACKET.md) (project root)  
> Per BHIV protocol, every submission must include Entry Points, Flow, Files, Testing, Failure Modes, and Evidence. All six sections are in the root review packet.

---

## Document Index

| Document | Purpose |
|----------|---------|
| [`Architecture.md`](./Architecture.md) | Before/after architecture, component map, security, integration points |
| [`Evidence_Model.md`](./Evidence_Model.md) | `EvidencePackage` dataclasses, field mapping, JSON example |
| [`Evidence_API.md`](./Evidence_API.md) | All 12 `/evidence/*` routes, auth, error codes, curl examples |
| [`Replay_Architecture.md`](./Replay_Architecture.md) | Replay definition, variants, compare, TAMPERED behavior |
| [`Migration_Guide.md`](./Migration_Guide.md) | L1/L2 cache migration, consumer impact, deployment steps |
| [`Future_Extensibility.md`](./Future_Extensibility.md) | Redis, S3, versioning, Governance Console integration paths |

## Proof Artifacts (Evidence)

| File | What it proves |
|------|----------------|
| [`smoke_test_evidence.json`](./smoke_test_evidence.json) | Live trace_id → GET evidence → verify → search (200 chain) |
| [`replay_proof.json`](./replay_proof.json) | `ReplayEngine.replay_by_trace()` with `integrity_status: VERIFIED` |
| [`example_exported_evidence.json`](./example_exported_evidence.json) | Full `POST /evidence/export` `format=json` response |

## Quick Start

```bash
cd backend
export NYAI_API_KEY=your-key          # required for /nyaya/* and /evidence/*
uvicorn api.main:app --reload --port 8000

# Run all sprint tests
pytest tests/test_evidence_infrastructure.py tests/test_production_hardening.py tests/test_tantra_convergence.py -v
```

## Prior Sprint Artifacts

TANTRA convergence proofs remain in [`../SHASHANK-NYAI_CONVERGENCE_IMPLEMENTATION_PLAN/`](../SHASHANK-NYAI_CONVERGENCE_IMPLEMENTATION_PLAN/).
