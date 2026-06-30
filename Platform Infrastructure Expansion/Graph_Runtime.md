# Knowledge Graph Runtime — Phase V

Source: `backend/knowledge/graph/`. A generic, in-memory, evidence-linked graph
runtime with filesystem persistence.

## 1. Models

### `Entity`
`entity_id` (UUID), `entity_type` (generic), `label`, `attributes`, `asset_id?`
(optional link to a `KnowledgeAsset`), `created_at`, `evidence_trace_id?`.

### `Relationship`
`relationship_id` (UUID), `source_entity_id`, `target_entity_id`,
`relationship_type` (generic), `weight` (default 1.0), `attributes`,
`created_at`, `evidence_trace_id?`.

## 2. Generic relationship types — no legal ontology in code

Relationship types are **arbitrary caller-supplied strings**. The codebase ships
no embedded legal ontology. Common examples used in docs/tests are `CITES`,
`DEPENDS_ON`, `SUPERSEDES`, `RELATED_TO`, `DERIVED_FROM`, but the runtime treats
them as opaque labels. Only `find_citations()` special-cases the literal string
`"CITES"`, and even that is a generic convenience, not a legal rule.

## 3. Registries & storage

| Registry | File | Notes |
|----------|------|-------|
| `EntityRegistry` | `knowledge_store/graph_entities.jsonl` | in-memory dict + append-only JSONL |
| `RelationshipRegistry` | `knowledge_store/graph_relationships.jsonl` | in-memory dict + append-only JSONL |

Both are thread-safe via `threading.Lock()` and load existing state on init.
`RelationshipRegistry.get_for_entity(entity_id, direction)` supports
`outbound` / `inbound` / `both`.

## 4. Traversal algorithms (`GraphTraversal`)

- **`find_dependencies(entity_id, depth=3)`** — BFS over **outbound** edges.
  Returns `{entity_id, dependencies: [{entity, relationship, level}], depth}`.
- **`find_impact(entity_id, depth=3)`** — reverse BFS over **inbound** edges.
  Returns `{entity_id, impacted_entities: [...], depth}`.
- **`find_citations(entity_id)`** — inbound edges where
  `relationship_type == "CITES"`.
- **`find_path(source, target)`** — BFS shortest path over outbound edges.
  Returns `{path: [entity_id...], relationships: [...], found: bool}`.

`depth` is clamped to `[1, 5]`. **No performance claims** beyond "BFS in memory".

## 5. Loop prevention

Every traversal maintains a `visited` set seeded with the start node and adds
each neighbour before enqueuing it, so cycles (e.g. `A → B → A`) terminate and
never re-expand a node.

## 6. API (`/graph/*`)

| Method | Path | Body / Query | Response |
|--------|------|--------------|----------|
| POST | `/graph/entities` | `{entity_type, label, attributes?, asset_id?}` | `Entity` |
| GET | `/graph/entities/{entity_id}` | — | `Entity` (404 if missing) |
| GET | `/graph/entities` | `entity_type?, limit, offset` | `{entities, total, limit, offset}` |
| POST | `/graph/relationships` | `{source_entity_id, target_entity_id, relationship_type, weight?, attributes?}` | `Relationship` (404 if either entity missing) |
| GET | `/graph/entities/{entity_id}/dependencies` | `depth (1-5)` | `{entity_id, dependencies, depth}` |
| GET | `/graph/entities/{entity_id}/impact` | `depth (1-5)` | `{entity_id, impacted_entities, depth}` |
| GET | `/graph/entities/{entity_id}/citations` | — | `{entity_id, citations}` |
| GET | `/graph/path` | `source_entity_id, target_entity_id` | `{path, relationships, found}` |

`GET /graph/entities?entity_type=<unknown>` returns `200` with an empty list
(not 404).

## 7. Evidence for graph operations

`EntityRegistry.register()` and `RelationshipRegistry.register()` both call
`record_knowledge_operation(operation="GRAPH_OP", ...)`. The returned evidence
`trace_id` is stored on the entity/relationship and is independently
retrievable/verifiable via `/evidence/*`.
