# Future Extensibility

## Redis Integration

| Component | Redis Pattern |
|-----------|---------------|
| OutputBucket `_index` | `HSET evidence:index trace_id → line_number` |
| Rate limiter | Sorted set sliding window per IP |
| response_cache L1 | Redis LRU with 500-entry cap |

## Distributed Storage

- Migrate `nyai_output_log.jsonl` to S3/GCS with date-prefix sharding (`2026/06/23/`)
- `EvidenceRepository` becomes storage-backend agnostic via interface
- Cross-region replication for disaster recovery

## Evidence Versioning

- Bump `EVIDENCE_FORMAT_VERSION` for schema additions
- `from_stored_entry()` handles v1 → v2 field mapping
- Old entries remain readable; new fields default to empty

## Governance Console

- Poll `GET /evidence/search?recommendation=ESCALATE&limit=50`
- Subscribe to webhook on new ESCALATE evidence (future)
- Display `integrity_status` badges (VERIFIED / TAMPERED)

## Replay Center

- File watcher on OutputBucket writes → real-time evidence stream
- WebSocket fan-out to audit dashboards
- `compare_evidence()` batch jobs for determinism regression

## Intentionally Disconnected

These modules remain **out of scope** until constitutional review:

- `governed_execution`
- `raj_adapter`
- `sovereign_agents`

No reconnection in Phase IV. Evidence infrastructure is advisory-only.
