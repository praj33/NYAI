"""Verification service — evidence integrity and ledger chain checks."""
from __future__ import annotations

from typing import Any, Dict

from evidence.integrity import evidence_integrity


class VerificationService:
    def verify_by_trace_id(self, trace_id: str) -> Dict[str, Any]:
        return evidence_integrity.verify_by_trace_id(trace_id)

    def verify_chain(self) -> Dict[str, Any]:
        return evidence_integrity.verify_chain()


verification_service = VerificationService()
