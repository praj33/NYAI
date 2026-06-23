"""Evidence service — orchestrates repository reads and export for API layer."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from evidence.exporter import evidence_exporter
from evidence.models import EvidencePackage
from evidence.repository import evidence_repository
from evidence.search import evidence_search


class EvidenceService:
    def get_by_trace_id(self, trace_id: str) -> Optional[EvidencePackage]:
        return evidence_repository.get_by_trace_id(trace_id)

    def get_raw_by_trace_id(self, trace_id: str) -> Optional[Dict[str, Any]]:
        return evidence_repository.get_raw_by_trace_id(trace_id)

    def search_by_input_hash(self, input_hash: str) -> Optional[EvidencePackage]:
        return evidence_repository.search_by_input_hash(input_hash)

    def search(
        self,
        *,
        recommendation: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        statute_keyword: Optional[str] = None,
        input_hash: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        evidence_version: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        return evidence_search.search(
            recommendation=recommendation,
            jurisdiction=jurisdiction,
            statute_keyword=statute_keyword,
            input_hash=input_hash,
            date_from=date_from,
            date_to=date_to,
            evidence_version=evidence_version,
            limit=limit,
            offset=offset,
        )

    def list_by_evidence_version(self, version: str, limit: int = 20) -> List[EvidencePackage]:
        return evidence_repository.search_by_evidence_version(version, limit=limit)

    def export(self, trace_id: str, fmt: str = "json") -> Optional[Dict[str, Any]]:
        if fmt == "summary":
            return evidence_exporter.export_summary(trace_id)
        return evidence_exporter.export_as_json(trace_id)

    def count(self) -> int:
        return evidence_repository.count()

    def get_ledger_entry_for_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        return evidence_repository.get_ledger_entry_for_trace(trace_id)


def resolve_cached_response(trace_id: str, response_cache) -> Optional[Dict[str, Any]]:
    """L1 cache miss → L2 EvidenceRepository fallback for /nyaya/* secondary endpoints."""
    cached = response_cache.get(trace_id)
    if cached:
        return cached
    return evidence_repository.get_raw_by_trace_id(trace_id)


evidence_service = EvidenceService()
