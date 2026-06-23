from __future__ import annotations
import json
from typing import Any, Dict, List, Optional
from evidence.repository import evidence_repository

class EvidenceSearch:
    def search(
        self,
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
        if input_hash:
            pkg = evidence_repository.search_by_input_hash(input_hash)
            packages = [pkg] if pkg else []
        elif date_from and date_to:
            packages = evidence_repository.search_by_date_range(date_from, date_to, limit=10000)
        elif evidence_version:
            packages = evidence_repository.search_by_evidence_version(evidence_version, limit=10000)
        elif recommendation:
            packages = evidence_repository.search_by_recommendation(recommendation, limit=500)
        elif jurisdiction:
            packages = evidence_repository.search_by_jurisdiction(jurisdiction, limit=500)
        elif statute_keyword:
            packages = evidence_repository.search_by_statute(statute_keyword, limit=500)
        else:
            packages = evidence_repository.list_evidence(limit=500, offset=0)

        if jurisdiction and recommendation:
            packages = [p for p in packages if jurisdiction.lower() in p.decision.jurisdiction.lower()]
        if evidence_version:
            packages = [p for p in packages if p.identity.evidence_version == evidence_version]
        if date_from and date_to:
            packages = [
                p for p in packages
                if date_from <= p.identity.created_at <= date_to
            ]
        if statute_keyword and packages and (recommendation or jurisdiction or input_hash or date_from):
            packages = [p for p in packages if any(
                statute_keyword.lower() in json.dumps(s, default=str).lower()
                for s in p.reasoning.applicable_statutes)]

        total = len(packages)
        return {
            "total": total, "limit": limit, "offset": offset,
            "results": [
                {"trace_id": p.identity.trace_id, "evidence_id": p.identity.evidence_id,
                 "recommendation_type": p.decision.recommendation_type, "jurisdiction": p.decision.jurisdiction,
                 "domain": p.decision.domain, "input_hash": p.hashes.input_hash,
                 "created_at": p.identity.created_at, "integrity_status": p.integrity_status,
                 "evidence_version": p.identity.evidence_version}
                for p in packages[offset: offset + limit]
            ],
        }

evidence_search = EvidenceSearch()
