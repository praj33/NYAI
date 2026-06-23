from __future__ import annotations
import hashlib, json, logging
from typing import Any, Dict
from tantra.output_bucket import output_bucket

logger = logging.getLogger("nyai.evidence.integrity")

class EvidenceIntegrity:
    def verify_by_trace_id(self, trace_id: str) -> Dict[str, Any]:
        raw = output_bucket.retrieve(trace_id)
        if not raw:
            return {"verified": False, "trace_id": trace_id, "reason": "evidence_not_found", "integrity_status": "UNKNOWN"}
        return self._verify_entry(raw)

    def _verify_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        trace_id = entry.get("trace_id", "UNKNOWN")
        stored_hash = entry.get("entry_hash", "")
        entry_copy = {k: v for k, v in entry.items() if k != "entry_hash"}
        recomputed = hashlib.sha256(
            json.dumps(entry_copy, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()
        tampered = recomputed != stored_hash
        return {
            "verified": not tampered, "trace_id": trace_id,
            "stored_entry_hash": stored_hash, "recomputed_entry_hash": recomputed,
            "tamper_detected": tampered,
            "integrity_status": "TAMPERED" if tampered else "VERIFIED",
        }

    def verify_chain(self) -> Dict[str, Any]:
        try:
            from provenance_chain.hash_chain_ledger import HashChainLedger
            ledger = HashChainLedger()
            chain_valid = ledger.verify_chain_integrity()
            return {"chain_valid": chain_valid, "chain_length": ledger.get_chain_length(),
                    "integrity_status": "VERIFIED" if chain_valid else "BROKEN"}
        except Exception as e:
            return {"chain_valid": False, "chain_length": 0, "integrity_status": "ERROR", "error": str(e)}

evidence_integrity = EvidenceIntegrity()
