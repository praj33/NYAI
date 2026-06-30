# Promotion Pipeline — Phase V

Source: `backend/promotion/`. A governed state machine for knowledge-asset
lifecycle. **No autonomous promotion** — every transition requires an explicit
`actor` and `rationale`, writes an `ApprovalRecord`, and records evidence.

## 1. State machine

```
        ┌─────────┐   promote    ┌────────┐   promote    ┌──────────┐
        │  DRAFT  │ ───────────► │ REVIEW │ ───────────► │ APPROVED │
        └────┬────┘ ◄─────────── └───┬────┘              └────┬─────┘
             │        (REVIEW→DRAFT) │                        │
             │ archive               │ archive                │ archive
             ▼                       ▼                        ▼
        ┌──────────────────────────────────────────────────────┐
        │                       ARCHIVED  (terminal)            │
        └──────────────────────────────────────────────────────┘

   rollback(any) ──► appends a NEW DRAFT version (content copied from a prior
                     version; history never overwritten)
```

Newly registered/ingested assets carry `approval_status="PENDING"`, treated as
`DRAFT`.

## 2. Valid transitions

| From | Allowed `to` |
|------|--------------|
| DRAFT | REVIEW, ARCHIVED |
| REVIEW | APPROVED, DRAFT, ARCHIVED |
| APPROVED | ARCHIVED |
| ARCHIVED | *(none — terminal)* |

## 3. Invalid transitions (explicitly documented)

- `DRAFT → APPROVED` (must pass through REVIEW) → **400**.
- Any transition out of `ARCHIVED` → **400** (terminal).
- Unknown target state (e.g. `"PUBLISHED"`) → **400** (`AssetState(...)` raises
  `ValueError`).
- Missing `actor` or `rationale` → **400**.

## 4. `ApprovalRecord`

`record_id`, `asset_id`, `version_id`, `from_state`, `to_state`, `actor`,
`rationale`, `evidence_trace_id` (**mandatory**), `operation` ∈ {PROMOTE,
ROLLBACK}, `timestamp`. Persisted append-only at
`backend/promotion_logs/approval_log.jsonl` (overridable via
`PROMOTION_LOG_DIRECTORY`).

## 5. `ApprovalAuditTrail`

`{asset_id, records: [ApprovalRecord...], count}` — chronological list of all
approval/rollback records for an asset, via
`GET /knowledge/assets/{id}/approval-trail`.

## 6. Rollback mechanism

`rollback(asset_id, target_version_id, actor, reason)`:

1. Loads the current asset and the target version (404 if either missing).
2. Builds a **new** version (`version_number+1`, new `version_id`) whose content
   is copied from the target version.
3. Resets `approval_status` to `DRAFT`.
4. Persists via the repository (records `ROLLBACK` evidence).
5. Writes an `ApprovalRecord` with `operation="ROLLBACK"`.

Prior versions remain on disk — rollback **never** overwrites history.

## 7. Promotion / rollback evidence

Each `promote()` records `PROMOTE` evidence; each `rollback()` records
`ROLLBACK` evidence (both full TANTRA-canonical, `recommendation.type="INFORM"`).
The evidence `trace_id` is returned in the API response and stored on the
`ApprovalRecord`.

## 8. No-autonomous-promotion guarantee

The pipeline raises `ValueError` if `actor` or `rationale` is empty, and there is
no code path that advances state without an explicit caller request. State is
only ever changed through `promote()` / `rollback()`, both of which demand
attribution and produce an immutable audit + evidence record.

## 9. API

`POST /knowledge/assets/{id}/promote`, `POST /knowledge/assets/{id}/rollback`,
`GET /knowledge/assets/{id}/state`, `GET /knowledge/assets/{id}/approval-trail`.
