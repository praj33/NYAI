# Phase IV Architecture — Constitutional Evidence Infrastructure

**Status:** Complete (23 June 2026)  
**Tests:** 34/34 PASS (13 evidence · 15 production · 6 convergence)

> **BHIV onboarding:** Entry Points, Flow, Files, Testing, Failure Modes, and Evidence are in the authoritative [`REVIEW_PACKET.md`](../REVIEW_PACKET.md) at project root. This document covers architecture depth only.

## Before vs After

### Before (Phase II)
```
HTTP Request → query_legal() → NyayaResponse → response_cache (L1, volatile)
                                      ↓
                              output_bucket.store() (append-only, durable)
```

Secondary endpoints (`/case_summary`, `/timeline`, etc.) read **only** from `response_cache`. After restart, cache is empty → **404**.

### After (Phase IV)
```
HTTP Request → query_legal() → NyayaResponse → response_cache (L1 write-through)
                                      ↓
                              output_bucket.store() (durable JSONL)
                                      ↓
                         FileSystemBackend → EvidenceRepository
                                      ↓
                              EvidencePackage (canonical evidence object)
                                      ↓
        ┌─────────────────────────────┼─────────────────────────────┐
        ↓                             ↓                             ↓
  evidence_service              replay_service              verification_service
        ↓                             ↓                             ↓
  /evidence/* API            compare_evidence            verify + verify/chain
  Search/Export              Replay variants             hash chain audit
```

Evidence is the **primary architectural product**. Every query execution is reconstructable as a permanent `EvidencePackage`.

## Layered Architecture

| Layer | Modules | Responsibility |
|-------|---------|----------------|
| **API** | `api/evidence_router.py` | Thin orchestration — delegates to services only |
| **Services** | `evidence_service.py`, `replay_service.py`, `verification_service.py` | Business logic boundary for evidence operations |
| **Domain** | `evidence/models.py`, `replay_engine.py`, `integrity.py`, `search.py`, `exporter.py` | Canonical model, replay, integrity, search, export |
| **Persistence** | `evidence/repository.py`, `evidence/storage_backend.py` | Read/search over durable storage via `FileSystemBackend` |
| **Storage** | `tantra/output_bucket.py` | Append-only JSONL with O(1) line-number index |

## Component Map

| Module | Role |
|--------|------|
| `evidence/models.py` | Canonical `EvidencePackage` datamodel (`evidence_v1`) |
| `evidence/storage_backend.py` | `EvidenceStorageBackend` Protocol; `FileSystemBackend` (live); Redis/S3 stubs |
| `evidence/repository.py` | Read/search layer; date-range, version, ledger cross-reference |
| `evidence/integrity.py` | Entry hash verification + ledger chain check |
| `evidence/replay_engine.py` | Reconstruct evidence by trace, hash, recommendation, jurisdiction, statute |
| `evidence/search.py` | Multi-filter search with pagination |
| `evidence/exporter.py` | JSON and summary export formats |
| `services/evidence_service.py` | API orchestration + `resolve_cached_response()` L2 helper |
| `services/replay_service.py` | Replay and compare operations |
| `services/verification_service.py` | Integrity and chain verification |
| `api/evidence_router.py` | REST API at `/evidence/*` (12 routes, auth required) |
| `services/query_executor.py` | Shared ThreadPoolExecutor pools for hybrid retrieval and reranking |

## Data Flow

1. **HTTP Request** arrives at `POST /nyaya/query` (unchanged contract).
2. **`query_legal()`** runs the deterministic pipeline (unchanged semantics).
3. **`output_bucket.store()`** appends a JSONL entry with `entry_hash`, hashes, and `full_response`.
4. **`EvidenceRepository`** (via `FileSystemBackend`) wraps stored entries as `EvidencePackage` via `from_stored_entry()`.
5. **`evidence_router`** delegates to services; no direct domain imports in route handlers.
6. **`/evidence/*` API** exposes search, replay, verify, compare, and export without re-running legal reasoning.

## Secondary Endpoint L2 Fallback

```
GET /nyaya/case_summary?trace_id=
  → resolve_cached_response(trace_id, response_cache)
      → L1: response_cache.get()
      → L2 miss: evidence_repository.get_raw_by_trace_id()
```

Shared helper lives in `services/evidence_service.py`. Used by all five secondary read endpoints.

## Security

| Route prefix | Auth | Rate limit |
|--------------|------|------------|
| `/nyaya/*` | `X-API-Key` required | Per-IP sliding window |
| `/evidence/*` | `X-API-Key` required | Per-IP sliding window |
| `/health/*`, `/metrics`, `/docs` | Exempt | Exempt |

Enforced by `api/security.py` and `api/rate_limiter.py`. Requests without a valid key receive **401**; missing server configuration receives **503**.

## Integration Points

| System | Integration |
|--------|-------------|
| **ObserverPipeline** | `observer_steps` and `observer_validation` captured in `EvidenceReasoning` |
| **ResponseBuilder** | Full formatted response stored in `attachments.full_response` |
| **HashChainLedger** | `verification_service.verify_chain()` + `repository.get_ledger_entry_for_trace()` |
| **OutputBucket** | Source of truth; O(1) line-number index for retrieval |

## Proof Artifacts

| File | Purpose |
|------|---------|
| `smoke_test_evidence.json` | End-to-end GET + verify + search chain on a real trace_id |
| `replay_proof.json` | `ReplayEngine.replay_by_trace()` with `integrity_status` |
| `example_exported_evidence.json` | Full `POST /evidence/export` JSON response |

## What Was NOT Changed

- `api/schemas.py`, `api/response_builder.py`, `observer/pipeline.py` — protected contract files
- All `/nyaya/*` URLs, methods, and response shapes
- Recommendation semantics: INFORM / REVIEW / ESCALATE / INSUFFICIENT_DATA
- `response_cache` — retained as L1 write-through cache
- `governed_execution`, `raj_adapter`, `sovereign_agents` — intentionally disconnected
- No `enforcement_decision` anywhere in active paths
