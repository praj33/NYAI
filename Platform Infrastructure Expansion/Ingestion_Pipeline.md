# Ingestion Pipeline — Phase V

Source: `backend/ingestion/`. Governed ingestion — **no automatic publication**.
Every ingested asset is registered in the PENDING/DRAFT posture and stays there
until explicitly promoted.

## 1. Pipeline stages

`KnowledgeIngestionPipeline.ingest()` runs:

1. **Document registration** — assign `asset_id`, version 1 (for new assets).
2. **Metadata extraction** — `extract_metadata()` → `KnowledgeMetadata`.
3. **Schema validation** — `validate_schema()` (fail closed).
4. **Duplicate detection** — content-hash comparison against existing assets.
5. **Version comparison** — when `existing_asset_id` is supplied, diff against
   the latest version and create a new version (`INGEST_UPDATE`).
6. **Approval status assignment** — always `PENDING` at ingestion.
7. **Ingestion logging** — append an `IngestionLogEntry`.
8. **Evidence record** — `record_knowledge_operation("INGEST_NEW" | "INGEST_UPDATE", ...)`
   in addition to the repository's `REGISTER`/`UPDATE` evidence.

## 2. Schema validation rules

Required fields on every document (non-empty):

| Field | Type |
|-------|------|
| `title` | non-empty string |
| `jurisdiction` | non-empty string |
| `domain` | non-empty string |
| `source_attribution` | non-empty string |
| `content` | non-empty object (dict) |

`validate_schema()` returns a list of human-readable errors; an empty list means
valid. The pipeline rejects with `operation="SCHEMA_REJECTED"`,
`status="REJECTED"` and a `rejection_reason` naming the offending field(s).

## 3. Duplicate detection algorithm

`content_hash = sha256(json.dumps(content, sort_keys=True))`. The pipeline scans
existing latest-version assets; if an identical hash is found and no
`existing_asset_id` was supplied, it rejects with `DUPLICATE_REJECTED` and
reports `duplicate_of`. Because the hash is a pure function, the same content
always collides regardless of actor (see `test_determinism_knowledge.py`).

## 4. Version comparison output

`compare_versions(asset_id, new_content)`:

```json
{"comparable": true, "identical": false,
 "added": ["b"], "removed": [], "changed": ["a"],
 "differences": [{"field": "a", "change": "modified", "old": 1, "new": 2},
                 {"field": "b", "change": "added", "new": 3}],
 "summary": "1 added, 0 removed, 1 modified"}
```

## 5. `IngestionLogEntry` schema

`log_id`, `asset_id`, `version_id`, `actor`,
`operation` ∈ {INGEST_NEW, INGEST_UPDATE, DUPLICATE_REJECTED, SCHEMA_REJECTED},
`status` ∈ {SUCCESS, REJECTED}, `content_hash`, `evidence_trace_id`,
`rejection_reason?`, `timestamp`. Persisted append-only at
`backend/ingestion_logs/ingestion_log.jsonl` (overridable via
`INGESTION_LOG_DIRECTORY`).

## 6. Approval status flow

Ingestion never approves. New assets carry `governance.approval_status="PENDING"`
(treated as `DRAFT` by the promotion state machine). Promotion is a separate,
explicit, governed action (`Promotion_Pipeline.md`).

## 7. Evidence record format

The ingestion-level evidence record is a full TANTRA-canonical record with
`knowledge_operation="INGEST_NEW"` (or `INGEST_UPDATE"`),
`recommendation.type="INFORM"`, jurisdiction/domain from the document metadata,
and `determinism_proof.version="3.0.0"`. Its `trace_id` is returned as
`IngestionResult.trace_id` and recorded on the `IngestionLogEntry`.

## 8. `IngestionResult`

`status`, `operation`, `log_id`, `asset_id?`, `version_id?`, `trace_id?`
(evidence), `content_hash?`, `rejection_reason?`, `duplicate_of?`, `diff?`.

## 9. API

`POST /knowledge/ingest`, `GET /knowledge/ingestion/{log_id}`,
`GET /knowledge/ingestion`.
