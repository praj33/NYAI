"""
Workspace API router — Phase V.

Routes under ``/workspace/*`` for document upload/versioning, annotations,
diffing and audit history. Thin transport layer; the workspace stores hold the
domain logic and evidence linkage.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("nyai.workspace.api")
workspace_router = APIRouter(prefix="/workspace", tags=["workspace"])


# ── request models ─────────────────────────────────────────────

class UploadRequest(BaseModel):
    asset_id: str = Field(..., description="linked KnowledgeAsset id")
    filename: str
    content: Dict[str, Any] = Field(..., description="document body (required)")
    content_type: str = "application/json"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    uploaded_by: str = "system"
    version_id: Optional[str] = None


class MetadataUpdateRequest(BaseModel):
    metadata: Dict[str, Any] = Field(..., description="metadata fields to merge")
    actor: str


class AnnotationRequest(BaseModel):
    doc_id: str
    asset_id: str
    annotation_type: str = Field(..., description="COMMENT | REVIEW_NOTE | FLAG | APPROVAL_NOTE")
    content: str
    author: str


# ── store accessors ────────────────────────────────────────────

def _documents():
    from workspace.document_store import document_store
    return document_store


def _annotations():
    from workspace.annotation_store import annotation_store
    return annotation_store


def _build_document(req: UploadRequest):
    from workspace.document_store import WorkspaceDocument
    return WorkspaceDocument(
        doc_id="",
        asset_id=req.asset_id,
        version_id=req.version_id or "",
        filename=req.filename,
        content_type=req.content_type,
        content=req.content,
        metadata=req.metadata,
        uploaded_by=req.uploaded_by,
        uploaded_at="",
    )


# ── routes ─────────────────────────────────────────────────────

@workspace_router.post("/documents/upload")
async def upload_document(request: UploadRequest):
    doc = _documents().upload(_build_document(request))
    return doc.to_dict()


@workspace_router.post("/annotations")
async def add_annotation(request: AnnotationRequest):
    from workspace.annotation_store import Annotation
    try:
        annotation = _annotations().add(Annotation(
            annotation_id="",
            doc_id=request.doc_id,
            asset_id=request.asset_id,
            annotation_type=request.annotation_type,
            content=request.content,
            author=request.author,
        ))
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error_code": "INVALID_ANNOTATION", "message": str(e)})
    return annotation.to_dict()


@workspace_router.patch("/documents/{doc_id}/metadata")
async def update_document_metadata(doc_id: str, request: MetadataUpdateRequest):
    try:
        doc = _documents().update_metadata(doc_id, request.metadata, request.actor)
    except KeyError:
        raise HTTPException(status_code=404, detail={"error_code": "DOCUMENT_NOT_FOUND", "doc_id": doc_id})
    return doc.to_dict()


@workspace_router.get("/documents/{doc_id}/annotations")
async def get_document_annotations(doc_id: str) -> List[Dict[str, Any]]:
    return [a.to_dict() for a in _annotations().get_for_document(doc_id)]


@workspace_router.get("/documents/{doc_id_a}/compare/{doc_id_b}")
async def compare_documents(doc_id_a: str, doc_id_b: str):
    try:
        return _documents().compare_versions(doc_id_a, doc_id_b)
    except KeyError as e:
        raise HTTPException(status_code=404, detail={"error_code": "DOCUMENT_NOT_FOUND", "message": str(e)})


@workspace_router.get("/documents/{doc_id}/audit")
async def get_document_audit(doc_id: str):
    try:
        return _documents().get_audit_history(doc_id)
    except KeyError:
        raise HTTPException(status_code=404, detail={"error_code": "DOCUMENT_NOT_FOUND", "doc_id": doc_id})


@workspace_router.get("/documents/{asset_id}/versions")
async def get_document_versions(asset_id: str) -> List[Dict[str, Any]]:
    return [d.to_dict() for d in _documents().get_version_history(asset_id)]
