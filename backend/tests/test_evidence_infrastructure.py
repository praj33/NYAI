import sys, os, json, hashlib, uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("NYAI_API_KEY", "test-nyai-key-phase4")
os.environ.setdefault("RATE_LIMIT_PER_MINUTE", "120")

import pytest
from fastapi.testclient import TestClient
from tantra.output_bucket import output_bucket
from evidence.models import EvidencePackage, EVIDENCE_SCHEMA_VERSION
from evidence.repository import EvidenceRepository
from evidence.replay_engine import ReplayEngine
from api.main import app

client = TestClient(app, raise_server_exceptions=False)

def AUTH():
    return {"X-API-Key": os.environ["NYAI_API_KEY"]}

def _make_entry() -> str:
    trace_id = f"test-ph4-{uuid.uuid4().hex[:8]}"
    ih = hashlib.sha256(f"input-{trace_id}".encode()).hexdigest()
    oh = hashlib.sha256(f"output-{trace_id}".encode()).hexdigest()
    output_bucket.store({
        "trace_id": trace_id, "request_id": str(uuid.uuid4()),
        "input_hash": ih, "timestamp": "2026-01-01T00:00:00",
        "schema_version": "tantra_v3", "answer_disclaimer": "test",
        "legal_context": {"jurisdiction": "India", "domain": "criminal", "applicable_laws": []},
        "domain": "criminal", "domains": ["criminal"],
        "jurisdiction": "India", "jurisdiction_detected": "India", "jurisdiction_confidence": 0.9,
        "confidence": {"overall": 0.8, "jurisdiction": 0.9, "domain": 0.8, "statute_match": 0.7, "procedural_match": 0.6},
        "facts": [{"fact_id": "f1", "statement": "Test", "source": "test"}],
        "analysis": {"issues_identified": [], "rule_application": [], "conflicts": []},
        "recommendation": {"type": "INFORM", "confidence": 0.8, "rationale": "test"},
        "explanation_chain": [{"step_number": 1, "description": "test", "source": "test"}],
        "risk_flags": [], "legal_route": ["r1"],
        "determinism_proof": {"input_hash": ih, "output_hash": oh, "version": "3.0.0"},
        "statutes": [{"act": "Indian Penal Code", "year": 1860, "section": "302", "title": "Murder"}],
        "case_laws": [], "constitutional_articles": [], "provenance_chain": [],
        "reasoning_trace": {"original_query": "test", "cleaned_query": "test"},
        "timeline": [], "glossary": [], "evidence_requirements": [],
        "remedies": [], "procedural_steps": [], "observer_steps": [], "observer_validation": None,
        "metadata": {"formatted": True, "formatter_version": "3.0.0", "formatted_at": "2026-01-01T00:00:00",
                     "schema_compliant": True, "canonical_fields_validated": 11,
                     "structural_fields_validated": 4, "schema": "tantra_v3", "validation_mode": "FAIL_CLOSED"},
    })
    return trace_id

def test_1_evidence_package_model():
    tid = _make_entry()
    raw = output_bucket.retrieve(tid)
    assert raw is not None
    pkg = EvidencePackage.from_stored_entry(raw)
    assert pkg.identity.trace_id == tid
    assert pkg.identity.schema_version == EVIDENCE_SCHEMA_VERSION
    assert len(pkg.identity.evidence_id) == 64
    d = pkg.to_dict()
    for k in ("identity", "decision", "reasoning", "hashes", "storage", "replay"):
        assert k in d

def test_1b_output_bucket_sequential_store_index():
    """Sequential stores must index each trace_id to the correct JSONL line."""
    tid_first = _make_entry()
    tid_second = _make_entry()
    first = output_bucket.retrieve(tid_first)
    second = output_bucket.retrieve(tid_second)
    assert first is not None and second is not None
    assert first["trace_id"] == tid_first
    assert second["trace_id"] == tid_second
    assert output_bucket._index[tid_second] == output_bucket._index[tid_first] + 1

def test_2_evidence_repository_get_by_trace_id():
    tid = _make_entry()
    repo = EvidenceRepository()
    pkg = repo.get_by_trace_id(tid)
    assert pkg is not None and pkg.identity.trace_id == tid
    raw = repo.get_raw_by_trace_id(tid)
    assert raw is not None and raw.get("trace_id") == tid

def test_3_get_evidence_endpoint():
    tid = _make_entry()
    r = client.get(f"/evidence/{tid}", headers=AUTH())
    assert r.status_code == 200, f"Got {r.status_code}: {r.text[:200]}"
    body = r.json()
    assert "identity" in body and "decision" in body and "hashes" in body
    assert body["identity"]["trace_id"] == tid

def test_4_evidence_search():
    _make_entry()
    r = client.get("/evidence/search?recommendation=INFORM&limit=5", headers=AUTH())
    assert r.status_code == 200, f"Got {r.status_code}: {r.text[:200]}"
    body = r.json()
    assert "results" in body and "total" in body

def test_5_evidence_integrity_verify():
    tid = _make_entry()
    r = client.post("/evidence/verify", json={"trace_id": tid}, headers=AUTH())
    assert r.status_code == 200, f"Got {r.status_code}: {r.text[:200]}"
    body = r.json()
    assert "verified" in body and "integrity_status" in body
    assert body["trace_id"] == tid
    assert body["integrity_status"] in ("VERIFIED", "TAMPERED", "UNKNOWN")

def test_6_replay_by_trace():
    tid = _make_entry()
    result = ReplayEngine().replay_by_trace(tid)
    assert result["replayed"] is True
    assert "evidence" in result and "integrity_status" in result

def test_7_secondary_endpoints_use_persistent_storage():
    tid = _make_entry()
    from api.router import response_cache
    with response_cache.lock:
        response_cache.cache.clear()
    r = client.get(f"/nyaya/case_summary?trace_id={tid}", headers=AUTH())
    assert r.status_code == 200, (
        f"case_summary returned {r.status_code} after cache clear -- "
        f"router.py Patch C was not applied to all 5 endpoints. Body: {r.text[:200]}"
    )
    assert r.json().get("trace_id") == tid

def test_8_evidence_export():
    tid = _make_entry()
    r = client.post("/evidence/export", json={"trace_id": tid, "format": "json"}, headers=AUTH())
    assert r.status_code == 200, f"Got {r.status_code}: {r.text[:200]}"
    assert r.json().get("export_format") == "nyai_evidence_v1"
    r2 = client.post("/evidence/export", json={"trace_id": tid, "format": "summary"}, headers=AUTH())
    assert r2.status_code == 200
    assert "evidence_id" in r2.json() and "input_hash" in r2.json()


def test_9_evidence_authentication_enforced():
    r = client.get("/evidence/search?limit=1")
    assert r.status_code == 401
    assert r.json().get("error_code") in ("UNAUTHORIZED", "INVALID_API_KEY")


def test_10_evidence_authentication_invalid_key():
    r = client.get("/evidence/search?limit=1", headers={"X-API-Key": "wrong-key"})
    assert r.status_code == 401
    assert r.json().get("error_code") == "INVALID_API_KEY"


def test_11_evidence_compare():
    tid_a = _make_entry()
    tid_b = _make_entry()
    r = client.post(
        "/evidence/compare",
        json={"trace_id_a": tid_a, "trace_id_b": tid_b},
        headers=AUTH(),
    )
    assert r.status_code == 200, f"Got {r.status_code}: {r.text[:200]}"
    body = r.json()
    assert body.get("compared") is True
    assert body.get("trace_id_a") == tid_a
    assert body.get("trace_id_b") == tid_b


def test_12_evidence_search_date_and_version():
    tid = _make_entry()
    repo = EvidenceRepository()
    raw = output_bucket.retrieve(tid)
    ts = raw["timestamp"]
    by_date = repo.search_by_date_range(ts[:10], ts, limit=10000)
    assert any(p.identity.trace_id == tid for p in by_date)
    assert any(p.identity.trace_id == tid for p in repo.search_by_evidence_version("1.0.0", limit=10000))
    r = client.get(f"/evidence/search?date_from={ts[:10]}&date_to={ts}&limit=1", headers=AUTH())
    assert r.status_code == 200, f"Got {r.status_code}: {r.text[:200]}"
    assert "total" in r.json() and "results" in r.json()
    r2 = client.get("/evidence/version/1.0.0", headers=AUTH())
    assert r2.status_code == 200
    assert r2.json().get("evidence_version") == "1.0.0"


def test_13_get_ledger_entry_for_trace():
    tid = _make_entry()
    repo = EvidenceRepository()
    entry = repo.get_ledger_entry_for_trace(tid)
    assert entry is None or isinstance(entry, dict)
