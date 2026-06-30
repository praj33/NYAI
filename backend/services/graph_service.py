"""
Graph service — Phase V.

Thin orchestration layer over the graph registries and traversal engine.
Validation that referenced entities exist lives here (fail closed); the API
layer simply maps exceptions to HTTP codes.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from knowledge.graph.models import Entity, Relationship, new_entity, new_relationship
from knowledge.graph.registry import entity_registry, relationship_registry
from knowledge.graph.traversal import GraphTraversal


class GraphService:
    def __init__(self, entities=None, relationships=None):
        self._entities = entities or entity_registry
        self._relationships = relationships or relationship_registry
        self._traversal = GraphTraversal(self._entities, self._relationships)

    # ── entities ───────────────────────────────────────────────

    def register_entity(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        entity = new_entity(
            entity_type=payload["entity_type"],
            label=payload["label"],
            attributes=payload.get("attributes") or {},
            asset_id=payload.get("asset_id"),
        )
        stored = self._entities.register(entity)
        return stored.to_dict()

    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        entity = self._entities.get(entity_id)
        return entity.to_dict() if entity else None

    def list_entities(
        self,
        entity_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        entities = self._entities.list_all(entity_type=entity_type)
        total = len(entities)
        page = entities[offset:offset + limit]
        return {
            "entities": [e.to_dict() for e in page],
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    # ── relationships ──────────────────────────────────────────

    def register_relationship(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source_id = payload["source_entity_id"]
        target_id = payload["target_entity_id"]
        if self._entities.get(source_id) is None:
            raise KeyError(f"source_entity_id not found: {source_id}")
        if self._entities.get(target_id) is None:
            raise KeyError(f"target_entity_id not found: {target_id}")
        relationship = new_relationship(
            source_entity_id=source_id,
            target_entity_id=target_id,
            relationship_type=payload["relationship_type"],
            weight=float(payload.get("weight", 1.0)),
            attributes=payload.get("attributes") or {},
        )
        stored = self._relationships.register(relationship)
        return stored.to_dict()

    # ── traversal ──────────────────────────────────────────────

    def find_dependencies(self, entity_id: str, depth: int = 3) -> Dict[str, Any]:
        if self._entities.get(entity_id) is None:
            raise KeyError(f"entity_id not found: {entity_id}")
        return self._traversal.find_dependencies(entity_id, depth=depth)

    def find_impact(self, entity_id: str, depth: int = 3) -> Dict[str, Any]:
        if self._entities.get(entity_id) is None:
            raise KeyError(f"entity_id not found: {entity_id}")
        return self._traversal.find_impact(entity_id, depth=depth)

    def find_citations(self, entity_id: str) -> Dict[str, Any]:
        if self._entities.get(entity_id) is None:
            raise KeyError(f"entity_id not found: {entity_id}")
        return {"entity_id": entity_id, "citations": self._traversal.find_citations(entity_id)}

    def find_path(self, source_entity_id: str, target_entity_id: str) -> Dict[str, Any]:
        return self._traversal.find_path(source_entity_id, target_entity_id)


graph_service = GraphService()
