"""Generate convergence proof JSON artifacts for sprint deliverables."""
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient

from api.main import app
from tantra.sovereign_core_mock import SovereignCoreMock
from tantra.output_bucket import output_bucket
from provenance_chain.hash_chain_ledger import ledger

DELIVERABLES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "SHASHANK-NYAI_CONVERGENCE_IMPLEMENTATION_PLAN",
)

VALID_QUERY_PAYLOAD = {
    "query": "theft of mobile phone",
    "jurisdiction_hint": "India",
    "user_context": {"role": "citizen", "confidence_required": True},
}


def main():
    client = TestClient(app)
    generated_at = datetime.utcnow().isoformat() + "Z"

    query_resp = client.post("/nyaya/query", json=VALID_QUERY_PAYLOAD)
    assert query_resp.status_code == 200, query_resp.text
    nyai_output = query_resp.json()
    trace_id = nyai_output["trace_id"]

    trace_resp = client.get(f"/nyaya/trace/{trace_id}")
    assert trace_resp.status_code == 200, trace_resp.text
    trace_data = trace_resp.json()

    output_resp = client.get(f"/nyaya/output/{trace_id}")
    assert output_resp.status_code == 200, output_resp.text
    output_data = output_resp.json()

    core = SovereignCoreMock()
    sovereign_receipt = core.receive(nyai_output, expected_trace_id=trace_id)
    bucket_verification = output_bucket.verify(trace_id)
    ledger_events = ledger.reconstruct(trace_id=trace_id)

    flow_proof = {
        "status": "PASS" if sovereign_receipt.get("accepted") and bucket_verification.get("verified") else "FAIL",
        "trace_id": trace_id,
        "generated_at": generated_at,
        "sovereign_receipt": sovereign_receipt,
        "bucket_verified": bucket_verification.get("verified", False),
        "trace_continuity": trace_id == sovereign_receipt.get("trace_id"),
        "input_hash_continuity": nyai_output.get("input_hash") == sovereign_receipt.get("input_hash_received"),
        "flow_proof": {
            "flow": "TANTRA",
            "trace_id": trace_id,
            "input_hash": nyai_output.get("input_hash"),
            "stages": {
                "nyai_response": {
                    "trace_id": trace_id,
                    "input_hash": nyai_output.get("input_hash"),
                    "output_hash": (nyai_output.get("determinism_proof") or {}).get("output_hash"),
                    "recommendation": nyai_output.get("recommendation"),
                    "schema_version": nyai_output.get("schema_version"),
                    "answer_disclaimer": nyai_output.get("answer_disclaimer"),
                },
                "sovereign_core": sovereign_receipt,
                "verification": bucket_verification,
                "ledger_events": ledger_events,
            },
            "flow_status": "PASS" if sovereign_receipt.get("accepted") and bucket_verification.get("verified") else "FAIL",
        },
        "authority_note": "Advisory participation only. No enforcement authority transferred.",
    }

    trace_replay_proof = {
        **trace_data,
        "generated_at": generated_at,
        "query_trace_id": trace_id,
        "trace_continuity_verified": all(
            step.get("trace_id") == trace_id for step in trace_data.get("event_chain", [])
        ),
    }

    output_proof = {
        **output_data,
        "generated_at": generated_at,
        "query_trace_id": trace_id,
    }

    os.makedirs(DELIVERABLES_DIR, exist_ok=True)
    artifacts = {
        "tantra_flow_proof.json": flow_proof,
        "trace_replay_proof.json": trace_replay_proof,
        "output_proof.json": output_proof,
    }
    for filename, payload in artifacts.items():
        path = os.path.join(DELIVERABLES_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, default=str)
        print(f"Wrote {path}")

    summary = {
        "trace_id": trace_id,
        "input_hash": nyai_output.get("input_hash"),
        "output_hash": (nyai_output.get("determinism_proof") or {}).get("output_hash"),
        "recommendation_type": (nyai_output.get("recommendation") or {}).get("type"),
        "schema_version": nyai_output.get("schema_version"),
        "flow_status": flow_proof["status"],
        "tamper_verified": trace_data.get("tamper_verified"),
        "bucket_verified": bucket_verification.get("verified"),
        "ledger_event_count": len(ledger_events),
        "generated_at": generated_at,
    }
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    main()
