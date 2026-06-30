"""Phase V — Promotion pipeline tests (TestClient + X-API-Key)."""
import sys, os, uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("NYAI_API_KEY", "test-key-production-hardening")

import pytest
from fastapi.testclient import TestClient
from api.main import app
from tantra.output_bucket import output_bucket

client = TestClient(app, raise_server_exceptions=False)


def AUTH():
    return {"X-API-Key": os.environ["NYAI_API_KEY"]}


@pytest.fixture(autouse=True)
def _relax_rate_limits(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "100000")
    monkeypatch.setenv("RATE_LIMIT_BURST", "100000")
    yield


def _register(content=None):
    r = client.post("/knowledge/assets", json={
        "title": "Promo", "jurisdiction": "India", "domain": "civil",
        "source_attribution": "s", "content": content or {"v": 1},
    }, headers=AUTH())
    assert r.status_code == 200, r.text
    return r.json()


def _promote(asset_id, target, actor="tester", rationale="r"):
    return client.post(f"/knowledge/assets/{asset_id}/promote", json={
        "target_state": target, "actor": actor, "rationale": rationale,
    }, headers=AUTH())


def test_1_draft_to_review():
    a = _register()
    r = _promote(a["asset_id"], "REVIEW")
    assert r.status_code == 200, r.text
    assert r.json()["to_state"] == "REVIEW"


def test_2_review_to_approved():
    a = _register()
    _promote(a["asset_id"], "REVIEW")
    r = _promote(a["asset_id"], "APPROVED")
    assert r.status_code == 200, r.text
    assert r.json()["to_state"] == "APPROVED"


def test_3_invalid_transition_rejected():
    a = _register()
    r = _promote(a["asset_id"], "APPROVED")   # DRAFT -> APPROVED is invalid
    assert r.status_code in (400, 422), r.text


def test_4_rollback_creates_new_version():
    a = _register({"v": 1})
    aid, v1 = a["asset_id"], a["version_id"]
    client.patch(f"/knowledge/assets/{aid}", json={
        "updates": {"content": {"v": 2}}, "updated_by": "e"}, headers=AUTH())
    r = client.post(f"/knowledge/assets/{aid}/rollback", json={
        "target_version_id": v1, "actor": "e", "reason": "revert"}, headers=AUTH())
    assert r.status_code == 200, r.text
    latest = client.get(f"/knowledge/assets/{aid}", headers=AUTH()).json()
    assert latest["content"] == {"v": 1}
    versions = client.get(f"/knowledge/assets/{aid}/versions", headers=AUTH()).json()
    assert latest["identity"]["version_number"] == max(v["identity"]["version_number"] for v in versions)


def test_5_approval_audit_trail():
    a = _register()
    aid = a["asset_id"]
    _promote(aid, "REVIEW")
    _promote(aid, "APPROVED")
    _promote(aid, "ARCHIVED")
    r = client.get(f"/knowledge/assets/{aid}/approval-trail", headers=AUTH())
    assert r.status_code == 200, r.text
    assert r.json()["count"] == 3


def test_6_promotion_evidence_record():
    a = _register()
    r = _promote(a["asset_id"], "REVIEW")
    trace = r.json()["evidence_trace_id"]
    raw = output_bucket.retrieve(trace)
    assert raw is not None
    assert raw["full_response"]["knowledge_operation"] == "PROMOTE"


def test_7_rollback_evidence_record():
    a = _register({"v": 1})
    aid, v1 = a["asset_id"], a["version_id"]
    client.patch(f"/knowledge/assets/{aid}", json={
        "updates": {"content": {"v": 2}}, "updated_by": "e"}, headers=AUTH())
    r = client.post(f"/knowledge/assets/{aid}/rollback", json={
        "target_version_id": v1, "actor": "e", "reason": "revert"}, headers=AUTH())
    trace = r.json()["evidence_trace_id"]
    raw = output_bucket.retrieve(trace)
    assert raw is not None
    assert raw["full_response"]["knowledge_operation"] == "ROLLBACK"


def test_8_archived_is_terminal():
    a = _register()
    aid = a["asset_id"]
    r1 = _promote(aid, "ARCHIVED")   # DRAFT -> ARCHIVED is valid
    assert r1.status_code == 200, r1.text
    r2 = _promote(aid, "REVIEW")     # no transitions out of ARCHIVED
    assert r2.status_code == 400, r2.text
