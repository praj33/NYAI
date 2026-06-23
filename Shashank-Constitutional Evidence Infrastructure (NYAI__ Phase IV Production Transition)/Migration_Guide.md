# Migration Guide — Phase IV Evidence Infrastructure

## Before

- **L1 only**: `response_cache` (OrderedDict, max 500 entries)
- Secondary endpoints (`/case_summary`, `/legal_routes`, `/timeline`, `/glossary`, `/recommendation_status`) returned **404 after server restart**
- No canonical evidence object or evidence API
- OutputBucket index used sequential count (O(n) linear scan)

## After

- **L1**: `response_cache` — unchanged, write-through on every `/query`
- **L2**: `EvidenceRepository` — persistent fallback from OutputBucket JSONL
- Secondary endpoints fall back to `evidence_repository.get_raw_by_trace_id()` when cache misses
- **No URL changes** for existing `/nyaya/*` consumers
- **320+ existing entries** in `output_logs/nyai_output_log.jsonl` are immediately accessible — no migration script required

## Consumer Impact

| Consumer | Action Required |
|----------|----------------|
| Frontend (`nyayaApi.js`) | None — `/nyaya/*` contract unchanged |
| `/nyaya/case_summary` etc. | None — now survives restart via L2 fallback |
| New evidence consumers | Add `X-API-Key` header, use `/evidence/*` endpoints |

## Deployment Steps

1. Deploy backend with Phase IV code
2. Verify `GET /health/ready` shows `evidence_repository: PASS`
3. Spot-check `GET /evidence/search?limit=3` with API key
4. Confirm existing trace_ids resolve via `/evidence/{trace_id}`

## Future Path

| Layer | Upgrade |
|-------|---------|
| L1 cache | Redis with TTL |
| L2 storage | S3/GCS JSONL with date-prefix sharding |
| Index | Redis HASH replacing in-memory `_index` dict |
