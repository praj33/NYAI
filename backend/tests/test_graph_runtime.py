"""Phase V — Knowledge graph runtime tests (TestClient + X-API-Key)."""
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


def _entity(label, etype="concept"):
    r = client.post("/graph/entities", json={"entity_type": etype, "label": label}, headers=AUTH())
    assert r.status_code == 200, r.text
    return r.json()


def _rel(src, tgt, rtype="DEPENDS_ON"):
    r = client.post("/graph/relationships", json={
        "source_entity_id": src, "target_entity_id": tgt, "relationship_type": rtype,
    }, headers=AUTH())
    assert r.status_code == 200, r.text
    return r.json()


def test_1_register_entity():
    e = _entity("Alpha")
    assert uuid.UUID(e["entity_id"])
    assert e.get("evidence_trace_id")


def test_2_register_relationship():
    a = _entity("A2")
    b = _entity("B2")
    rel = _rel(a["entity_id"], b["entity_id"])
    assert rel.get("relationship_id")


def test_3_dependency_lookup():
    a, b, c = _entity("A3"), _entity("B3"), _entity("C3")
    _rel(a["entity_id"], b["entity_id"])
    _rel(b["entity_id"], c["entity_id"])
    r = client.get(f"/graph/entities/{a['entity_id']}/dependencies?depth=3", headers=AUTH())
    assert r.status_code == 200, r.text
    ids = {d["entity"]["entity_id"] for d in r.json()["dependencies"]}
    assert b["entity_id"] in ids and c["entity_id"] in ids


def test_4_impact_analysis():
    a, b, c = _entity("A4"), _entity("B4"), _entity("C4")
    _rel(a["entity_id"], b["entity_id"])
    _rel(b["entity_id"], c["entity_id"])
    r = client.get(f"/graph/entities/{c['entity_id']}/impact?depth=3", headers=AUTH())
    assert r.status_code == 200, r.text
    ids = {d["entity"]["entity_id"] for d in r.json()["impacted_entities"]}
    assert a["entity_id"] in ids and b["entity_id"] in ids


def test_5_citation_relationships():
    x, y = _entity("X5"), _entity("Y5")
    _rel(y["entity_id"], x["entity_id"], rtype="CITES")
    r = client.get(f"/graph/entities/{x['entity_id']}/citations", headers=AUTH())
    assert r.status_code == 200, r.text
    ids = {c["entity"]["entity_id"] for c in r.json()["citations"]}
    assert y["entity_id"] in ids


def test_6_path_finding():
    a, b, c = _entity("A6"), _entity("B6"), _entity("C6")
    _rel(a["entity_id"], b["entity_id"])
    _rel(b["entity_id"], c["entity_id"])
    r = client.get(
        f"/graph/path?source_entity_id={a['entity_id']}&target_entity_id={c['entity_id']}",
        headers=AUTH(),
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["found"] is True
    assert len(body["path"]) == 3


def test_7_no_loop_traversal():
    a, b = _entity("A7"), _entity("B7")
    _rel(a["entity_id"], b["entity_id"])
    _rel(b["entity_id"], a["entity_id"])   # cycle
    r = client.get(f"/graph/entities/{a['entity_id']}/dependencies?depth=5", headers=AUTH())
    assert r.status_code == 200, r.text
    ids = {d["entity"]["entity_id"] for d in r.json()["dependencies"]}
    assert b["entity_id"] in ids


def test_8_graph_evidence_records():
    e = _entity("Evidence8")
    raw = output_bucket.retrieve(e["evidence_trace_id"])
    assert raw is not None
    assert raw["full_response"]["knowledge_operation"] == "GRAPH_OP"
