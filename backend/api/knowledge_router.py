"""
Knowledge API router — Phase V.

Routes under ``/knowledge/*`` for the governed knowledge repository, ingestion,
and promotion pipeline. Routers are thin: they validate transport input and
delegate to services. No business logic lives here.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger("nyai.knowledge.api")
knowledge_router = APIRouter(prefix="/knowledge", tags=["knowledge"])


# ── request models ─────────────────────────────────────────────

class RegisterAssetRequest(BaseModel):
    title: str = Field(..., description="Asset title (required)")
    jurisdiction: str = "Global"
    domain: str = "general"
    source_attribution: str = ""
    content: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    author: Optional[str] = None
    description: Optional[str] = None
    asset_id: Optional[str] = None


class UpdateAssetRequest(BaseModel):
    updates: Dict[str, Any] = Field(..., description="content and/or metadata overrides")
    updated_by: str = Field(..., description="actor performing the update")


class IngestRequest(BaseModel):
    document: Dict[str, Any] = Field(..., description="raw document to ingest")
    actor: str
    jurisdiction: str = "Global"
    domain: str = "general"
    source_attribution: str = ""
    existing_asset_id: Optional[str] = None


class PromoteRequest(BaseModel):
    target_state: str = Field(..., description="DRAFT | REVIEW | APPROVED | ARCHIVED")
    actor: str
    rationale: str


class RollbackRequest(BaseModel):
    target_version_id: str
    actor: str
    reason: str


# ── service accessors (lazy import keeps router import-safe) ────

def _knowledge():
    from services.knowledge_service import knowledge_service
    return knowledge_service


def _ingestion():
    from services.ingestion_service import ingestion_service
    return ingestion_service


def _promotion():
    from services.promotion_service import promotion_service
    return promotion_service


# ── static / specific routes first ─────────────────────────────

@knowledge_router.post("/assets")
async def register_asset(request: RegisterAssetRequest):
    return _knowledge().register(request.dict())


@knowledge_router.get("/assets")
async def list_assets(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    jurisdiction: Optional[str] = Query(None),
    domain: Optional[str] = Query(None),
):
    return _knowledge().list_all(
        limit=limit, offset=offset, jurisdiction=jurisdiction, domain=domain
    )


@knowledge_router.post("/ingest")
async def ingest_document(request: IngestRequest):
    return _ingestion().ingest(
        document=request.document,
        actor=request.actor,
        jurisdiction=request.jurisdiction,
        domain=request.domain,
        source_attribution=request.source_attribution,
        existing_asset_id=request.existing_asset_id,
    )


@knowledge_router.get("/ingestion")
async def list_ingestion(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return _ingestion().list_log_entries(limit=limit, offset=offset)


@knowledge_router.get("/ingestion/{log_id}")
async def get_ingestion_entry(log_id: str):
    entry = _ingestion().get_log_entry(log_id)
    if entry is None:
        raise HTTPException(status_code=404, detail={"error_code": "INGESTION_LOG_NOT_FOUND", "log_id": log_id})
    return entry


# ── asset detail + version routes ──────────────────────────────

@knowledge_router.get("/assets/{asset_id}/versions/{version_id}")
async def get_asset_version(asset_id: str, version_id: str):
    asset = _knowledge().get_version(asset_id, version_id)
    if asset is None:
        raise HTTPException(status_code=404, detail={"error_code": "VERSION_NOT_FOUND", "asset_id": asset_id, "version_id": version_id})
    return asset


@knowledge_router.get("/assets/{asset_id}/versions")
async def list_asset_versions(asset_id: str):
    versions = _knowledge().list_versions(asset_id)
    if not versions:
        raise HTTPException(status_code=404, detail={"error_code": "ASSET_NOT_FOUND", "asset_id": asset_id})
    return versions


@knowledge_router.get("/assets/{asset_id}/integrity")
async def get_asset_integrity(asset_id: str):
    report = _knowledge().verify_integrity(asset_id)
    if report.get("status") == "NOT_FOUND":
        raise HTTPException(status_code=404, detail={"error_code": "ASSET_NOT_FOUND", "asset_id": asset_id})
    return report


@knowledge_router.get("/assets/{asset_id}/state")
async def get_asset_state(asset_id: str):
    try:
        return _promotion().get_state(asset_id)
    except KeyError:
        raise HTTPException(status_code=404, detail={"error_code": "ASSET_NOT_FOUND", "asset_id": asset_id})


@knowledge_router.get("/assets/{asset_id}/approval-trail")
async def get_approval_trail(asset_id: str):
    return _promotion().get_approval_trail(asset_id)


@knowledge_router.post("/assets/{asset_id}/promote")
async def promote_asset(asset_id: str, request: PromoteRequest):
    try:
        return _promotion().promote(
            asset_id=asset_id,
            target_state=request.target_state,
            actor=request.actor,
            rationale=request.rationale,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail={"error_code": "ASSET_NOT_FOUND", "asset_id": asset_id})
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error_code": "INVALID_PROMOTION", "message": str(e)})


@knowledge_router.post("/assets/{asset_id}/rollback")
async def rollback_asset(asset_id: str, request: RollbackRequest):
    try:
        return _promotion().rollback(
            asset_id=asset_id,
            target_version_id=request.target_version_id,
            actor=request.actor,
            reason=request.reason,
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail={"error_code": "NOT_FOUND", "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error_code": "INVALID_ROLLBACK", "message": str(e)})


@knowledge_router.patch("/assets/{asset_id}")
async def update_asset(asset_id: str, request: UpdateAssetRequest):
    try:
        return _knowledge().update(asset_id, request.updates, request.updated_by)
    except KeyError:
        raise HTTPException(status_code=404, detail={"error_code": "ASSET_NOT_FOUND", "asset_id": asset_id})
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error_code": "INVALID_UPDATE", "message": str(e)})


@knowledge_router.get("/assets/{asset_id}")
async def get_asset(asset_id: str):
    asset = _knowledge().get(asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail={"error_code": "ASSET_NOT_FOUND", "asset_id": asset_id})
    return asset
