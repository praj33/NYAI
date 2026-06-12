"""
TANTRA Flow — End-to-end execution:
Input → NYAI → Mock Sovereign Core → Output Bucket → Verification

Same trace_id, same input_hash, no mutation between stages.
"""
import json
import hashlib
import urllib.request
from datetime import datetime
from typing import Dict, Any

from tantra.sovereign_core_mock import SovereignCoreMock
from tantra.output_bucket import OutputBucket


def run_tantra_flow(
    query: str,
    jurisdiction_hint: str = "India",
    nyai_url: str = "http://127.0.0.1:8000/nyaya/query",
) -> Dict[str, Any]:
    """
    Execute a full TANTRA flow:
    1. Send query to NYAI
    2. Forward output to Mock Sovereign Core
    3. Store in Output Bucket
    4. Verify stored output
    """
    flow_start = datetime.utcnow().isoformat()

    # ─── Stage 1: Send to NYAI ───
    payload = {
        "query": query,
        "jurisdiction_hint": jurisdiction_hint,
        "user_context": {"role": "citizen", "confidence_required": True}
    }

    req = urllib.request.Request(
        nyai_url,
        json.dumps(payload).encode('utf-8'),
        {'Content-Type': 'application/json'}
    )
    resp = urllib.request.urlopen(req, timeout=120)
    nyai_output = json.loads(resp.read())

    trace_id = nyai_output.get("trace_id", "UNKNOWN")
    input_hash = nyai_output.get("input_hash", "")

    # ─── Stage 2: Forward to Sovereign Core ───
    core = SovereignCoreMock()
    sovereign_receipt = core.receive(nyai_output, expected_trace_id=trace_id)

    # ─── Stage 3: Store in Output Bucket ───
    bucket = OutputBucket()
    storage_receipt = bucket.store(nyai_output)

    # ─── Stage 4: Verify from Bucket ───
    verification = bucket.verify(trace_id)

    # ─── Assemble flow proof ───
    flow_proof = {
        "flow": "TANTRA",
        "flow_start": flow_start,
        "flow_end": datetime.utcnow().isoformat(),
        "trace_id": trace_id,
        "input_hash": input_hash,
        "stages": {
            "nyai_response": {
                "trace_id": trace_id,
                "input_hash": input_hash,
                "output_hash": nyai_output.get("determinism_proof", {}).get("output_hash", ""),
                "recommendation": nyai_output.get("recommendation", {}),
                "facts_count": len(nyai_output.get("facts", [])),
                "schema_fields_present": sum(
                    1 for f in [
                        "trace_id", "request_id", "input_hash", "legal_context",
                        "facts", "analysis", "recommendation", "explanation_chain",
                        "risk_flags", "determinism_proof", "timestamp"
                    ] if f in nyai_output
                ),
            },
            "sovereign_core": sovereign_receipt,
            "output_bucket": storage_receipt,
            "verification": verification,
        },
        "trace_continuity": trace_id == sovereign_receipt.get("trace_id"),
        "input_hash_continuity": input_hash == sovereign_receipt.get("input_hash_received"),
        "sovereign_accepted": sovereign_receipt.get("accepted", False),
        "bucket_verified": verification.get("verified", False),
        "flow_status": "PASS" if (
            sovereign_receipt.get("accepted", False)
            and verification.get("verified", False)
            and trace_id == sovereign_receipt.get("trace_id")
        ) else "FAIL",
    }

    return flow_proof
