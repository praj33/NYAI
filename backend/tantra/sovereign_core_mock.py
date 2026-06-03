"""
Mock Sovereign Core — Temporary TANTRA downstream consumer.
Receives NYAI output, validates schema, logs receipt, returns acknowledgment.
"""
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List


CANONICAL_FIELDS = [
    "trace_id", "request_id", "input_hash", "legal_context",
    "facts", "analysis", "recommendation", "explanation_chain",
    "risk_flags", "determinism_proof", "timestamp",
]


class SovereignCoreMock:
    """
    Mock Sovereign Core that:
    - Receives NYAI output
    - Validates schema presence
    - Validates trace_id continuity
    - Logs receipt
    - Returns acknowledgment with trace_id
    """

    def __init__(self):
        self._receipts: List[Dict[str, Any]] = []

    def receive(self, nyai_output: Dict[str, Any], expected_trace_id: str = None) -> Dict[str, Any]:
        """
        Process NYAI output as Sovereign Core would.
        Returns acknowledgment or rejection.
        """
        trace_id = nyai_output.get("trace_id", "UNKNOWN")
        violations = []

        # 1. Schema presence check
        for field in CANONICAL_FIELDS:
            if field not in nyai_output or nyai_output[field] is None:
                violations.append(f"SOVEREIGN_REJECT: missing field '{field}'")

        # 2. Trace continuity check
        if expected_trace_id and trace_id != expected_trace_id:
            violations.append(
                f"SOVEREIGN_REJECT: trace_id mismatch expected='{expected_trace_id}' got='{trace_id}'"
            )

        # 3. Input hash presence
        proof = nyai_output.get("determinism_proof", {})
        if isinstance(proof, dict):
            input_hash = proof.get("input_hash", "")
            output_hash = proof.get("output_hash", "")
        else:
            input_hash = getattr(proof, "input_hash", "")
            output_hash = getattr(proof, "output_hash", "")

        if not input_hash or not output_hash:
            violations.append("SOVEREIGN_REJECT: determinism_proof missing hashes")

        # Build receipt
        receipt = {
            "sovereign_core": "MOCK",
            "trace_id": trace_id,
            "received_at": datetime.utcnow().isoformat(),
            "input_hash_received": input_hash,
            "output_hash_received": output_hash,
            "schema_fields_present": len(CANONICAL_FIELDS) - len([v for v in violations if "missing field" in v]),
            "schema_fields_required": len(CANONICAL_FIELDS),
            "violations": violations,
            "accepted": len(violations) == 0,
            "status": "ACCEPTED" if len(violations) == 0 else "REJECTED",
        }

        self._receipts.append(receipt)
        return receipt

    def get_receipts(self) -> List[Dict[str, Any]]:
        """Return all receipts."""
        return list(self._receipts)


# Module-level singleton
sovereign_core = SovereignCoreMock()
