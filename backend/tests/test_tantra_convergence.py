"""
TANTRA Convergence Tests — exactly 5 tests verifying convergence sprint outcomes.
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

    rec_type = data["recommendation"]["type"]
    assert rec_type in VALID_RECOMMENDATION_TYPES
    assert "enforcement_decision" not in data


def test_observer_blocks_invalid_schema():
    """Invalid schema payload must fail closed — not return 200."""
    response = client.post("/nyaya/query", json={})
    assert response.status_code in {400, 422, 500}


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
