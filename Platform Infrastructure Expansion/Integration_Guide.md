# Integration Guide — Phase V

How Phase V mounts onto the existing Phase IV runtime, and the backward-compat
guarantees.

## 1. Registering Phase V routers in `main.py`

Added at the **bottom** of `backend/api/main.py`, after all existing routers,
using the same try/except pattern as `procedure_router`:

```python
try:
    from api.knowledge_router import knowledge_router
    app.include_router(knowledge_router)
except ImportError as e:
    _phase_v_logger.warning("knowledge_router not available: %s", e)
# ... workspace_router, graph_router likewise
```

If any Phase V module fails to import, the existing API continues unaffected
(the routers simply are not mounted).

The root `GET /` endpoint's `endpoints` dict was extended with `knowledge`,
`workspace`, and `graph` sub-dicts (additive only).

## 2. Health check integration

`backend/api/health.py` gained `_check_knowledge_repository()`, added to the
`/health/ready` `dependencies` map:

```json
"knowledge_repository": {"status": "PASS", "detail": "Knowledge repository accessible (N assets stored)"}
```

It follows the existing `PASS` / `DEGRADED` / `FAIL` convention (a `DEGRADED`
status does not take readiness to 503).

> Note: the spec's illustrative snippet used `checks[...] = {"status": "ok"}`.
> The real handler uses the existing `dependencies` map with `PASS`/`DEGRADED`,
> so the Phase V check matches the established health contract rather than
> introducing a parallel `checks`/`ok` shape.

## 3. Auth & rate limiting

`/knowledge/*`, `/workspace/*`, `/graph/*` were added to `_PROTECTED_PREFIXES`
in **both** `api/security.py` and `api/rate_limiter.py`. This reuses the
existing `APIKeyAuthMiddleware` and per-IP sliding-window limiter — **no new
auth scheme**. These two files are not in the frozen set; only their prefix
tuple was extended (additive).

## 4. How `evidence_bridge.py` connects Phase V → Phase IV

`knowledge/evidence_bridge.record_knowledge_operation()`:

1. Builds a full TANTRA-canonical record (11 canonical + 4 structural + contract
   fields), `schema_version="tantra_v3"`, `recommendation.type="INFORM"`,
   `determinism_proof.version="3.0.0"`.
2. Validates it through the **frozen** `ResponseBuilder.build()` (fail closed).
3. Persists via `output_bucket.store()`.
4. Returns a fresh evidence `trace_id`.

Because storage is the same `OutputBucket`, every Phase V operation is
immediately visible through the existing `/evidence/*` API (get, search, verify,
replay, compare, export).

## 5. Environment variables (all optional, sensible defaults)

| Variable | Default | Purpose |
|----------|---------|---------|
| `KNOWLEDGE_STORE_DIRECTORY` | `backend/knowledge_store` | Asset + graph JSONL store |
| `INGESTION_LOG_DIRECTORY` | `backend/ingestion_logs` | Ingestion audit log |
| `PROMOTION_LOG_DIRECTORY` | `backend/promotion_logs` | Approval log |
| `WORKSPACE_STORE_DIRECTORY` | `backend/workspace_store` | Documents + annotations |

No **new required** variables. `NYAI_API_KEY` (Phase IV) now also gates the
Phase V routes.

## 6. Backward-compatibility guarantees

- No existing endpoint URL changed; new routers mount after existing ones.
- Frozen files untouched except the explicitly-allowed additive edits to
  `api/main.py` (router registration + root dict) and `api/health.py` (new
  readiness check).
- 35/35 Phase IV tests (evidence infrastructure 14, production hardening 15,
  TANTRA convergence 6) still pass alongside the 66 new Phase V tests
  (**101/101** total when run together).
- `/nyaya/query`, `/evidence/{trace_id}`, `/evidence/verify` behave identically.

## 7. Migration notes for existing deployments

- No schema migration required; Phase V uses new directories created on first
  use. Existing `output_logs` gains additional INFORM-type evidence records for
  knowledge operations — fully compatible with existing readers.
- To roll Phase V back, remove the three router-registration blocks from
  `main.py`; the platform reverts to Phase IV behaviour with no data loss.
