# Architecture — Platform Infrastructure Expansion (Phase V)

Phase V extends the Phase IV Constitutional Evidence Infrastructure with a
governed knowledge layer. **Nothing in the evidence layer was redesigned** —
every Phase V operation funnels into the existing `OutputBucket` through a thin
`evidence_bridge`, so all new operations are automatically visible, replayable,
and verifiable through the existing `/evidence/*` API.

## 1. System diagram (Phase V overlaid on Phase IV)

```
                         ┌──────────────────────────────────────────┐
   Client (X-API-Key)    │            FastAPI app (api/main.py)       │
        │                │  middleware: Trace → Logging → RateLimit   │
        │                │             → APIKeyAuth                    │
        ▼                └──────────────────────────────────────────┘
  ┌───────────────────────── Phase V routers (mounted AFTER Phase IV) ─────────────────────────┐
  │  /knowledge/*  (knowledge_router)   /workspace/* (workspace_router)   /graph/* (graph_router)│
  └───────┬──────────────────────────────────┬───────────────────────────────────┬────────────┘
          ▼                                   ▼                                   ▼
   knowledge_service                  document_store / annotation_store      graph_service
   ingestion_service                                                          (registries +
   promotion_service                                                           traversal)
          │                                   │                                   │
          ▼                                   ▼                                   ▼
   KnowledgeRepository ───────► IngestionPipeline      PromotionPipeline    EntityRegistry
   (storage-agnostic)          (validate/dedupe/log)   (state machine +     RelationshipRegistry
          │                                              ApprovalStore)      GraphTraversal (BFS)
          │                                   │                                   │
          └───────────────┬───────────────────┴───────────────────┬───────────────┘
                          ▼                                         ▼
                 knowledge/evidence_bridge.record_knowledge_operation()
                          │   (builds TANTRA-canonical record, validates via ResponseBuilder)
                          ▼
        ┌──────────────────────────── Phase IV (frozen) ────────────────────────────┐
        │  tantra/output_bucket.store()  ──►  EvidenceRepository  ──►  /evidence/*    │
        │  (append-only JSONL, entry_hash)    (on-demand EvidencePackage assembly)    │
        └────────────────────────────────────────────────────────────────────────────┘
```

## 2. Component map

```
KnowledgeRepository ─┐
IngestionPipeline ───┤
PromotionPipeline ───┼──► EvidenceBridge ──► OutputBucket ──► EvidenceRepository ──► /evidence/*
GraphRuntime ────────┤
WorkspaceAPIs ───────┘
```

Each box is storage-agnostic: it depends only on a `Protocol` (e.g.
`KnowledgeStorageBackend`) and never hard-codes file paths inside business logic.

## 3. Data flow: ingestion → promotion → graph

1. **Ingest** — `POST /knowledge/ingest` → `IngestionPipeline` validates the
   document, extracts metadata, detects duplicates, registers a **DRAFT/PENDING**
   asset (v1), writes an `IngestionLogEntry`, and records `INGEST_NEW` evidence.
2. **Workspace review** — documents/annotations are uploaded under `/workspace/*`;
   each upload/update/annotation is a new versioned record + evidence.
3. **Promote** — `POST /knowledge/assets/{id}/promote` walks the state machine
   `DRAFT → REVIEW → APPROVED → ARCHIVED`; every transition requires an explicit
   `actor` + `rationale`, writes an `ApprovalRecord`, and records `PROMOTE`
   evidence. **No autonomous promotion.**
4. **Rollback** — `POST /knowledge/assets/{id}/rollback` appends a new DRAFT
   version copied from a prior version (history never overwritten) + `ROLLBACK`
   evidence.
5. **Graph** — entities/relationships are registered under `/graph/*`;
   dependency / impact / citation / path queries run BFS in memory. Every
   registration records `GRAPH_OP` evidence.

## 4. Storage layout (JSONL files and directories)

| Path | Content | Writer |
|------|---------|--------|
| `backend/knowledge_store/<asset_id>.jsonl` | One line per asset version (append-only) | `FileSystemKnowledgeBackend` |
| `backend/knowledge_store/graph_entities.jsonl` | Graph entities | `EntityRegistry` |
| `backend/knowledge_store/graph_relationships.jsonl` | Graph relationships | `RelationshipRegistry` |
| `backend/ingestion_logs/ingestion_log.jsonl` | Ingestion audit entries | `IngestionLog` |
| `backend/promotion_logs/approval_log.jsonl` | Approval / rollback records | `ApprovalStore` |
| `backend/workspace_store/documents.jsonl` | Workspace document versions | `DocumentStore` |
| `backend/workspace_store/annotations.jsonl` | Annotations | `AnnotationStore` |
| `backend/output_logs/nyai_output_log.jsonl` | **(Phase IV, frozen)** Evidence records for every Phase V op | `OutputBucket` |

All directories are overridable via environment variables (see
`Integration_Guide.md`).

## 5. Evidence linkage diagram

```
KnowledgeAsset.governance.evidence_id ─┐
KnowledgeAsset.evidence_linkage[]      ├─► evidence trace_id (uuid4)
WorkspaceDocument.evidence_trace_id    │        │
Annotation.evidence_trace_id           │        ▼
Entity/Relationship.evidence_trace_id  │   OutputBucket entry (full TANTRA record)
ApprovalRecord.evidence_trace_id      ─┘        │
                                                ▼
                            GET /evidence/{trace_id}  → EvidencePackage
                            POST /evidence/verify     → integrity_status
```

Every Phase V mutation stores exactly one TANTRA-canonical evidence record whose
fresh `trace_id` is returned to the caller and persisted on the domain object,
giving a bidirectional link between the knowledge object and its evidence.

## 6. Thread-safety & fail-closed posture

- All shared mutable state (`FileSystemKnowledgeBackend`, registries, logs,
  stores) uses `threading.Lock()`, mirroring `tantra/output_bucket.py`.
- Missing required fields → exception → HTTP 4xx/5xx (FastAPI validation 422,
  invalid transitions 400, missing resources 404). No silent degradation.
- The evidence bridge validates every record through the **frozen**
  `ResponseBuilder` before persistence, so a malformed record fails closed
  rather than polluting the evidence store.
