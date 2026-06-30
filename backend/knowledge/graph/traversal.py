"""
Graph traversal — Phase V graph runtime.

In-memory BFS traversal with explicit ``visited`` sets to prevent infinite
loops on cyclic graphs. No performance claims beyond "BFS in memory".
"""
from __future__ import annotations

from collections import deque
from typing import Any, Dict, List, Optional

from knowledge.graph.registry import EntityRegistry, RelationshipRegistry


class GraphTraversal:
    def __init__(
        self,
        entity_registry: EntityRegistry,
        relationship_registry: RelationshipRegistry,
    ):
        self._entities = entity_registry
        self._relationships = relationship_registry

    def find_dependencies(self, entity_id: str, depth: int = 3) -> Dict[str, Any]:
        """
        BFS over OUTBOUND edges: entities this one depends on / points to.

        Returns ``{entity_id, dependencies, depth}`` where ``dependencies`` is a
        list of ``{entity, relationship, level}``.
        """
        return self._bfs(entity_id, depth, direction="outbound", result_key="dependencies")

    def find_impact(self, entity_id: str, depth: int = 3) -> Dict[str, Any]:
        """
        Reverse BFS over INBOUND edges: entities that depend on this one.

        Returns ``{entity_id, impacted_entities, depth}``.
        """
        return self._bfs(entity_id, depth, direction="inbound", result_key="impacted_entities")

    def find_citations(self, entity_id: str) -> List[Dict[str, Any]]:
        """Return all entities that CITE this entity (relationship_type == 'CITES')."""
        citations: List[Dict[str, Any]] = []
        for rel in self._relationships.get_for_entity(entity_id, direction="inbound"):
            if rel.relationship_type == "CITES":
                source = self._entities.get(rel.source_entity_id)
                citations.append({
                    "entity": source.to_dict() if source else {"entity_id": rel.source_entity_id},
                    "relationship": rel.to_dict(),
                })
        return citations

    def find_path(self, source_entity_id: str, target_entity_id: str) -> Dict[str, Any]:
        """
        BFS shortest path over OUTBOUND edges.

        Returns ``{path, relationships, found}`` where ``path`` is a list of
        entity_ids (inclusive of source and target).
        """
        if source_entity_id == target_entity_id:
            return {"path": [source_entity_id], "relationships": [], "found": True}

        visited = {source_entity_id}
        # queue holds (entity_id, path_of_ids, path_of_relationships)
        queue: deque = deque([(source_entity_id, [source_entity_id], [])])
        while queue:
            current, path, rels = queue.popleft()
            for rel in self._relationships.get_for_entity(current, direction="outbound"):
                nxt = rel.target_entity_id
                if nxt in visited:
                    continue
                new_path = path + [nxt]
                new_rels = rels + [rel.to_dict()]
                if nxt == target_entity_id:
                    return {"path": new_path, "relationships": new_rels, "found": True}
                visited.add(nxt)
                queue.append((nxt, new_path, new_rels))
        return {"path": [], "relationships": [], "found": False}

    # ── internals ──────────────────────────────────────────────

    def _bfs(self, entity_id: str, depth: int, direction: str, result_key: str) -> Dict[str, Any]:
        depth = max(1, min(int(depth), 5))
        results: List[Dict[str, Any]] = []
        visited = {entity_id}
        # queue holds (entity_id, level)
        queue: deque = deque([(entity_id, 0)])
        while queue:
            current, level = queue.popleft()
            if level >= depth:
                continue
            for rel in self._relationships.get_for_entity(current, direction=direction):
                neighbor_id = (
                    rel.target_entity_id if direction == "outbound" else rel.source_entity_id
                )
                if neighbor_id in visited:
                    continue
                visited.add(neighbor_id)
                neighbor = self._entities.get(neighbor_id)
                results.append({
                    "entity": neighbor.to_dict() if neighbor else {"entity_id": neighbor_id},
                    "relationship": rel.to_dict(),
                    "level": level + 1,
                })
                queue.append((neighbor_id, level + 1))
        return {"entity_id": entity_id, result_key: results, "depth": depth}
