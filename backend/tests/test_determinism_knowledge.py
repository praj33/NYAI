"""Phase V — Determinism / hash-verification tests for knowledge operations."""
import sys, os, uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("NYAI_API_KEY", "test-key-production-hardening")

import pytest

from knowledge.models import new_asset
from knowledge.repository import KnowledgeRepository
from knowledge.storage_backend import FileSystemKnowledgeBackend
from knowledge.integrity import compute_content_hash
from ingestion.pipeline import KnowledgeIngestionPipeline
from ingestion.logger import IngestionLog


def _repo(tmp_path):
    return KnowledgeRepository(storage=FileSystemKnowledgeBackend(store_dir=str(tmp_path / "kstore")))


def _asset(content):
    return new_asset(title="D", jurisdiction="India", domain="civil",
                     source_attribution="s", content=content)


def test_1_content_hash_deterministic():
    content = {"b": 2, "a": 1, "nested": {"y": 2, "x": 1}}
    assert compute_content_hash(content) == compute_content_hash(dict(content))


def test_2_asset_id_stable_across_versions(tmp_path):
    repo = _repo(tmp_path)
    stored = repo.register(_asset({"v": 1}))
    aid = stored.identity.asset_id
    a2 = repo.update(aid, {"content": {"v": 2}}, "e")
    a3 = repo.update(aid, {"content": {"v": 3}}, "e")
    assert a2.identity.asset_id == aid
    assert a3.identity.asset_id == aid


def test_3_evidence_trace_id_unique_per_operation(tmp_path):
    repo = _repo(tmp_path)
    traces = []
    for i in range(5):
        stored = repo.register(_asset({"v": i}))
        traces.append(stored.governance.evidence_id)
    assert len(set(traces)) == 5
    for t in traces:
        assert uuid.UUID(t)


def test_4_version_numbers_sequential(tmp_path):
    repo = _repo(tmp_path)
    stored = repo.register(_asset({"v": 0}))
    aid = stored.identity.asset_id
    for i in range(1, 5):
        repo.update(aid, {"content": {"v": i}}, "e")
    versions = repo.list_versions(aid)
    assert [v.identity.version_number for v in versions] == [1, 2, 3, 4, 5]


def test_5_ingestion_hash_deterministic(tmp_path):
    repo = _repo(tmp_path)
    log = IngestionLog(log_dir=str(tmp_path / "ilogs"))
    pipe = KnowledgeIngestionPipeline(repository=repo, log=log)
    doc = {"title": "T", "jurisdiction": "India", "domain": "civil",
           "source_attribution": "s", "content": {"text": "fixed-content"}}
    r1 = pipe.ingest(dict(doc), actor="alice", jurisdiction="India", domain="civil", source_attribution="s")
    r2 = pipe.ingest(dict(doc), actor="bob", jurisdiction="India", domain="civil", source_attribution="s")
    assert r1.content_hash == r2.content_hash
    assert r2.status == "DUPLICATE_REJECTED"
