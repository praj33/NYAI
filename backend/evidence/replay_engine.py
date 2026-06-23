from __future__ import annotations
import logging
from typing import Any, Dict, List
from evidence.repository import evidence_repository
from evidence.integrity import evidence_integrity

logger = logging.getLogger("nyai.evidence.replay")

class ReplayEngine:
    def replay_by_trace(self, trace_id: str) -> Dict[str, Any]:
        pkg = evidence_repository.get_by_trace_id(trace_id)
        if not pkg:
            return {"replayed": False, "trace_id": trace_id, "reason": "evidence_not_found"}
        verification = evidence_integrity.verify_by_trace_id(trace_id)
        pkg.integrity_status = verification.get("integrity_status", "UNVERIFIED")
        return {"replayed": True, "trace_id": trace_id, "integrity_status": pkg.integrity_status,
                "tamper_detected": verification.get("tamper_detected", False),
                "evidence": pkg.to_dict(), "replay_source": "output_bucket"}

    def replay_by_input_hash(self, input_hash: str) -> Dict[str, Any]:
        pkg = evidence_repository.search_by_input_hash(input_hash)
        if not pkg:
            return {"replayed": False, "input_hash": input_hash, "reason": "no_evidence_for_input_hash"}
        return self.replay_by_trace(pkg.identity.trace_id)

    def replay_by_recommendation(self, rec_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        return [
            {"trace_id": p.identity.trace_id, "recommendation_type": p.decision.recommendation_type,
             "jurisdiction": p.decision.jurisdiction, "evidence_id": p.identity.evidence_id,
             "created_at": p.identity.created_at}
            for p in evidence_repository.search_by_recommendation(rec_type, limit=limit)
        ]

    def replay_by_jurisdiction(self, jurisdiction: str, limit: int = 10) -> List[Dict[str, Any]]:
        return [
            {"trace_id": p.identity.trace_id, "jurisdiction": p.decision.jurisdiction,
             "recommendation_type": p.decision.recommendation_type,
             "evidence_id": p.identity.evidence_id, "created_at": p.identity.created_at}
            for p in evidence_repository.search_by_jurisdiction(jurisdiction, limit=limit)
        ]

    def replay_by_statute(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        return [
            {"trace_id": p.identity.trace_id,
             "matching_statutes": [s for s in p.reasoning.applicable_statutes if keyword.lower() in str(s).lower()],
             "recommendation_type": p.decision.recommendation_type, "evidence_id": p.identity.evidence_id}
            for p in evidence_repository.search_by_statute(keyword, limit=limit)
        ]

    def compare_evidence(self, trace_id_a: str, trace_id_b: str) -> Dict[str, Any]:
        pkg_a = evidence_repository.get_by_trace_id(trace_id_a)
        pkg_b = evidence_repository.get_by_trace_id(trace_id_b)
        if not pkg_a or not pkg_b:
            return {"compared": False, "reason": f"evidence not found: a={bool(pkg_a)}, b={bool(pkg_b)}"}
        return {"compared": True, "trace_id_a": trace_id_a, "trace_id_b": trace_id_b,
                "same_input_hash": pkg_a.hashes.input_hash == pkg_b.hashes.input_hash,
                "same_output_hash": pkg_a.hashes.output_hash == pkg_b.hashes.output_hash,
                "same_recommendation": pkg_a.decision.recommendation_type == pkg_b.decision.recommendation_type,
                "deterministic": pkg_a.hashes.input_hash == pkg_b.hashes.input_hash and pkg_a.hashes.output_hash == pkg_b.hashes.output_hash,
                "evidence_a_id": pkg_a.identity.evidence_id, "evidence_b_id": pkg_b.identity.evidence_id}

replay_engine = ReplayEngine()
