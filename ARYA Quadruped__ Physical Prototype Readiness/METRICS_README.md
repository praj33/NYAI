# METRICS_README.md
## NYAI In-Memory Metrics Endpoint
**Endpoint:** `GET /metrics` (no API key required)  
**Module:** `backend/api/metrics.py`

---

## Purpose

The `/metrics` endpoint exposes thread-safe, in-memory operational counters and latency samples for the NYAI API gateway. Metrics reset on process restart; there is no persistence or reset API in this sprint.

**Recommended scrape/poll frequency:** every **30 seconds**.

---

## Metrics Reference

| Metric | Type | Description |
|--------|------|-------------|
| `service` | metadata | Always `nyaya-api-gateway` |
| `started_at` | metadata | ISO8601 process start timestamp |
| `uptime_seconds` | gauge | Seconds since `started_at` |
| `requests.total` | counter | Total requests to `/nyaya/*` |
| `requests.errors_5xx` | counter | 5xx responses on `/nyaya/*` |
| `requests.errors_4xx` | counter | 4xx responses on `/nyaya/*` |
| `requests.rate_limited` | counter | 429 responses |
| `requests.auth_failures` | counter | 401 responses |
| `requests.validation_errors` | counter | 422 responses |
| `latency.average_ms` | gauge | Mean of last ≤1000 `/nyaya/query` durations |
| `latency.samples_window` | metadata | Window size (1000) |
| `active_requests` | gauge | In-flight requests across middleware |

---

## Alerting Thresholds (Recommended)

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Error rate | `errors_5xx / total > 5%` over 5 min | Page on-call |
| Auth failures spike | `auth_failures` > 50/min per instance | Check key rotation / abuse |
| Rate limiting | `rate_limited` sustained > 10% of traffic | Review limits or scale |
| Latency | `average_ms` > 3000 for 5 min | Investigate retrieval/LLM |
| Readiness | `/health/ready` status `unavailable` | Block traffic at LB |

---

## Reset Behavior

Metrics reset **only on process restart**. No admin reset endpoint exists in this sprint.

---

## Error Classification Map

| Error Code | Trigger | HTTP Status |
|---|---|---|
| `SCHEMA_VALIDATION_ERROR` | Observer rejects response schema | 500 |
| `TRACE_CONTINUITY_ERROR` | trace_id mutated mid-pipeline | 500 |
| `HASH_MISMATCH_ERROR` | Ledger hash tamper detected | 500 |
| `DEPENDENCY_FAILURE` | Retriever/bucket/ledger unavailable | 503 |
| `RATE_LIMIT_EXCEEDED` | Per-IP limit exceeded | 429 |
| `UNAUTHORIZED` | Missing API key header | 401 |
| `INVALID_API_KEY` | Wrong API key value | 401 |
| `AUTH_CONFIGURATION_ERROR` | NYAI_API_KEY env var not set | 503 |
| `VALIDATION_ERROR` | Pydantic schema rejection | 422 |
| `NOT_FOUND` | trace_id not in bucket | 404 |
| `INTERNAL_ERROR` | Unhandled exception | 500 |

---

## Future: Prometheus / Grafana Integration

This sprint uses JSON polling. A future sprint can:

1. Add `prometheus_client` and expose `/metrics` in Prometheus text format.
2. Map counters to `nyai_requests_total{status="..."}` histograms.
3. Scrape via Prometheus Operator `ServiceMonitor` every 30s.
4. Dashboard: request rate, p95 latency, auth failure rate, readiness status.

---

## Example

```bash
curl -s http://localhost:8000/metrics | jq .
```
