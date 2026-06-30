"""Phase V — Workspace API tests (TestClient + X-API-Key)."""
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


def _upload(asset_id=None, content=None, metadata=None):
    body = {
        "asset_id": asset_id or str(uuid.uuid4()),
        "filename": "doc.json",
        "content_type": "application/json",
        "content": content or {"text": "hello", "n": 1},
        "metadata": metadata or {"status": "draft"},
        "uploaded_by": "tester",
    }
    return client.post("/workspace/documents/upload", json=body, headers=AUTH())


def test_1_upload_document():
    r = _upload()
    assert r.status_code == 200, r.text
    body = r.json()
    assert "doc_id" in body and body["doc_id"]
    assert body.get("evidence_trace_id")


def test_2_update_metadata():
    up = _upload().json()
    r = client.patch(
        f"/workspace/documents/{up['doc_id']}/metadata",
        json={"metadata": {"status": "review"}, "actor": "rev"},
        headers=AUTH(),
    )
    assert r.status_code == 200, r.text
    assert r.json()["metadata"]["status"] == "review"


def test_3_add_annotation():
    up = _upload().json()
    r = client.post("/workspace/annotations", json={
        "doc_id": up["doc_id"], "asset_id": up["asset_id"],
        "annotation_type": "COMMENT", "content": "looks good", "author": "rev",
    }, headers=AUTH())
    assert r.status_code == 200, r.text
    assert r.json().get("annotation_id")


def test_4_get_annotations_for_document():
    up = _upload().json()
    client.post("/workspace/annotations", json={
        "doc_id": up["doc_id"], "asset_id": up["asset_id"],
        "annotation_type": "REVIEW_NOTE", "content": "note", "author": "rev",
    }, headers=AUTH())
    r = client.get(f"/workspace/documents/{up['doc_id']}/annotations", headers=AUTH())
    assert r.status_code == 200, r.text
    anns = r.json()
    assert len(anns) >= 1
    assert anns[0]["doc_id"] == up["doc_id"]


def test_5_version_history():
    asset_id = str(uuid.uuid4())
    up = _upload(asset_id=asset_id).json()
    d2 = client.patch(f"/workspace/documents/{up['doc_id']}/metadata",
                      json={"metadata": {"r": 1}, "actor": "a"}, headers=AUTH()).json()
    client.patch(f"/workspace/documents/{d2['doc_id']}/metadata",
                 json={"metadata": {"r": 2}, "actor": "a"}, headers=AUTH())
    r = client.get(f"/workspace/documents/{asset_id}/versions", headers=AUTH())
    assert r.status_code == 200, r.text
    assert len(r.json()) == 3


def test_6_compare_versions():
    asset_id = str(uuid.uuid4())
    a = _upload(asset_id=asset_id, content={"x": 1, "y": 2}).json()
    b = _upload(asset_id=asset_id, content={"x": 1, "y": 99, "z": 3}).json()
    r = client.get(f"/workspace/documents/{a['doc_id']}/compare/{b['doc_id']}", headers=AUTH())
    assert r.status_code == 200, r.text
    assert len(r.json()["differences"]) > 0


def test_7_audit_history():
    asset_id = str(uuid.uuid4())
    up = _upload(asset_id=asset_id).json()
    client.patch(f"/workspace/documents/{up['doc_id']}/metadata",
                 json={"metadata": {"r": 1}, "actor": "a"}, headers=AUTH())
    client.post("/workspace/annotations", json={
        "doc_id": up["doc_id"], "asset_id": asset_id,
        "annotation_type": "FLAG", "content": "flagged", "author": "rev",
    }, headers=AUTH())
    r = client.get(f"/workspace/documents/{up['doc_id']}/audit", headers=AUTH())
    assert r.status_code == 200, r.text
    assert len(r.json()) >= 3


def test_8_auth_required():
    r = client.get(f"/workspace/documents/{uuid.uuid4()}/annotations")
    assert r.status_code in (401, 403)
