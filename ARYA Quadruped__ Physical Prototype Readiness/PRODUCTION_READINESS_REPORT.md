# PRODUCTION_READINESS_REPORT.md
## NYAI — Production Candidate Readiness
**Sprint:** ARYA Quadruped Physical Prototype Readiness  
**Date:** 18 June 2026  
**Status:** **Production Candidate Ready**

---

## 1. Executive Summary

NYAI has been hardened from **TANTRA-Convergence Ready** to **Production Candidate Ready** by adding infrastructure around the existing legal pipeline — not inside it.

**What changed:**
- API key authentication on `/nyaya/*`
- Per-IP sliding-window rate limiting
- Three-tier health endpoints (`/health`, `/health/live`, `/health/ready`)
- Structured JSON access logging with `trace_id`
- In-memory metrics endpoint (`/metrics`)
- 8 new hard-failing production tests (14 total with convergence suite)

**What did NOT change:**
- Recommendation semantics (`INFORM / REVIEW / ESCALATE / INSUFFICIENT_DATA`)
- `trace_id` lifecycle and middleware propagation
- `router.py`, `response_builder.py`, `schemas.py`, `observer/pipeline.py`
- `tantra/flow.py`, `output_bucket.py`, `sovereign_core_mock.py`
- `governed_execution`, `raj_adapter`, `sovereign_agents` remain disconnected
- No `enforcement_decision` anywhere in active API paths

---

## 2. Architecture Summary

### Middleware Stack (request path, outer → inner)

```
Client
  → CORS (CORSMiddleware)
  → TraceIdMiddleware (uuid4 → request.state.trace_id)
  → StructuredLoggingMiddleware (JSON NDJSON per request)
  → RateLimiterMiddleware (/nyaya/* only)
  → APIKeyAuthMiddleware (/nyaya/* only)
  → Route handlers
```

### Request Flow

1. CORS preflight/headers applied.
2. `trace_id` assigned to `request.state`.
3. Structured logger records start time.
4. Rate limiter enforces per-IP sliding window.
5. Auth validates `X-API-Key` via `hmac.compare_digest` (fail-closed).
6. Existing NYAI pipeline executes unchanged.
7. Structured logger emits JSON line with `trace_id`, `duration_ms`, `status_code`.

---

## 3. Security Controls

### API Key Authentication
- **Protected:** `/nyaya/*`
- **Exempt:** `/health`, `/health/live`, `/health/ready`, `/metrics`, `/docs`, `/redoc`, `/`
- **Key source:** `NYAI_API_KEY` environment variable
- **Comparison:** `hmac.compare_digest()` (timing-attack safe)
- **Missing key:** HTTP 503 `AUTH_CONFIGURATION_ERROR` (fail-closed)

### Rate Limiting
- **Algorithm:** Stdlib sliding window (`collections.deque`, `threading.Lock`)
- **Default:** 60 requests/IP/60s (`RATE_LIMIT_PER_MINUTE`)
- **Response:** HTTP 429 + `Retry-After` + `RATE_LIMIT_EXCEEDED`

### Abuse Resistance
- Timing-safe key comparison
- Pydantic validation on all request bodies (no raw SQL paths in API layer)
- Rate limiting before auth gate (abuse blocked before key validation)

---

## 4. Health Monitoring

| Endpoint | Purpose | Target |
|----------|---------|--------|
| `GET /health` | Basic liveness | <50ms, always 200 if process alive |
| `GET /health/live` | K8s liveness probe | Same as `/health` |
| `GET /health/ready` | Readiness + dependency checks | 200 ready/degraded; 503 unavailable |

**Dependency checks:** `output_bucket`, `ledger`, `retriever` (advisor), `model` (GROQ_API_KEY).

**Kubernetes recommendation:**
- Liveness: `GET /health/live` every 10s
- Readiness: `GET /health/ready` every 15s; remove from LB on 503

---

## 5. Telemetry

### Structured Logging
- Logger: `nyai.access`
- Format: one JSON object per line (NDJSON) on stderr
- Required fields: `timestamp`, `trace_id`, `request_id`, `endpoint`, `method`, `status_code`, `duration_ms`, `client_ip`, `error_code`, `log_level`

### Metrics
See [`METRICS_README.md`](./METRICS_README.md) for full counter definitions and error classification map.

---

## 6. Known Risks

| Risk | Status |
|------|--------|
| SovereignCoreMock in-memory, restart-unsafe | **Deferred** — future sprint |
| Local provenance only (`provenance_ledger.json`) | **Deferred** |
| No load/stress testing | **Deferred** |
| Independent third-party verification | **Deferred** |
| CORS wildcard if `FRONTEND_URL` unset | **Mitigate** — set in production |
| BM25 index startup ~8–12s | **Documented** |
| Governed modules disconnected | **Intentional** |
| In-memory metrics (no Prometheus yet) | **This sprint scope** |

---

## 7. Deployment Requirements

| Requirement | Value |
|-------------|-------|
| Python | 3.10+ |
| Start command | `cd backend && uvicorn api.main:app --host 0.0.0.0 --port 8000` |
| Required env | `NYAI_API_KEY`, `RATE_LIMIT_PER_MINUTE`, `GROQ_API_KEY` (optional, degraded without) |
| Pip packages | `requirements.txt` including `slowapi`, `python-json-logger` |

---

## 8. Rollback Procedure

1. Revert `main.py` to pre-sprint version.
2. Remove `security.py`, `rate_limiter.py`, `health.py`, `structured_logger.py`, `metrics.py`, `trace_middleware.py`.
3. Restart server.
4. Verify `POST /nyaya/query` responds without auth header.

No data loss — `router.py` and data files unchanged.

---

## 9. Operational Runbook

### Rotate API Key
1. Generate new key.
2. Update `NYAI_API_KEY` in deployment env.
3. Rolling restart instances.
4. Revoke old key from clients.

### Adjust Rate Limits
1. Set `RATE_LIMIT_PER_MINUTE` (and optionally `RATE_LIMIT_BURST` for future use).
2. Restart process.

### `/health/ready` Returns DEGRADED
- Check `dependencies` block for `DEGRADED` entries.
- `model: DEGRADED` → set `GROQ_API_KEY`.
- `retriever: DEGRADED` → check advisor initialization logs.

### Auth Failures Spike
```bash
# Grep structured logs for auth failures
grep '"error_code": "INVALID_API_KEY"' <container-logs>
grep '"error_code": "UNAUTHORIZED"' <container-logs>
```

### Verify a Trace Manually
```bash
curl -H "X-API-Key: $NYAI_API_KEY" http://localhost:8000/nyaya/trace/{trace_id}
curl -H "X-API-Key: $NYAI_API_KEY" http://localhost:8000/nyaya/output/{trace_id}
```
