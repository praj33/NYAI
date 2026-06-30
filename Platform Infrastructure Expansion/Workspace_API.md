# Workspace & Knowledge API — Phase V

All routes require the `X-API-Key` header (enforced by the existing
`APIKeyAuthMiddleware`, extended to cover `/knowledge/*`, `/workspace/*`,
`/graph/*`). Missing/invalid key → 401.

## 1. Workspace endpoints (`/workspace/*`)

| Method | Path | Body | Response |
|--------|------|------|----------|
| POST | `/workspace/documents/upload` | `{asset_id, filename, content, content_type?, metadata?, uploaded_by?}` | `WorkspaceDocument` |
| PATCH | `/workspace/documents/{doc_id}/metadata` | `{metadata, actor}` | `WorkspaceDocument` (new version) |
| POST | `/workspace/annotations` | `{doc_id, asset_id, annotation_type, content, author}` | `Annotation` |
| GET | `/workspace/documents/{doc_id}/annotations` | — | `List[Annotation]` |
| GET | `/workspace/documents/{asset_id}/versions` | — | `List[WorkspaceDocument]` |
| GET | `/workspace/documents/{doc_id_a}/compare/{doc_id_b}` | — | `{differences, summary, identical}` |
| GET | `/workspace/documents/{doc_id}/audit` | — | `List[audit_event]` |

`content` is **required** on upload; omitting it → 422.

### `WorkspaceDocument`
`doc_id`, `asset_id`, `version_id`, `filename`, `content_type`, `content`,
`metadata`, `uploaded_by`, `uploaded_at`, `evidence_trace_id`,
`operation` ∈ {UPLOAD, UPDATE_METADATA}.

### `Annotation`
`annotation_id`, `doc_id`, `asset_id`,
`annotation_type` ∈ {COMMENT, REVIEW_NOTE, FLAG, APPROVAL_NOTE}, `content`,
`author`, `created_at`, `evidence_trace_id`. Invalid `annotation_type` → 400.

### Version comparison output (diff structure)

```json
{"differences": [{"field": "y", "change": "modified", "old": 2, "new": 99},
                 {"field": "z", "change": "added", "new": 3}],
 "identical": false,
 "summary": {"added": 1, "removed": 0, "modified": 1, "total_changes": 2},
 "doc_id_a": "...", "doc_id_b": "..."}
```

### Audit history event types

`UPLOAD`, `UPDATE_METADATA`, `ANNOTATION` — aggregated for the asset that the
given `doc_id` belongs to, sorted by timestamp. Each event carries
`evidence_trace_id`.

## 2. Knowledge endpoints (`/knowledge/*`)

| Method | Path | Body / Query | Response |
|--------|------|--------------|----------|
| POST | `/knowledge/assets` | `RegisterAssetRequest` (title required) | `{asset_id, version_id, trace_id, version_number}` |
| GET | `/knowledge/assets/{asset_id}` | — | `KnowledgeAsset` (404 if missing) |
| GET | `/knowledge/assets/{asset_id}/versions` | — | `List[KnowledgeAsset]` |
| GET | `/knowledge/assets/{asset_id}/versions/{version_id}` | — | `KnowledgeAsset` |
| PATCH | `/knowledge/assets/{asset_id}` | `{updates, updated_by}` | `{asset_id, new_version_id, trace_id}` |
| GET | `/knowledge/assets/{asset_id}/integrity` | — | `{verified, content_hash, status, asset_id}` |
| GET | `/knowledge/assets` | `limit, offset, jurisdiction?, domain?` | `{assets, total, limit, offset}` |
| POST | `/knowledge/ingest` | `IngestRequest` | `IngestionResult` |
| GET | `/knowledge/ingestion/{log_id}` | — | `IngestionLogEntry` |
| GET | `/knowledge/ingestion` | `limit, offset` | `{entries, total}` |
| POST | `/knowledge/assets/{asset_id}/promote` | `{target_state, actor, rationale}` | `{asset_id, from_state, to_state, record_id, evidence_trace_id}` |
| POST | `/knowledge/assets/{asset_id}/rollback` | `{target_version_id, actor, reason}` | `{asset_id, restored_version_id, new_version_id, evidence_trace_id}` |
| GET | `/knowledge/assets/{asset_id}/state` | — | `{asset_id, current_state, last_updated}` |
| GET | `/knowledge/assets/{asset_id}/approval-trail` | — | `ApprovalAuditTrail` |

## 3. Auth

Every route above is protected. The middleware is the **same** Phase IV
`APIKeyAuthMiddleware`; no new auth scheme was introduced. Routes are also
subject to the existing per-IP rate limiter.

## 4. Evidence generation per operation

Every mutating workspace/knowledge operation calls
`record_knowledge_operation()` and returns/stores the resulting evidence
`trace_id`, so each can be retrieved via `GET /evidence/{trace_id}` and verified
via `POST /evidence/verify`.

## 5. No business logic in routers

Routers validate transport input (Pydantic) and delegate to services
(`knowledge_service`, `ingestion_service`, `promotion_service`) or stores. They
only translate exceptions to HTTP codes: `KeyError → 404`, `ValueError → 400`,
Pydantic validation → 422.
