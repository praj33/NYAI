# Evidence API Reference

> **BHIV onboarding:** See [`REVIEW_PACKET.md`](../REVIEW_PACKET.md) sections 1 (Entry Points), 4 (Testing), 5 (Failure Modes), 6 (Evidence).

Base path: `/evidence`  
Auth: **Required** — `X-API-Key` header (same fail-closed behavior as `/nyaya/*`)  
Rate limit: Per-IP sliding window (same as `/nyaya/*`)

Unauthenticated requests return **401** with `error_code: UNAUTHORIZED`.

## Endpoint Table

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/evidence/{trace_id}` | Yes | Full EvidencePackage by trace_id |
| GET | `/evidence/search` | Yes | Multi-filter search with pagination |
| GET | `/evidence/hash/{input_hash}` | Yes | Lookup by input hash |
| GET | `/evidence/recommendation/{rec_type}` | Yes | List evidence by recommendation type |
| GET | `/evidence/jurisdiction/{country}` | Yes | List evidence by jurisdiction |
| GET | `/evidence/statute?keyword=` | Yes | Search by statute keyword |
| GET | `/evidence/version/{evidence_version}` | Yes | List evidence by format version (e.g. `1.0.0`) |
| POST | `/evidence/verify` | Yes | Verify entry integrity by trace_id |
| POST | `/evidence/verify/chain` | Yes | Verify hash chain ledger |
| POST | `/evidence/compare` | Yes | Compare two evidence packages for determinism |
| POST | `/evidence/export` | Yes | Export JSON or summary |

**Total: 12 routes** (11 specific + 1 catch-all `GET /{trace_id}`)

## Endpoints Detail

### GET /evidence/{trace_id}
Returns canonical `EvidencePackage` JSON.

**404**: `{"error_code": "EVIDENCE_NOT_FOUND", "trace_id": "..."}`

### GET /evidence/search
Query params:

| Param | Type | Description |
|-------|------|-------------|
| `recommendation` | string | INFORM / REVIEW / ESCALATE / INSUFFICIENT_DATA |
| `jurisdiction` | string | Jurisdiction substring match |
| `statute` | string | Statute keyword |
| `input_hash` | string | Exact input hash lookup |
| `date_from` | string | ISO date lower bound (inclusive) |
| `date_to` | string | ISO date upper bound (inclusive) |
| `evidence_version` | string | Format version filter (e.g. `1.0.0`) |
| `limit` | int | 1–100 (default 20) |
| `offset` | int | Pagination offset (default 0) |

```json
{
  "total": 42,
  "limit": 20,
  "offset": 0,
  "results": [
    {
      "trace_id": "...",
      "evidence_id": "...",
      "recommendation_type": "INFORM",
      "jurisdiction": "IN",
      "domain": "criminal",
      "input_hash": "...",
      "created_at": "...",
      "integrity_status": "UNVERIFIED",
      "evidence_version": "1.0.0"
    }
  ]
}
```

### GET /evidence/recommendation/{rec_type}
Valid types: `INFORM`, `REVIEW`, `ESCALATE`, `INSUFFICIENT_DATA`

**400**: `{"error_code": "INVALID_RECOMMENDATION_TYPE", "valid": [...]}`

### GET /evidence/version/{evidence_version}
Lists evidence packages matching `identity.evidence_version` (currently `1.0.0`).

### POST /evidence/verify
Body: `{"trace_id": "..."}`

```json
{
  "verified": true,
  "trace_id": "...",
  "integrity_status": "VERIFIED",
  "tamper_detected": false
}
```

### POST /evidence/compare
Body: `{"trace_id_a": "...", "trace_id_b": "..."}`

```json
{
  "compared": true,
  "trace_id_a": "...",
  "trace_id_b": "...",
  "same_input_hash": false,
  "same_output_hash": false,
  "same_recommendation": true,
  "deterministic": false,
  "evidence_a_id": "...",
  "evidence_b_id": "..."
}
```

### POST /evidence/export
Body: `{"trace_id": "...", "format": "json"}` or `"summary"`

JSON format response:
```json
{
  "export_format": "nyai_evidence_v1",
  "exported_at": "2026-06-23T...",
  "evidence": { ... }
}
```

See `example_exported_evidence.json` in this folder for a full live export.

## Error Codes

| Code | HTTP | Meaning |
|------|------|---------|
| `UNAUTHORIZED` | 401 | Missing or empty `X-API-Key` |
| `INVALID_API_KEY` | 401 | Key does not match `NYAI_API_KEY` |
| `EVIDENCE_NOT_FOUND` | 404 | No evidence for trace_id or input_hash |
| `INVALID_RECOMMENDATION_TYPE` | 400 | Unknown recommendation filter |
| `RATE_LIMIT_EXCEEDED` | 429 | Per-IP limit exceeded |

## Distinction from `/nyaya/trace/*` and `/nyaya/output/*`

| Endpoint family | Returns | Re-runs pipeline? |
|-----------------|---------|-------------------|
| `/nyaya/trace/{id}` | Observer event chain + tamper flag | No |
| `/nyaya/output/{id}` | Raw stored output + hash proof | No |
| `/evidence/{id}` | Canonical `EvidencePackage` | No |
| `/evidence/search` | Filtered evidence index | No |

## Downstream Consumers

| System | Usage |
|--------|-------|
| **Governance Console** | Poll `/evidence/search?recommendation=ESCALATE` for review queue |
| **InsightFlow** | Export via `/evidence/export` for analytics pipelines |
| **Audit Tools** | `/evidence/verify` + `/evidence/verify/chain` for tamper proofs |
| **Replay Center** | `/evidence/compare` for determinism regression checks |

## Route Ordering

Specific routes (`/search`, `/hash/`, `/recommendation/`, `/version/`, etc.) are registered **before** the catch-all `GET /{trace_id}` to prevent FastAPI from treating `search` or `version` as a trace_id.

## Example Requests

```bash
# Retrieve evidence (auth required)
curl -H "X-API-Key: $NYAI_API_KEY" http://localhost:8000/evidence/{trace_id}

# Search by date range and version
curl -H "X-API-Key: $NYAI_API_KEY" \
  "http://localhost:8000/evidence/search?date_from=2026-06-01&date_to=2026-06-30&evidence_version=1.0.0"

# Compare two traces
curl -X POST -H "X-API-Key: $NYAI_API_KEY" -H "Content-Type: application/json" \
  -d '{"trace_id_a":"...","trace_id_b":"..."}' \
  http://localhost:8000/evidence/compare
```
