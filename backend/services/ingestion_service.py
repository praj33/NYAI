"""
Ingestion service — Phase V.

Thin orchestration layer over ``KnowledgeIngestionPipeline`` and the
``IngestionLog``. Called by the API layer; holds no transport concerns.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ingestion.pipeline import ingestion_pipeline
from ingestion.logger import ingestion_log


class IngestionService:
    def __init__(self, pipeline=None, log=None):
        self._pipeline = pipeline or ingestion_pipeline
        self._log = log or ingestion_log

    def ingest(
        self,
        document: Dict[str, Any],
        actor: str,
        jurisdiction: str,
        domain: str,
        source_attribution: str,
        existing_asset_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        result = self._pipeline.ingest(
            document=document,
            actor=actor,
            jurisdiction=jurisdiction,
            domain=domain,
            source_attribution=source_attribution,
            existing_asset_id=existing_asset_id,
        )
        return result.to_dict()

    def get_log_entry(self, log_id: str) -> Optional[Dict[str, Any]]:
        entry = self._log.get(log_id)
        return entry.to_dict() if entry else None

    def list_log_entries(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        entries = self._log.list_all(limit=limit, offset=offset)
        return {
            "entries": [e.to_dict() for e in entries],
            "total": self._log.count(),
            "limit": limit,
            "offset": offset,
        }


ingestion_service = IngestionService()
