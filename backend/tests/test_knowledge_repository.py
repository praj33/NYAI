"""Phase V — Knowledge repository unit tests."""
import sys, os, json, uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("NYAI_API_KEY", "test-key-production-hardening")

import pytest

from knowledge.models import KnowledgeAsset, new_asset
from knowledge.repository import KnowledgeRepository
from knowledge.storage_backend import FileSystemKnowledgeBackend
from knowledge.integrity import compute_content_hash
from tantra.output_bucket import output_bucket
from api.response_builder import CANONICAL_FIELDS


def _repo(tmp_path) -> KnowledgeRepository:
    return KnowledgeRepository(storage=FileSystemKnowledgeBackend(store_dir=str(tmp_path / "kstore")))


def _asset(content=None):
    return new_asset(
        title="Test Asset", jurisdiction="India", domain="criminal",
        source_attribution="unit-test", content=content or {"body": "v1", "n": 1},
        tags=["t1"], author="tester", description="d",
    )


def test_1_register_new_asset(tmp_path):
    repo = _repo(tmp_path)
    content = {"body": "hello", "k": 2}
    stored = repo.register(_asset(content))
    assert uuid.UUID(stored.identity.asset_id)
    assert stored.identity.version_number == 1
    assert stored.integrity.content_hash == compute_content_hash(content)


def test_2_get_asset(tmp_path):
    repo = _repo(tmp_path)
    stored = repo.register(_asset({"body": "abc"}))
    got = repo.get(stored.identity.asset_id)
    assert got is not None
    assert got.metadata.title == "Test Asset"
    assert got.metadata.jurisdiction == "India"
    assert got.content == {"body": "abc"}


def test_3_update_creates_new_version(tmp_path):
    repo = _repo(tmp_path)
    stored = repo.register(_asset({"body": "v1"}))
    v1_id = stored.identity.version_id
    updated = repo.update(stored.identity.asset_id, {"content": {"body": "v2"}}, "editor")
    assert updated.identity.version_number == 2
    old = repo.get_version(stored.identity.asset_id, v1_id)
    assert old is not None and old.content == {"body": "v1"}
    assert len(updated.version_history) == 2


def test_4_list_versions(tmp_path):
    repo = _repo(tmp_path)
    stored = repo.register(_asset({"body": "v1"}))
    aid = stored.identity.asset_id
    repo.update(aid, {"content": {"body": "v2"}}, "editor")
    repo.update(aid, {"content": {"body": "v3"}}, "editor")
    versions = repo.list_versions(aid)
    assert len(versions) == 3
    assert [v.identity.version_number for v in versions] == [1, 2, 3]


def test_5_integrity_verify_pass(tmp_path):
    repo = _repo(tmp_path)
    stored = repo.register(_asset({"body": "intact"}))
    report = repo.verify_integrity(stored.identity.asset_id)
    assert report["verified"] is True
    assert report["status"] == "VERIFIED"


def test_6_integrity_verify_tamper(tmp_path):
    backend = FileSystemKnowledgeBackend(store_dir=str(tmp_path / "kstore"))
    repo = KnowledgeRepository(storage=backend)
    stored = repo.register(_asset({"body": "original"}))
    aid = stored.identity.asset_id
    # Corrupt the stored content on disk without updating the stored hash.
    path = backend._asset_path(aid)
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    entry = json.loads(lines[-1])
    entry["content"] = {"body": "TAMPERED"}
    lines[-1] = json.dumps(entry, sort_keys=True) + "\n"
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    report = repo.verify_integrity(aid)
    assert report["verified"] is False
    assert report["status"] == "TAMPERED"


def test_7_evidence_bridge_produces_evidence_record(tmp_path):
    repo = _repo(tmp_path)
    stored = repo.register(_asset({"body": "evidence"}))
    trace = stored.governance.evidence_id
    assert trace and trace in stored.evidence_linkage
    raw = output_bucket.retrieve(trace)
    assert raw is not None
    full = raw["full_response"]
    for field in CANONICAL_FIELDS:
        assert field in full, f"missing canonical field {field}"
    assert full["recommendation"]["type"] == "INFORM"
    assert full["knowledge_operation"] == "REGISTER"


def test_8_repository_count(tmp_path):
    repo = _repo(tmp_path)
    for i in range(4):
        repo.register(_asset({"body": f"a{i}"}))
    assert repo.count() == 4


def test_9_storage_backend_agnostic(tmp_path):
    backend = FileSystemKnowledgeBackend(store_dir=str(tmp_path / "agnostic"))
    repo = KnowledgeRepository(storage=backend)
    stored = repo.register(_asset({"body": "agnostic"}))
    got = repo.get(stored.identity.asset_id)
    assert got is not None and got.content == {"body": "agnostic"}


def test_10_version_history_preserved_on_update(tmp_path):
    repo = _repo(tmp_path)
    stored = repo.register(_asset({"body": "v1"}))
    aid, v1 = stored.identity.asset_id, stored.identity.version_id
    repo.update(aid, {"content": {"body": "v2"}}, "editor")
    old = repo.get_version(aid, v1)
    assert old is not None and old.content == {"body": "v1"}
    assert old.identity.version_number == 1
