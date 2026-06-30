"""Phase V — Knowledge ingestion pipeline unit tests."""
import sys, os, uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("NYAI_API_KEY", "test-key-production-hardening")

import pytest

from knowledge.repository import KnowledgeRepository
from knowledge.storage_backend import FileSystemKnowledgeBackend
from ingestion.pipeline import KnowledgeIngestionPipeline
from ingestion.logger import IngestionLog
from ingestion.extractor import extract_metadata
from tantra.output_bucket import output_bucket


def _pipeline(tmp_path) -> KnowledgeIngestionPipeline:
    repo = KnowledgeRepository(storage=FileSystemKnowledgeBackend(store_dir=str(tmp_path / "kstore")))
    log = IngestionLog(log_dir=str(tmp_path / "ilogs"))
    return KnowledgeIngestionPipeline(repository=repo, log=log)


def _doc(extra=None):
    d = {
        "title": "Doc", "jurisdiction": "India", "domain": "civil",
        "source_attribution": "test-src", "content": {"text": uuid.uuid4().hex},
        "tags": ["a"], "author": "auth", "description": "desc",
    }
    if extra:
        d.update(extra)
    return d


def test_1_ingest_new_document(tmp_path):
    pipe = _pipeline(tmp_path)
    res = pipe.ingest(_doc(), actor="u", jurisdiction="India", domain="civil", source_attribution="s")
    assert res.status == "SUCCESS"
    assert res.operation == "INGEST_NEW"
    assert uuid.UUID(res.asset_id)
    assert res.log_id


def test_2_schema_validation_rejects_missing_field(tmp_path):
    pipe = _pipeline(tmp_path)
    doc = _doc()
    doc.pop("title")
    res = pipe.ingest(doc, actor="u", jurisdiction="India", domain="civil", source_attribution="s")
    assert res.status == "REJECTED"
    assert "title" in (res.rejection_reason or "")


def test_3_duplicate_detection(tmp_path):
    pipe = _pipeline(tmp_path)
    doc = _doc()
    first = pipe.ingest(doc, actor="u", jurisdiction="India", domain="civil", source_attribution="s")
    assert first.status == "SUCCESS"
    second = pipe.ingest(doc, actor="u2", jurisdiction="India", domain="civil", source_attribution="s")
    assert second.status == "DUPLICATE_REJECTED"


def test_4_version_comparison(tmp_path):
    pipe = _pipeline(tmp_path)
    res = pipe.ingest(_doc({"content": {"a": 1}}), actor="u", jurisdiction="India", domain="civil", source_attribution="s")
    diff = pipe.compare_versions(res.asset_id, {"a": 2, "b": 3})
    assert diff["comparable"] is True
    assert len(diff["differences"]) > 0


def test_5_ingestion_log_append(tmp_path):
    pipe = _pipeline(tmp_path)
    res = pipe.ingest(_doc(), actor="u", jurisdiction="India", domain="civil", source_attribution="s")
    entry = pipe._log.get(res.log_id)
    assert entry is not None
    assert entry.asset_id == res.asset_id
    assert entry.status == "SUCCESS"


def test_6_approval_status_is_pending_after_ingest(tmp_path):
    pipe = _pipeline(tmp_path)
    res = pipe.ingest(_doc(), actor="u", jurisdiction="India", domain="civil", source_attribution="s")
    asset = pipe._repo.get(res.asset_id)
    assert asset.governance.approval_status == "PENDING"


def test_7_ingestion_evidence_record(tmp_path):
    pipe = _pipeline(tmp_path)
    res = pipe.ingest(_doc(), actor="u", jurisdiction="India", domain="civil", source_attribution="s")
    raw = output_bucket.retrieve(res.trace_id)
    assert raw is not None
    assert raw["full_response"]["knowledge_operation"] == "INGEST_NEW"


def test_8_metadata_extraction():
    doc = {
        "title": "T", "jurisdiction": "UK", "domain": "family",
        "source_attribution": "src", "tags": ["x", "y"],
        "author": "me", "description": "about", "content": {"a": 1},
    }
    md = extract_metadata(doc)
    assert md.title == "T"
    assert md.jurisdiction == "UK"
    assert md.domain == "family"
    assert md.source_attribution == "src"
    assert md.tags == ["x", "y"]
    assert md.author == "me"
    assert md.description == "about"
