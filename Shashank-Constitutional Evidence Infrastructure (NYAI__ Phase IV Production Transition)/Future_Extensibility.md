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

Phase IV exposes read-only evidence APIs that a Governance Console can poll without modifying NYAI behavior:

- **Review queue poll:** `GET /evidence/search?recommendation=ESCALATE&limit=50`
- **Optional filters:** `date_from`, `date_to`, `jurisdiction`, `evidence_version`, `integrity_status`
- **Per-item drill-down:** `GET /evidence/{trace_id}` for the canonical `EvidencePackage`
- **Integrity check:** `POST /evidence/verify` with `{"trace_id": "..."}` before escalation
- **Badge mapping:** display `integrity_status` as `VERIFIED` (green), `TAMPERED` (red), `UNVERIFIED` (grey)
- **Chain audit:** `GET /evidence/verify/chain/{trace_id}` for provenance ledger cross-reference
- **Future webhook:** subscribe to new ESCALATE evidence on bucket append (not implemented in Phase IV)
- **Advisory-only:** Governance Console must not transfer enforcement authority or mutate stored evidence

## Replay Center

Phase IV provides replay and compare hooks; real-time streaming is a future extension:

- **Current replay API:** `POST /evidence/replay/{trace_id}` reconstructs evidence from OutputBucket (no pipeline re-execution)
- **Determinism compare:** `POST /evidence/compare` with `trace_id_a` / `trace_id_b` returns `same_input_hash`, `same_output_hash`, `deterministic`
- **Batch regression:** run `compare_evidence()` across trace pairs after model or ruleset changes
- **Replay variants:** `replay_by_input_hash`, `replay_by_recommendation`, `replay_by_jurisdiction`, `replay_by_statute` (see `Replay_Architecture.md`)
- **TAMPERED fail-open:** replay still returns stored evidence with `tamper_detected: true` for audit visibility
- **Future file watcher:** monitor `nyai_output_log.jsonl` appends → real-time evidence stream
- **Future WebSocket fan-out:** push new evidence events to audit dashboards
- **Does not:** re-run `POST /nyaya/query`, modify bucket entries, or change recommendation semantics

## Intentionally Disconnected

These modules remain **out of scope** until constitutional review:

- `governed_execution`
- `raj_adapter`
- `sovereign_agents`

No reconnection in Phase IV. Evidence infrastructure is advisory-only.
