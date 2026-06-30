"""
Annotation store — Phase V workspace.

Append-only JSONL persistence of review annotations. Every ``add`` writes an
evidence record via the evidence bridge so annotations are auditable through
the existing ``/evidence/*`` API.
"""
from __future__ import annotations

import json
import os
import threading
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from knowledge.evidence_bridge import record_knowledge_operation

ANNOTATION_TYPES = {"COMMENT", "REVIEW_NOTE", "FLAG", "APPROVAL_NOTE"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Annotation:
    annotation_id: str
    doc_id: str
    asset_id: str
    annotation_type: str       # COMMENT | REVIEW_NOTE | FLAG | APPROVAL_NOTE
    content: str
    author: str
    created_at: str = field(default_factory=_utc_now)
    evidence_trace_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Annotation":
        return cls(**data)


def _resolve_store_dir() -> str:
    configured = os.environ.get("WORKSPACE_STORE_DIRECTORY", "").strip()
    if configured:
        return configured
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "workspace_store")


class AnnotationStore:
    def __init__(self, store_dir: Optional[str] = None):
        if store_dir is None:
            store_dir = _resolve_store_dir()
        self._store_dir = store_dir
        os.makedirs(self._store_dir, exist_ok=True)
        self._file = os.path.join(self._store_dir, "annotations.jsonl")
        self._lock = threading.Lock()

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

    def add(self, annotation: Annotation) -> Annotation:
        if annotation.annotation_type not in ANNOTATION_TYPES:
            raise ValueError(
                f"invalid annotation_type: {annotation.annotation_type}; "
                f"expected one of {sorted(ANNOTATION_TYPES)}"
            )
        if not annotation.annotation_id:
            annotation.annotation_id = str(uuid.uuid4())
        if not annotation.created_at:
            annotation.created_at = _utc_now()

        evidence_trace_id = record_knowledge_operation(
            operation="ANNOTATION",
            asset_id=annotation.asset_id,
            version_id=annotation.doc_id,
            trace_id=str(uuid.uuid4()),
            actor=annotation.author,
            metadata={
                "jurisdiction": "Global",
                "domain": "workspace",
                "annotation_type": annotation.annotation_type,
                "doc_id": annotation.doc_id,
            },
            content_hash=record_content_hash(annotation),
        )
        annotation.evidence_trace_id = evidence_trace_id

        with self._lock:
            with open(self._file, "a", encoding="utf-8") as f:
                f.write(json.dumps(annotation.to_dict(), sort_keys=True, default=str) + "\n")
        return annotation

    def get_for_document(self, doc_id: str) -> List[Annotation]:
        return [Annotation.from_dict(a) for a in self._read_all() if a.get("doc_id") == doc_id]

    def get_for_asset(self, asset_id: str) -> List[Annotation]:
        return [Annotation.from_dict(a) for a in self._read_all() if a.get("asset_id") == asset_id]


def record_content_hash(annotation: Annotation) -> str:
    import hashlib
    canonical = json.dumps(
        {"type": annotation.annotation_type, "content": annotation.content},
        sort_keys=True, default=str,
    )
    return hashlib.sha256(canonical.encode()).hexdigest()


annotation_store = AnnotationStore()
