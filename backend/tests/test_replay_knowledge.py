"""Phase V — Replay tests for knowledge operations (stored-record replay)."""
import sys, os, uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("NYAI_API_KEY", "test-key-production-hardening")

import pytest
from fastapi.testclient import TestClient
from api.main import app
from ingestion.pipeline import ingestion_pipeline

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
        "title": "Replay", "jurisdiction": "India", "domain": "civil",
        "source_attribution": "s", "content": content or {"v": uuid.uuid4().hex},
    }, headers=AUTH())
    assert r.status_code == 200, r.text
    return r.json()


def test_1_knowledge_replay_by_trace():
    a = _register()
    r = client.get(f"/evidence/{a['trace_id']}", headers=AUTH())
    assert r.status_code == 200, r.text
    assert "identity" in r.json()
    assert r.json()["identity"]["trace_id"] == a["trace_id"]


def test_2_knowledge_ops_appear_in_replay_by_recommendation():
    _register()
    r = client.get("/evidence/recommendation/INFORM?limit=50", headers=AUTH())
    assert r.status_code == 200, r.text
    assert r.json()["count"] > 0


def test_3_ingestion_evidence_replayable():
    res = ingestion_pipeline.ingest(
        {"title": "T", "jurisdiction": "India", "domain": "civil",
         "source_attribution": "s", "content": {"text": uuid.uuid4().hex}},
        actor="u", jurisdiction="India", domain="civil", source_attribution="s",
    )
    assert res.status == "SUCCESS"
    r = client.get(f"/evidence/{res.trace_id}", headers=AUTH())
    assert r.status_code == 200, r.text


def test_4_promotion_evidence_replayable():
    a = _register()
    pr = client.post(f"/knowledge/assets/{a['asset_id']}/promote", json={
        "target_state": "REVIEW", "actor": "x", "rationale": "r"}, headers=AUTH()).json()
    r = client.get(f"/evidence/{pr['evidence_trace_id']}", headers=AUTH())
    assert r.status_code == 200, r.text


def test_5_rollback_evidence_replayable():
    a = _register({"v": 1})
    aid, v1 = a["asset_id"], a["version_id"]
    client.patch(f"/knowledge/assets/{aid}", json={
        "updates": {"content": {"v": 2}}, "updated_by": "e"}, headers=AUTH())
    rb = client.post(f"/knowledge/assets/{aid}/rollback", json={
        "target_version_id": v1, "actor": "e", "reason": "revert"}, headers=AUTH()).json()
    r = client.get(f"/evidence/{rb['evidence_trace_id']}", headers=AUTH())
    assert r.status_code == 200, r.text
