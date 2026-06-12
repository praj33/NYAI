"""
TANTRA Convergence Tests — convergence sprint verification suite.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient

from api.main import app
from tantra.output_bucket import output_bucket

client = TestClient(app)

CANONICAL_FIELDS = [
    "trace_id",
    "request_id",
    "input_hash",
    "legal_context",
    "facts",
    "analysis",
    "recommendation",
    "explanation_chain",
    "risk_flags",
    "determinism_proof",
    "timestamp",
]

CONTRACT_FIELDS = [
    "schema_version",
    "answer_disclaimer",
]

VALID_RECOMMENDATION_TYPES = {"INFORM", "REVIEW", "ESCALATE", "INSUFFICIENT_DATA"}

VALID_QUERY_PAYLOAD = {
    "query": "theft of mobile phone",
    "jurisdiction_hint": "India",
    "user_context": {"role": "citizen", "confidence_required": True},
}


def test_canonical_schema_valid_response():
    """POST /nyaya/query returns 200 with all 11 canonical fields and recommendation."""
    response = client.post("/nyaya/query", json=VALID_QUERY_PAYLOAD)
    assert response.status_code == 200
    data = response.json()

    for field in CANONICAL_FIELDS:
        assert field in data, f"Missing canonical field: {field}"
        assert data[field] is not None, f"Canonical field is None: {field}"

    for field in CONTRACT_FIELDS:
        assert field in data, f"Missing contract field: {field}"
        assert data[field] is not None, f"Contract field is None: {field}"

    assert data["schema_version"] == "tantra_v3"
    assert "advisory only" in data["answer_disclaimer"].lower()

    rec_type = data["recommendation"]["type"]
    assert rec_type in VALID_RECOMMENDATION_TYPES
    assert "enforcement_decision" not in data


def test_observer_blocks_invalid_schema():
    """Observer and ResponseBuilder must fail closed on invalid enriched response."""
    from observer.pipeline import ObserverPipeline
    from api.response_builder import ResponseBuilder, SchemaValidationError

    trace_id = "test-trace-invalid-schema"
    observer = ObserverPipeline(trace_id)
    invalid_response = {"trace_id": trace_id}

    result = observer.validate_response(invalid_response)
    assert not result.passed
    assert result.validation_status == "FAIL"
    assert len(result.violations) > 0

    builder = ResponseBuilder()
    with pytest.raises(SchemaValidationError):
        builder.build(invalid_response)


def test_trace_id_same_across_all_stages():
    """Stored output_bucket trace_id matches response trace_id."""
    response = client.post("/nyaya/query", json=VALID_QUERY_PAYLOAD)
    assert response.status_code == 200
    trace_id = response.json()["trace_id"]

    stored = output_bucket.retrieve(trace_id)
    assert stored is not None
    assert stored.get("trace_id") == trace_id
    full = stored.get("full_response") or {}
    assert full.get("trace_id") == trace_id


def test_trace_endpoint_returns_real_data():
    """GET /nyaya/trace/{trace_id} returns non-empty event_chain with tamper verification."""
    response = client.post("/nyaya/query", json=VALID_QUERY_PAYLOAD)
    assert response.status_code == 200
    trace_id = response.json()["trace_id"]

    trace_response = client.get(f"/nyaya/trace/{trace_id}")
    assert trace_response.status_code == 200
    data = trace_response.json()

    assert isinstance(data["event_chain"], list)
    assert len(data["event_chain"]) > 0
    assert data["tamper_verified"] is True
    assert data["input_hash"]
    assert len(data["input_hash"]) > 0


def test_output_bucket_retrieval_and_hash_verification():
    """GET /nyaya/output/{trace_id} returns verified stored output."""
    response = client.post("/nyaya/query", json=VALID_QUERY_PAYLOAD)
    assert response.status_code == 200
    trace_id = response.json()["trace_id"]

    output_response = client.get(f"/nyaya/output/{trace_id}")
    assert output_response.status_code == 200
    data = output_response.json()

    assert data["verification"]["verified"] is True
    assert data["hash_proof"]["tamper_detected"] is False
    assert data["hash_proof"]["input_hash"]
    assert len(data["hash_proof"]["input_hash"]) > 0


def test_hash_chain_ledger_reconstruct():
    """HashChainLedger supports append, verify, and reconstruct."""
    import tempfile
    import uuid
    from provenance_chain.hash_chain_ledger import HashChainLedger

    ledger_path = os.path.join(tempfile.gettempdir(), f"nyai_test_ledger_{uuid.uuid4().hex}.json")
    if os.path.exists(ledger_path):
        os.unlink(ledger_path)

    try:
        ledger = HashChainLedger(ledger_path)
        assert ledger.verify_chain_integrity() is True
        assert ledger.reconstruct() == []

        idx1 = ledger.append_event({"trace_id": "trace-a", "payload": "event-one"})
        idx2 = ledger.append_event({"trace_id": "trace-b", "payload": "event-two"})

        assert ledger.verify_chain_integrity() is True
        assert ledger.get_chain_length() == 3

        all_events = ledger.reconstruct()
        assert len(all_events) == 2
        assert all_events[0]["signed_event"]["trace_id"] == "trace-a"
        assert all_events[1]["signed_event"]["trace_id"] == "trace-b"

        filtered = ledger.reconstruct(trace_id="trace-a")
        assert len(filtered) == 1
        assert filtered[0]["index"] == idx1
        assert idx2 == 2
    finally:
        if os.path.exists(ledger_path):
            os.unlink(ledger_path)
