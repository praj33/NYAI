"""
Knowledge domain models — Phase V.

Mirrors the dataclass + asdict pattern used in ``evidence/models.py``.
All models are storage-agnostic plain dataclasses; persistence and evidence
linkage are handled by the repository / storage backend layers.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

KNOWLEDGE_SCHEMA_VERSION = "knowledge_v1"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class KnowledgeIdentity:
    asset_id: str            # UUID, stable across versions
    version_id: str          # UUID, unique per version
    version_number: int      # 1-indexed, increments on each version
    schema_version: str = KNOWLEDGE_SCHEMA_VERSION
    origin: str = "nyai-knowledge-repository"
    created_at: str = field(default_factory=_utc_now)
    updated_at: str = field(default_factory=_utc_now)


@dataclass
class KnowledgeMetadata:
    title: str
    jurisdiction: str                    # e.g. "India", "UK", "UAE", "Global"
    domain: str                          # e.g. "criminal", "civil", "family"
    source_attribution: str              # provenance of the asset
    tags: List[str] = field(default_factory=list)
    author: Optional[str] = None
    description: Optional[str] = None


@dataclass
class KnowledgeIntegrity:
    content_hash: str        # SHA-256 of canonical content
    integrity_status: str = "UNVERIFIED"    # UNVERIFIED | VERIFIED | TAMPERED
    verified_at: Optional[str] = None


@dataclass
class KnowledgeGovernance:
    approval_status: str = "PENDING"    # PENDING | APPROVED | REJECTED | ARCHIVED
    approved_by: Optional[str] = None
    approval_timestamp: Optional[str] = None
    rejection_reason: Optional[str] = None
    replay_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    evidence_id: Optional[str] = None   # links to EvidencePackage (trace_id)


@dataclass
class KnowledgeAsset:
    identity: KnowledgeIdentity
    metadata: KnowledgeMetadata
    content: Dict[str, Any]             # opaque; the governed payload
    integrity: KnowledgeIntegrity
    governance: KnowledgeGovernance
    version_history: List[str] = field(default_factory=list)   # list of version_ids
    evidence_linkage: List[str] = field(default_factory=list)  # list of evidence_ids

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str, sort_keys=True)

    def compute_content_hash(self) -> str:
        """SHA-256 of canonical content. Pure function — deterministic."""
        canonical = json.dumps(self.content, sort_keys=True, default=str)
        return hashlib.sha256(canonical.encode()).hexdigest()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeAsset":
        """Reconstruct a KnowledgeAsset from a stored dict (JSONL line)."""
        return cls(
            identity=KnowledgeIdentity(**data["identity"]),
            metadata=KnowledgeMetadata(**data["metadata"]),
            content=data.get("content", {}),
            integrity=KnowledgeIntegrity(**data["integrity"]),
            governance=KnowledgeGovernance(**data["governance"]),
            version_history=list(data.get("version_history", [])),
            evidence_linkage=list(data.get("evidence_linkage", [])),
        )


def new_asset(
    title: str,
    jurisdiction: str,
    domain: str,
    source_attribution: str,
    content: Dict[str, Any],
    tags: Optional[List[str]] = None,
    author: Optional[str] = None,
    description: Optional[str] = None,
    asset_id: Optional[str] = None,
) -> KnowledgeAsset:
    """Factory that builds a version-1 KnowledgeAsset with computed integrity."""
    aid = asset_id or str(uuid.uuid4())
    vid = str(uuid.uuid4())
    asset = KnowledgeAsset(
        identity=KnowledgeIdentity(asset_id=aid, version_id=vid, version_number=1),
        metadata=KnowledgeMetadata(
            title=title,
            jurisdiction=jurisdiction,
            domain=domain,
            source_attribution=source_attribution,
            tags=list(tags or []),
            author=author,
            description=description,
        ),
        content=dict(content or {}),
        integrity=KnowledgeIntegrity(content_hash=""),
        governance=KnowledgeGovernance(),
        version_history=[],
        evidence_linkage=[],
    )
    asset.integrity.content_hash = asset.compute_content_hash()
    return asset
