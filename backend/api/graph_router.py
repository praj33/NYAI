"""
Graph API router — Phase V.

Routes under ``/graph/*`` for the knowledge graph runtime (entities,
relationships, dependency / impact / citation / path traversal). Thin transport
layer delegating to ``graph_service``.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger("nyai.graph.api")
graph_router = APIRouter(prefix="/graph", tags=["graph"])


# ── request models ─────────────────────────────────────────────

class EntityRequest(BaseModel):
    entity_type: str
    label: str
    attributes: Dict[str, Any] = Field(default_factory=dict)
    asset_id: Optional[str] = None


class RelationshipRequest(BaseModel):
    source_entity_id: str
    target_entity_id: str
    relationship_type: str
    weight: float = 1.0
    attributes: Dict[str, Any] = Field(default_factory=dict)


def _graph():
    from services.graph_service import graph_service
    return graph_service


# ── static / specific routes first ─────────────────────────────

@graph_router.post("/entities")
async def register_entity(request: EntityRequest):
    return _graph().register_entity(request.dict())


@graph_router.get("/entities")
async def list_entities(
    entity_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return _graph().list_entities(entity_type=entity_type, limit=limit, offset=offset)


@graph_router.post("/relationships")
async def register_relationship(request: RelationshipRequest):
    try:
        return _graph().register_relationship(request.dict())
    except KeyError as e:
        raise HTTPException(status_code=404, detail={"error_code": "ENTITY_NOT_FOUND", "message": str(e)})


@graph_router.get("/path")
async def find_path(
    source_entity_id: str = Query(...),
    target_entity_id: str = Query(...),
):
    return _graph().find_path(source_entity_id, target_entity_id)


# ── entity detail + traversal routes ───────────────────────────

@graph_router.get("/entities/{entity_id}/dependencies")
async def get_dependencies(entity_id: str, depth: int = Query(3, ge=1, le=5)):
    try:
        return _graph().find_dependencies(entity_id, depth=depth)
    except KeyError:
        raise HTTPException(status_code=404, detail={"error_code": "ENTITY_NOT_FOUND", "entity_id": entity_id})


@graph_router.get("/entities/{entity_id}/impact")
async def get_impact(entity_id: str, depth: int = Query(3, ge=1, le=5)):
    try:
        return _graph().find_impact(entity_id, depth=depth)
    except KeyError:
        raise HTTPException(status_code=404, detail={"error_code": "ENTITY_NOT_FOUND", "entity_id": entity_id})


@graph_router.get("/entities/{entity_id}/citations")
async def get_citations(entity_id: str):
    try:
        return _graph().find_citations(entity_id)
    except KeyError:
        raise HTTPException(status_code=404, detail={"error_code": "ENTITY_NOT_FOUND", "entity_id": entity_id})


@graph_router.get("/entities/{entity_id}")
async def get_entity(entity_id: str):
    entity = _graph().get_entity(entity_id)
    if entity is None:
        raise HTTPException(status_code=404, detail={"error_code": "ENTITY_NOT_FOUND", "entity_id": entity_id})
    return entity
