"""
Knowledge service — Phase V.

Thin orchestration layer over ``KnowledgeRepository``. The API layer
(``knowledge_router``) calls this service; the service holds no transport
concerns and the repository holds the business logic + evidence linkage.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from knowledge.models import KnowledgeAsset, new_asset
from knowledge.repository import knowledge_repository


class KnowledgeService:
    def __init__(self, repository=None):
        self._repo = repository or knowledge_repository

    def register(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        asset = new_asset(
            title=payload["title"],
            jurisdiction=payload.get("jurisdiction", "Global"),
            domain=payload.get("domain", "general"),
            source_attribution=payload.get("source_attribution", ""),
            content=payload.get("content") or {},
            tags=payload.get("tags") or [],
            author=payload.get("author"),
            description=payload.get("description"),
            asset_id=payload.get("asset_id"),
        )
        stored = self._repo.register(asset)
        return {
            "asset_id": stored.identity.asset_id,
            "version_id": stored.identity.version_id,
            "trace_id": stored.governance.evidence_id,
            "version_number": stored.identity.version_number,
        }

    def get(self, asset_id: str) -> Optional[Dict[str, Any]]:
        asset = self._repo.get(asset_id)
        return asset.to_dict() if asset else None

    def get_version(self, asset_id: str, version_id: str) -> Optional[Dict[str, Any]]:
        asset = self._repo.get_version(asset_id, version_id)
        return asset.to_dict() if asset else None

    def list_versions(self, asset_id: str) -> List[Dict[str, Any]]:
        return [a.to_dict() for a in self._repo.list_versions(asset_id)]

    def update(self, asset_id: str, updates: Dict[str, Any], updated_by: str) -> Dict[str, Any]:
        updated = self._repo.update(asset_id, updates, updated_by)
        return {
            "asset_id": updated.identity.asset_id,
            "new_version_id": updated.identity.version_id,
            "trace_id": updated.governance.evidence_id,
            "version_number": updated.identity.version_number,
        }

    def verify_integrity(self, asset_id: str) -> Dict[str, Any]:
        return self._repo.verify_integrity(asset_id)

    def list_all(
        self,
        limit: int = 50,
        offset: int = 0,
        jurisdiction: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        assets = self._repo.list_all(limit=1_000_000, offset=0)
        if jurisdiction:
            assets = [a for a in assets if a.metadata.jurisdiction.lower() == jurisdiction.lower()]
        if domain:
            assets = [a for a in assets if a.metadata.domain.lower() == domain.lower()]
        total = len(assets)
        page = assets[offset:offset + limit]
        return {
            "assets": [a.to_dict() for a in page],
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def count(self) -> int:
        return self._repo.count()


knowledge_service = KnowledgeService()
