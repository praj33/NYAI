# Knowledge Repository — Phase V

Source: `backend/knowledge/`. Governed, versioned, evidence-linked asset store.

## 1. `KnowledgeAsset` model

| Field | Type | Description |
|-------|------|-------------|
| `identity` | `KnowledgeIdentity` | Stable asset id + per-version id/number |
| `metadata` | `KnowledgeMetadata` | Title, jurisdiction, domain, attribution, tags |
| `content` | `Dict[str, Any]` | Opaque governed payload |
| `integrity` | `KnowledgeIntegrity` | SHA-256 content hash + status |
| `governance` | `KnowledgeGovernance` | Approval status, approver, evidence link |
| `version_history` | `List[str]` | All version_ids for this asset |
| `evidence_linkage` | `List[str]` | All evidence trace_ids for this asset |

Methods: `to_dict()`, `to_json()`, `compute_content_hash()`, `from_dict()`.

### `KnowledgeIdentity`
`asset_id` (UUID, stable across versions), `version_id` (UUID per version),
`version_number` (1-indexed), `schema_version="knowledge_v1"`,
`origin="nyai-knowledge-repository"`, `created_at`, `updated_at`.

### `KnowledgeMetadata`
`title`, `jurisdiction` (e.g. India/UK/UAE/Global), `domain`,
`source_attribution`, `tags`, `author?`, `description?`.

### `KnowledgeIntegrity`
`content_hash` (SHA-256), `integrity_status` ∈ {UNVERIFIED, VERIFIED, TAMPERED},
`verified_at?`.

### `KnowledgeGovernance`
`approval_status` ∈ {PENDING, APPROVED, REJECTED, ARCHIVED} (also DRAFT/REVIEW
via the promotion state machine), `approved_by?`, `approval_timestamp?`,
`rejection_reason?`, `replay_id`, `evidence_id?` (trace_id of the latest
evidence record).

## 2. Storage backend protocol

`KnowledgeStorageBackend` (`@runtime_checkable Protocol`):
`store`, `retrieve`, `retrieve_version`, `list_versions`, `list_all`, `count`,
`delete` (soft-delete only — history is never purged).

## 3. `FileSystemKnowledgeBackend`

- One JSONL file per `asset_id` under `backend/knowledge_store/`.
- Each line is a complete versioned asset snapshot → history is append-only and
  never overwritten.
- In-memory index `{asset_id -> [version_id, ...]}` rebuilt from disk on init.
- Thread-safe via `threading.Lock()` (mirrors `OutputBucket`).
- `retrieve()` returns the latest version (last line); `retrieve_version()`
  scans for a specific `version_id`.
- Store dir overridable via `KNOWLEDGE_STORE_DIRECTORY`.

A `RedisKnowledgeBackend` stub is included for future swap-in (see
`Future_Extensibility.md`).

## 4. Version history mechanism

- `register()` → version 1.
- `update()` → builds a **new** version (number+1, new `version_id`), preserves
  the prior version on disk, appends to `version_history`.
- `store_version()` (used by promotion/rollback) persists a caller-built version
  with its own evidence record.

## 5. Content hash computation (deterministic)

`compute_content_hash(content) = sha256(json.dumps(content, sort_keys=True))`.
A pure function — same input always yields the same hash (hash-verified).

## 6. Integrity verification

`verify_integrity(asset_id)` re-reads the stored asset from disk, recomputes the
content hash, and compares to the stored hash:

```json
{"verified": true, "content_hash": "...", "expected_hash": "...",
 "status": "VERIFIED", "asset_id": "...", "version_id": "..."}
```

A mismatch → `verified: false`, `status: "TAMPERED"`.

## 7. Evidence linkage per operation

| Repository method | Evidence operation | Canonical fields stamped |
|-------------------|--------------------|--------------------------|
| `register()` | `REGISTER` | all 11 canonical + 4 structural + `tantra_v3` |
| `update()` | `UPDATE` | same |
| `store_version()` (promotion) | `PROMOTE` | same |
| `store_version()` (rollback) | `ROLLBACK` | same |

The evidence record carries `recommendation.type="INFORM"`,
`determinism_proof.version="3.0.0"`, plus knowledge-specific fields
(`knowledge_operation`, `asset_id`, `version_id`, `content_hash`, `actor`). The
returned `trace_id` is stored on `governance.evidence_id` and appended to
`evidence_linkage`.

## 8. API (see `Workspace_API.md` for full request/response shapes)

`POST /knowledge/assets`, `GET /knowledge/assets/{id}`,
`GET /knowledge/assets/{id}/versions[/{version_id}]`,
`PATCH /knowledge/assets/{id}`, `GET /knowledge/assets/{id}/integrity`,
`GET /knowledge/assets`, plus ingestion and promotion routes.
