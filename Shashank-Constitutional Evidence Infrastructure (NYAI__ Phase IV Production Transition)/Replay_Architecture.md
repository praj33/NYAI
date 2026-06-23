# Replay Architecture

## Definition

**Replay** = reconstruct a constitutional evidence object from immutable OutputBucket storage. Replay does **not** re-execute the legal query pipeline or return a cached in-memory runtime response.

## replay_by_trace Flow

```
trace_id
  → EvidenceRepository.get_by_trace_id()
  → OutputBucket.retrieve() [O(1) line-index seek]
  → EvidencePackage.from_stored_entry()
  → EvidenceIntegrity.verify_by_trace_id()
  → Set integrity_status on package
  → Return {replayed: true, evidence: {...}, tamper_detected: bool}
```

## Replay Variants

| Method | Use Case |
|--------|----------|
| `replay_by_trace(trace_id)` | Full evidence reconstruction for audit |
| `replay_by_input_hash(hash)` | Determinism verification — same input → same evidence |
| `replay_by_recommendation(type)` | Governance review of ESCALATE / INSUFFICIENT_DATA cases |
| `replay_by_jurisdiction(country)` | Jurisdiction-specific evidence sampling |
| `replay_by_statute(keyword)` | Statute-linked evidence discovery (e.g. IPC, BNS) |

## compare_evidence

Compares two evidence packages by `trace_id`:

```json
{
  "compared": true,
  "same_input_hash": true,
  "same_output_hash": true,
  "same_recommendation": true,
  "deterministic": true
}
```

Used for determinism verification: identical inputs should produce identical output hashes.

## TAMPERED Behavior

When `integrity_status = TAMPERED`:

- Replay **still returns** the stored evidence (fail-open for audit visibility)
- `tamper_detected: true` is set in the replay response
- Downstream systems (Governance Console) should flag the package for investigation
- Replay does **not** block or mutate the stored data

## What Replay Does NOT Do

- Does not call `POST /nyaya/query` again
- Does not modify OutputBucket entries
- Does not transfer enforcement authority
- Does not change recommendation semantics
