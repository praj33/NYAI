from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from evidence.repository import evidence_repository

class EvidenceExporter:
    def export_as_json(self, trace_id: str) -> Optional[Dict[str, Any]]:
        pkg = evidence_repository.get_by_trace_id(trace_id)
        if not pkg:
            return None
        return {"export_format": "nyai_evidence_v1",
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "evidence": pkg.to_dict()}

    def export_summary(self, trace_id: str) -> Optional[Dict[str, Any]]:
        pkg = evidence_repository.get_by_trace_id(trace_id)
        if not pkg:
            return None
        return {"evidence_id": pkg.identity.evidence_id, "trace_id": pkg.identity.trace_id,
                "created_at": pkg.identity.created_at, "recommendation": pkg.decision.recommendation_type,
                "jurisdiction": pkg.decision.jurisdiction, "domain": pkg.decision.domain,
                "confidence": pkg.decision.confidence, "input_hash": pkg.hashes.input_hash,
                "output_hash": pkg.hashes.output_hash, "integrity_status": pkg.integrity_status,
                "statute_count": len(pkg.reasoning.applicable_statutes),
                "fact_count": len(pkg.reasoning.facts)}

evidence_exporter = EvidenceExporter()
