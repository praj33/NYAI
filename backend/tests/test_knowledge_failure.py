"""Phase V — Failure / rollback / validation tests (TestClient + X-API-Key)."""
import sys, os, uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("NYAI_API_KEY", "test-key-production-hardening")

import pytest
from fastapi.testclient import TestClient
from api.main import app

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
        "title": "F", "jurisdiction": "India", "domain": "civil",
        "source_attribution": "s", "content": {"v": 1},
    }, headers=AUTH())
    assert r.status_code == 200, r.text
    return r.json()


def test_1_register_asset_missing_required_field():
    r = client.post("/knowledge/assets", json={"jurisdiction": "India"}, headers=AUTH())
    assert r.status_code == 422


def test_2_get_nonexistent_asset():
    r = client.get("/knowledge/assets/does-not-exist", headers=AUTH())
    assert r.status_code == 404


def test_3_invalid_promotion_state():
    a = _register()
    r = client.post(f"/knowledge/assets/{a['asset_id']}/promote", json={
        "target_state": "PUBLISHED", "actor": "x", "rationale": "r"}, headers=AUTH())
    assert r.status_code in (400, 422)


def test_4_promote_archived_asset():
    a = _register()
    aid = a["asset_id"]
    r1 = client.post(f"/knowledge/assets/{aid}/promote", json={
        "target_state": "ARCHIVED", "actor": "x", "rationale": "r"}, headers=AUTH())
    assert r1.status_code == 200
    r2 = client.post(f"/knowledge/assets/{aid}/promote", json={
        "target_state": "REVIEW", "actor": "x", "rationale": "r"}, headers=AUTH())
    assert r2.status_code == 400


def test_5_rollback_to_nonexistent_version():
    a = _register()
    r = client.post(f"/knowledge/assets/{a['asset_id']}/rollback", json={
        "target_version_id": "nope", "actor": "x", "reason": "r"}, headers=AUTH())
    assert r.status_code == 404


def test_6_graph_relationship_invalid_entity():
    e = client.post("/graph/entities", json={"entity_type": "concept", "label": "Solo"}, headers=AUTH()).json()
    r = client.post("/graph/relationships", json={
        "source_entity_id": "missing-source", "target_entity_id": e["entity_id"],
        "relationship_type": "DEPENDS_ON"}, headers=AUTH())
    assert r.status_code == 404


def test_7_duplicate_entity_type_list():
    r = client.get(f"/graph/entities?entity_type=nonexistent-{uuid.uuid4().hex}", headers=AUTH())
    assert r.status_code == 200
    assert r.json()["entities"] == []


def test_8_workspace_upload_missing_content():
    r = client.post("/workspace/documents/upload", json={
        "asset_id": str(uuid.uuid4()), "filename": "f.json", "uploaded_by": "u"}, headers=AUTH())
    assert r.status_code == 422
