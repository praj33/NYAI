"""
Production hardening tests — API auth, rate limiting, health, logging, metrics.
"""
import json
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["NYAI_API_KEY"] = "test-key-production-hardening"
os.environ["RATE_LIMIT_PER_MINUTE"] = "5"

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.metrics import metrics_store
from api.error_codes import ErrorCode

client = TestClient(app, raise_server_exceptions=False)

VALID_QUERY_PAYLOAD = {
    "query": "theft of mobile phone",
    "jurisdiction_hint": "India",
    "user_context": {"role": "citizen", "confidence_required": True},
}

FEEDBACK_PAYLOAD = {
    "trace_id": "550e8400-e29b-41d4-a716-446655440000",
    "rating": 5,
    "feedback_type": "clarity",
}

MOCK_TANTRA_FLOW_RESULT = {
    "flow_status": "PASS",
    "trace_id": "test-trace-id",
    "input_hash": "abc",
    "stages": {
        "sovereign_core": {"accepted": True, "trace_id": "test-trace-id"},
        "nyai_response": {},
        "output_bucket": {},
        "verification": {},
    },
    "trace_continuity": True,
    "input_hash_continuity": True,
    "sovereign_accepted": True,
    "bucket_verified": True,
}

AUTH_HEADERS = {"X-API-Key": "test-key-production-hardening"}


def test_authentication_enforced():
    response = client.post("/nyaya/query", json=VALID_QUERY_PAYLOAD)
    assert response.status_code == 401
    body = response.json()
    assert body["error_code"] in (ErrorCode.UNAUTHORIZED,)
    assert "trace_id" in body


def test_authentication_bypass_impossible():
    cases = [
        {"X-API-Key": "completely-wrong-key"},
        {"X-API-Key": ""},
        None,
        {"X-API-Key": "' OR '1'='1"},
        {"X-API-Key": "A" * 10000},
    ]
    for headers in cases:
        kwargs = {"json": VALID_QUERY_PAYLOAD}
        if headers is not None:
            kwargs["headers"] = headers
        response = client.post("/nyaya/query", **kwargs)
        assert response.status_code == 401


def test_rate_limit_triggers():
    responses = []
    for _ in range(6):
        responses.append(
            client.post(
                "/nyaya/query",
                json=VALID_QUERY_PAYLOAD,
                headers=AUTH_HEADERS,
            )
        )

    for response in responses[:5]:
        assert response.status_code != 429

    sixth = responses[5]
    assert sixth.status_code == 429
    body = sixth.json()
    assert body["error_code"] == ErrorCode.RATE_LIMIT_EXCEEDED
    assert "Retry-After" in sixth.headers


def test_health_endpoints_pass():
    for path in ("/health", "/health/live", "/health/ready"):
        response = client.get(path)
        assert response.status_code == 200

    health = client.get("/health").json()
    assert "status" in health

    ready = client.get("/health/ready").json()
    assert "dependencies" in ready
    assert isinstance(ready["dependencies"], dict)


def test_health_endpoint_detects_dependency_failure():
    from tantra import output_bucket as output_bucket_module

    original = output_bucket_module.output_bucket.retrieve

    def failing_retrieve(trace_id):
        raise RuntimeError("simulated bucket failure")

    output_bucket_module.output_bucket.retrieve = failing_retrieve
    try:
        response = client.get("/health/ready")
        body = response.json()
        assert body["dependencies"]["output_bucket"]["status"] == "FAIL"
        assert body["status"] in ("degraded", "unavailable")
        assert response.status_code in (200, 503)
        if response.status_code == 503:
            assert body["error_code"] == ErrorCode.DEPENDENCY_FAILURE
    finally:
        output_bucket_module.output_bucket.retrieve = original


def test_health_endpoint_detects_ledger_failure():
    from provenance_chain.hash_chain_ledger import HashChainLedger

    original = HashChainLedger.verify_chain_integrity

    def failing_verify(self):
        raise RuntimeError("simulated ledger failure")

    HashChainLedger.verify_chain_integrity = failing_verify
    try:
        response = client.get("/health/ready")
        body = response.json()
        assert body["dependencies"]["ledger"]["status"] == "FAIL"
        assert body["status"] == "unavailable"
        assert response.status_code == 503
        assert body["error_code"] == ErrorCode.DEPENDENCY_FAILURE
    finally:
        HashChainLedger.verify_chain_integrity = original


def test_structured_logging_contains_trace_id(caplog):
    caplog.set_level(logging.INFO, logger="nyai.access")
    response = client.post(
        "/nyaya/query",
        json=VALID_QUERY_PAYLOAD,
        headers=AUTH_HEADERS,
    )
    assert response.status_code in (200, 422, 429, 500, 503)

    matched = False
    for record in caplog.records:
        if record.name != "nyai.access":
            continue
        try:
            payload = json.loads(record.getMessage())
        except json.JSONDecodeError:
            continue
        if payload.get("trace_id") and payload.get("endpoint"):
            assert isinstance(payload["trace_id"], str)
            assert payload["trace_id"] != "unknown"
            assert "duration_ms" in payload
            matched = True
            break

    assert matched, "Expected structured log entry with trace_id"


def test_metrics_endpoint_updates():
    metrics_store.reset_counters()
    initial = client.get("/metrics").json()
    initial_auth_failures = initial["requests"]["auth_failures"]

    client.post("/nyaya/query", json=VALID_QUERY_PAYLOAD)

    updated = client.get("/metrics").json()
    assert updated["requests"]["auth_failures"] > initial_auth_failures
    assert isinstance(updated["active_requests"], int)
    assert updated["uptime_seconds"] > 0


def test_deployment_validation_scenarios_pass():
    original_key = os.environ.get("NYAI_API_KEY")
    try:
        if "NYAI_API_KEY" in os.environ:
            del os.environ["NYAI_API_KEY"]
        missing_key_response = client.post("/nyaya/query", json=VALID_QUERY_PAYLOAD)
        assert missing_key_response.status_code in (401, 503)
    finally:
        if original_key is not None:
            os.environ["NYAI_API_KEY"] = original_key
        else:
            os.environ["NYAI_API_KEY"] = "test-key-production-hardening"

    rate_responses = [
        client.post("/nyaya/query", json=VALID_QUERY_PAYLOAD, headers=AUTH_HEADERS)
        for _ in range(6)
    ]
    assert any(r.status_code == 429 for r in rate_responses)

    from api.rate_limiter import reset_rate_limiter

    reset_rate_limiter()
    invalid = client.post(
        "/nyaya/query",
        json=VALID_QUERY_PAYLOAD,
        headers={"X-API-Key": "invalid"},
    )
    assert invalid.status_code == 401
    assert invalid.json()["error_code"] == ErrorCode.INVALID_API_KEY

    ready = client.get("/health/ready")
    assert ready.status_code in (200, 503)
    body = ready.json()
    assert "status" in body


def test_tantra_flow_authentication_enforced():
    response = client.post("/nyaya/tantra_flow", json=VALID_QUERY_PAYLOAD)
    assert response.status_code == 401
    body = response.json()
    assert body["error_code"] == ErrorCode.UNAUTHORIZED
    assert "trace_id" in body


def test_feedback_authentication_enforced():
    response = client.post("/nyaya/feedback", json=FEEDBACK_PAYLOAD)
    assert response.status_code == 401
    body = response.json()
    assert body["error_code"] == ErrorCode.UNAUTHORIZED
    assert "trace_id" in body


def test_tantra_flow_authentication_bypass_impossible():
    cases = [
        {"X-API-Key": "wrong-key"},
        {"X-API-Key": ""},
        None,
    ]
    for headers in cases:
        kwargs = {"json": VALID_QUERY_PAYLOAD}
        if headers is not None:
            kwargs["headers"] = headers
        response = client.post("/nyaya/tantra_flow", **kwargs)
        assert response.status_code == 401


def test_feedback_authentication_bypass_impossible():
    cases = [
        {"X-API-Key": "wrong-key"},
        {"X-API-Key": ""},
        None,
    ]
    for headers in cases:
        kwargs = {"json": FEEDBACK_PAYLOAD}
        if headers is not None:
            kwargs["headers"] = headers
        response = client.post("/nyaya/feedback", **kwargs)
        assert response.status_code == 401


def test_rate_limit_triggers_on_feedback():
    responses = []
    for _ in range(6):
        responses.append(
            client.post(
                "/nyaya/feedback",
                json=FEEDBACK_PAYLOAD,
                headers=AUTH_HEADERS,
            )
        )

    for response in responses[:5]:
        assert response.status_code != 429

    sixth = responses[5]
    assert sixth.status_code == 429
    assert sixth.json()["error_code"] == ErrorCode.RATE_LIMIT_EXCEEDED


def test_rate_limit_triggers_on_tantra_flow(monkeypatch):
    monkeypatch.setattr("api.router.run_tantra_flow", lambda *args, **kwargs: MOCK_TANTRA_FLOW_RESULT)

    responses = []
    for _ in range(6):
        responses.append(
            client.post(
                "/nyaya/tantra_flow",
                json=VALID_QUERY_PAYLOAD,
                headers=AUTH_HEADERS,
            )
        )

    for response in responses[:5]:
        assert response.status_code != 429

    sixth = responses[5]
    assert sixth.status_code == 429
    assert sixth.json()["error_code"] == ErrorCode.RATE_LIMIT_EXCEEDED
