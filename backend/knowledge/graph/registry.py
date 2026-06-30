"""
Entity / Relationship registries — Phase V graph runtime.

In-memory stores with append-only JSONL persistence under
``backend/knowledge_store/``. Thread-safe via ``threading.Lock()``.
Every registration writes an evidence record via the evidence bridge.
"""
from __future__ import annotations

import hashlib
import json
import os
import threading
import uuid
from typing import Any, Dict, List, Optional

from knowledge.graph.models import Entity, Relationship
from knowledge.evidence_bridge import record_knowledge_operation


def _resolve_store_dir() -> str:
    configured = os.environ.get("KNOWLEDGE_STORE_DIRECTORY", "").strip()
    if configured:
        return configured
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", "knowledge_store"
    )


def _hash(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


class EntityRegistry:
    """In-memory entity store persisted to ``graph_entities.jsonl``."""

    def __init__(self, store_dir: Optional[str] = None):
        if store_dir is None:
            store_dir = _resolve_store_dir()
        self._store_dir = store_dir
        os.makedirs(self._store_dir, exist_ok=True)
        self._file = os.path.join(self._store_dir, "graph_entities.jsonl")
        self._entities: Dict[str, Entity] = {}
        self._lock = threading.Lock()
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self._file):
            return
        with open(self._file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entity = Entity.from_dict(json.loads(line))
                    self._entities[entity.entity_id] = entity
                except (json.JSONDecodeError, TypeError):
                    continue

    def register(self, entity: Entity) -> Entity:
        if not entity.entity_id:
            entity.entity_id = str(uuid.uuid4())
        evidence_trace_id = record_knowledge_operation(
            operation="GRAPH_OP",
            asset_id=entity.asset_id or entity.entity_id,
            version_id=entity.entity_id,
            trace_id=str(uuid.uuid4()),
            actor=str(entity.attributes.get("actor", "system")),
            metadata={
                "jurisdiction": "Global",
                "domain": "graph",
                "graph_op": "REGISTER_ENTITY",
                "entity_type": entity.entity_type,
            },
            content_hash=_hash({"label": entity.label, "type": entity.entity_type, "attrs": entity.attributes}),
        )
        entity.evidence_trace_id = evidence_trace_id
        with self._lock:
            self._entities[entity.entity_id] = entity
            with open(self._file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entity.to_dict(), sort_keys=True, default=str) + "\n")
        return entity

    def get(self, entity_id: str) -> Optional[Entity]:
        with self._lock:
            return self._entities.get(entity_id)

    def list_all(self, entity_type: Optional[str] = None) -> List[Entity]:
        with self._lock:
            entities = list(self._entities.values())
        if entity_type:
            entities = [e for e in entities if e.entity_type == entity_type]
        return entities

    def count(self) -> int:
        with self._lock:
            return len(self._entities)


class RelationshipRegistry:
    """In-memory relationship store persisted to ``graph_relationships.jsonl``."""

    def __init__(self, store_dir: Optional[str] = None):
        if store_dir is None:
            store_dir = _resolve_store_dir()
        self._store_dir = store_dir
        os.makedirs(self._store_dir, exist_ok=True)
        self._file = os.path.join(self._store_dir, "graph_relationships.jsonl")
        self._relationships: Dict[str, Relationship] = {}
        self._lock = threading.Lock()
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self._file):
            return
        with open(self._file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rel = Relationship.from_dict(json.loads(line))
                    self._relationships[rel.relationship_id] = rel
                except (json.JSONDecodeError, TypeError):
                    continue

    def register(self, relationship: Relationship) -> Relationship:
        if not relationship.relationship_id:
            relationship.relationship_id = str(uuid.uuid4())
        evidence_trace_id = record_knowledge_operation(
            operation="GRAPH_OP",
            asset_id=relationship.relationship_id,
            version_id=relationship.relationship_id,
            trace_id=str(uuid.uuid4()),
            actor=str(relationship.attributes.get("actor", "system")),
            metadata={
                "jurisdiction": "Global",
                "domain": "graph",
                "graph_op": "REGISTER_RELATIONSHIP",
                "relationship_type": relationship.relationship_type,
            },
            content_hash=_hash({
                "src": relationship.source_entity_id,
                "tgt": relationship.target_entity_id,
                "type": relationship.relationship_type,
            }),
        )
        relationship.evidence_trace_id = evidence_trace_id
        with self._lock:
            self._relationships[relationship.relationship_id] = relationship
            with open(self._file, "a", encoding="utf-8") as f:
                f.write(json.dumps(relationship.to_dict(), sort_keys=True, default=str) + "\n")
        return relationship

    def get(self, relationship_id: str) -> Optional[Relationship]:
        with self._lock:
            return self._relationships.get(relationship_id)

    def get_for_entity(self, entity_id: str, direction: str = "both") -> List[Relationship]:
        """direction: 'outbound' | 'inbound' | 'both'."""
        with self._lock:
            rels = list(self._relationships.values())
        out: List[Relationship] = []
        for r in rels:
            if direction in ("outbound", "both") and r.source_entity_id == entity_id:
                out.append(r)
            elif direction in ("inbound", "both") and r.target_entity_id == entity_id:
                out.append(r)
        return out

    def count(self) -> int:
        with self._lock:
            return len(self._relationships)


entity_registry = EntityRegistry()
relationship_registry = RelationshipRegistry()
