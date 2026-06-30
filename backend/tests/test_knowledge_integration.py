"""Phase V — Integration tests: knowledge layer + Phase IV evidence infra."""
import sys, os, uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("NYAI_API_KEY", "test-key-production-hardening")

import pytest
from fastapi.testclient import TestClient
from api.main import app
from evidence.repository import evidence_repository

client = TestClient(app, raise_server_exceptions=False)


def AUTH():
    return {"X-API-Key": os.environ["NYAI_API_KEY"]}


@pytest.fixture(autouse=True)
def _relax_rate_limits(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "100000")
    monkeypatch.setenv("RATE_LIMIT_BURST", "100000")
    yield


def _register():
    r = client.post("/knowledge/assets", json={
        "title": "Int", "jurisdiction": "India", "domain": "civil",
        "source_attribution": "s", "content": {"v": uuid.uuid4().hex},
    }, headers=AUTH())
    assert r.status_code == 200, r.text
    return r.json()


def test_1_knowledge_op_appears_in_evidence_search():
    _register()
    r = client.get("/evidence/search?recommendation=INFORM&limit=100", headers=AUTH())
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total"] > 0


def test_2_knowledge_evidence_verifiable():
    a = _register()
    r = client.post("/evidence/verify", json={"trace_id": a["trace_id"]}, headers=AUTH())
    assert r.status_code == 200, r.text
    assert r.json()["verified"] is True


def test_3_existing_nyaya_query_unaffected():
    payload = {
        "query": "theft of mobile phone",
        "jurisdiction_hint": "India",
        "user_context": {"role": "citizen", "confidence_required": True},
    }
    r = client.post("/nyaya/query", json=payload, headers=AUTH())
    assert r.status_code == 200, r.text[:300]
    body = r.json()
    canonical = ["trace_id", "request_id", "input_hash", "legal_context", "facts",
                 "analysis", "recommendation", "explanation_chain", "risk_flags",
                 "determinism_proof", "timestamp"]
    for field in canonical:
        assert field in body, f"missing canonical field {field}"
    assert evidence_repository.get_by_trace_id(body["trace_id"]) is not None


def test_4_health_ready_includes_knowledge():
    r = client.get("/health/ready")
    assert r.status_code in (200, 503)
    deps = r.json()["dependencies"]
    assert "knowledge_repository" in deps
    assert deps["knowledge_repository"]["status"] == "PASS"


def test_5_backward_compat_evidence_endpoints():
    a = _register()
    b = _register()
    ta, tb = a["trace_id"], b["trace_id"]
    checks = [
        client.get("/evidence/search?limit=1", headers=AUTH()),
        client.get(f"/evidence/hash/{uuid.uuid4().hex}", headers=AUTH()),
        client.get("/evidence/recommendation/INFORM?limit=1", headers=AUTH()),
        client.get("/evidence/jurisdiction/India?limit=1", headers=AUTH()),
        client.get("/evidence/statute?keyword=test&limit=1", headers=AUTH()),
        client.get("/evidence/version/1.0.0?limit=1", headers=AUTH()),
        client.post("/evidence/verify", json={"trace_id": ta}, headers=AUTH()),
        client.post("/evidence/verify/chain", headers=AUTH()),
        client.post("/evidence/compare", json={"trace_id_a": ta, "trace_id_b": tb}, headers=AUTH()),
        client.post("/evidence/export", json={"trace_id": ta, "format": "json"}, headers=AUTH()),
        client.get(f"/evidence/{ta}", headers=AUTH()),
        client.get(f"/evidence/{uuid.uuid4()}", headers=AUTH()),
    ]
    for resp in checks:
        assert resp.status_code in (200, 404), f"{resp.request.url} -> {resp.status_code}: {resp.text[:160]}"


def test_6_evidence_chain_integrity_after_knowledge_ops():
    for _ in range(3):
        _register()
    r = client.post("/evidence/verify/chain", headers=AUTH())
    assert r.status_code == 200, r.text
    assert "chain_valid" in r.json()
