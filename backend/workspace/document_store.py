"""
Document store — Phase V workspace.

Append-only JSONL persistence of workspace documents. Each upload and each
metadata update produces a new versioned ``WorkspaceDocument`` (history is never
overwritten) and an evidence record via the evidence bridge.
"""
from __future__ import annotations

import hashlib
import json
import os
import threading
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from knowledge.evidence_bridge import record_knowledge_operation
from workspace.annotation_store import annotation_store
from workspace.diff import DocumentDiffer


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class WorkspaceDocument:
    doc_id: str
    asset_id: str              # links to KnowledgeAsset
    version_id: str
    filename: str
    content_type: str          # "application/json", "text/plain", etc.
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    uploaded_by: str
    uploaded_at: str = field(default_factory=_utc_now)
    evidence_trace_id: str = ""
    operation: str = "UPLOAD"  # UPLOAD | UPDATE_METADATA

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkspaceDocument":
        return cls(**data)


def _resolve_store_dir() -> str:
    configured = os.environ.get("WORKSPACE_STORE_DIRECTORY", "").strip()
    if configured:
        return configured
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "workspace_store")


def _content_hash(content: Dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(content or {}, sort_keys=True, default=str).encode()).hexdigest()


class DocumentStore:
    def __init__(self, store_dir: Optional[str] = None, annotations=None):
        if store_dir is None:
            store_dir = _resolve_store_dir()
        self._store_dir = store_dir
        os.makedirs(self._store_dir, exist_ok=True)
        self._file = os.path.join(self._store_dir, "documents.jsonl")
        self._annotations = annotations or annotation_store
        self._lock = threading.Lock()

    # ── internals ──────────────────────────────────────────────

    def _read_all(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self._file):
            return []
        out: List[Dict[str, Any]] = []
        with open(self._file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return out

    def _append(self, doc: WorkspaceDocument) -> None:
        with self._lock:
            with open(self._file, "a", encoding="utf-8") as f:
                f.write(json.dumps(doc.to_dict(), sort_keys=True, default=str) + "\n")

    # ── public API ─────────────────────────────────────────────

    def upload(self, doc: WorkspaceDocument) -> WorkspaceDocument:
        if not doc.doc_id:
            doc.doc_id = str(uuid.uuid4())
        if not doc.version_id:
            doc.version_id = str(uuid.uuid4())
        if not doc.uploaded_at:
            doc.uploaded_at = _utc_now()
        doc.operation = "UPLOAD"

        doc.evidence_trace_id = record_knowledge_operation(
            operation="WORKSPACE_UPLOAD",
            asset_id=doc.asset_id,
            version_id=doc.doc_id,
            trace_id=str(uuid.uuid4()),
            actor=doc.uploaded_by,
            metadata={
                "jurisdiction": doc.metadata.get("jurisdiction", "Global"),
                "domain": doc.metadata.get("domain", "workspace"),
                "filename": doc.filename,
            },
            content_hash=_content_hash(doc.content),
        )
        self._append(doc)
        return doc

    def get(self, doc_id: str) -> Optional[WorkspaceDocument]:
        for entry in reversed(self._read_all()):
            if entry.get("doc_id") == doc_id:
                return WorkspaceDocument.from_dict(entry)
        return None

    def update_metadata(self, doc_id: str, metadata: Dict[str, Any], actor: str) -> WorkspaceDocument:
        current = self.get(doc_id)
        if current is None:
            raise KeyError(f"doc_id not found: {doc_id}")

        merged = dict(current.metadata)
        merged.update(metadata or {})

        new_doc = WorkspaceDocument(
            doc_id=str(uuid.uuid4()),
            asset_id=current.asset_id,
            version_id=current.version_id,
            filename=current.filename,
            content_type=current.content_type,
            content=current.content,
            metadata=merged,
            uploaded_by=actor,
            uploaded_at=_utc_now(),
            operation="UPDATE_METADATA",
        )
        new_doc.evidence_trace_id = record_knowledge_operation(
            operation="WORKSPACE_UPDATE",
            asset_id=new_doc.asset_id,
            version_id=new_doc.doc_id,
            trace_id=str(uuid.uuid4()),
            actor=actor,
            metadata={
                "jurisdiction": merged.get("jurisdiction", "Global"),
                "domain": merged.get("domain", "workspace"),
                "prior_doc_id": doc_id,
            },
            content_hash=_content_hash(new_doc.content),
        )
        self._append(new_doc)
        return new_doc

    def get_version_history(self, asset_id: str) -> List[WorkspaceDocument]:
        docs = [
            WorkspaceDocument.from_dict(e)
            for e in self._read_all()
            if e.get("asset_id") == asset_id
        ]
        docs.sort(key=lambda d: d.uploaded_at)
        return docs

    def compare_versions(self, doc_id_a: str, doc_id_b: str) -> Dict[str, Any]:
        doc_a = self.get(doc_id_a)
        doc_b = self.get(doc_id_b)
        if doc_a is None or doc_b is None:
            raise KeyError(
                f"document not found: a={bool(doc_a)} b={bool(doc_b)}"
            )
        result = DocumentDiffer.compare(doc_a.content, doc_b.content)
        result["doc_id_a"] = doc_id_a
        result["doc_id_b"] = doc_id_b
        return result

    def get_audit_history(self, doc_id: str) -> List[Dict[str, Any]]:
        """All audit events for the asset that ``doc_id`` belongs to."""
        doc = self.get(doc_id)
        if doc is None:
            raise KeyError(f"doc_id not found: {doc_id}")
        asset_id = doc.asset_id

        events: List[Dict[str, Any]] = []
        for d in self.get_version_history(asset_id):
            events.append({
                "event_type": d.operation,
                "doc_id": d.doc_id,
                "asset_id": d.asset_id,
                "actor": d.uploaded_by,
                "timestamp": d.uploaded_at,
                "evidence_trace_id": d.evidence_trace_id,
            })
        for ann in self._annotations.get_for_asset(asset_id):
            events.append({
                "event_type": "ANNOTATION",
                "doc_id": ann.doc_id,
                "asset_id": ann.asset_id,
                "annotation_type": ann.annotation_type,
                "actor": ann.author,
                "timestamp": ann.created_at,
                "evidence_trace_id": ann.evidence_trace_id,
            })
        events.sort(key=lambda e: e["timestamp"])
        return events


document_store = DocumentStore()
