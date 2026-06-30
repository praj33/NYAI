# Future Extensibility — Phase V

Phase V is intentionally storage-agnostic and protocol-driven. The paths below
are extension points, not commitments.

## 1. `RedisKnowledgeBackend` (stub shipped)

`backend/knowledge/storage_backend.py` ships a `RedisKnowledgeBackend` that
raises `NotImplementedError`. To implement, satisfy the
`KnowledgeStorageBackend` protocol:

```python
class RedisKnowledgeBackend:
    def store(self, asset): ...        # HSET knowledge:<asset_id> <version_id> <json>
    def retrieve(self, asset_id): ...  # latest version by sorted version_number
    def retrieve_version(self, asset_id, version_id): ...
    def list_versions(self, asset_id): ...
    def list_all(self, limit, offset): ...
    def count(self): ...
    def delete(self, asset_id): ...    # soft-delete marker only
```

Inject it: `KnowledgeRepository(storage=RedisKnowledgeBackend())`.

## 2. `ObjectStorageBackend` (S3/GCS)

Mirror the Phase IV evidence `ObjectStorageBackend` pattern: date-sharded JSONL
objects, one prefix per asset, with cross-region replication. Same protocol; no
business-logic changes.

## 3. Graph database integration (Neo4j adapter)

`EntityRegistry` / `RelationshipRegistry` expose a narrow surface
(`register`, `get`, `list_all`/`get_for_entity`, `count`). A `Neo4jEntityRegistry`
/ `Neo4jRelationshipRegistry` can implement the same methods, and
`GraphTraversal` can be swapped for native Cypher (`MATCH ... DEPENDS_ON*1..n`)
while keeping the `find_dependencies/find_impact/find_path` contract.

## 4. Streaming replay for large knowledge datasets

Today `list_all` and duplicate detection scan in memory. For large stores, add a
generator-based `iter_all()` to the backend protocol and stream evidence replay
rather than materializing lists.

## 5. Signature rotation for governance records

`ApprovalRecord` currently links to evidence by `trace_id`. A future version can
sign each record with a rotating key and store the key id, enabling cryptographic
non-repudiation of approvals alongside the existing hash chain.

## 6. OpenTelemetry integration points

Wrap `record_knowledge_operation`, pipeline stages, and traversal in OTel spans
keyed by the operation `trace_id` to correlate Phase V operations with the
existing structured logs.

## 7. Indexed search (current scan limitation)

Asset listing/filtering and duplicate detection are linear scans. Add an
inverted index (content_hash → asset_id, jurisdiction/domain → asset_ids) — the
same limitation called out for Phase IV evidence search.

## 8. Background workers for ingestion

Ingestion is synchronous. A queue-backed worker (Celery/RQ) could accept
documents, run the pipeline asynchronously, and emit evidence on completion,
keeping the API responsive for bulk loads — while preserving the
"no autonomous promotion" guarantee (workers ingest to DRAFT only).
