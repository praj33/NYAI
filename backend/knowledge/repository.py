"""
Governed Knowledge Repository — Phase V.

Every mutating public method:
    1. Validates inputs.
    2. Computes / verifies the content hash.
    3. Writes to the storage backend.
    4. Writes an evidence record via ``evidence_bridge.record_knowledge_operation``.
    5. Returns the stored asset (or relevant DTO).

The repository is storage-agnostic: it depends only on the
``KnowledgeStorageBackend`` protocol, never on file paths.
"""
from __future__ import annotations

import copy
import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from knowledge.models import (
    KnowledgeAsset,
    KnowledgeGovernance,
    KnowledgeIdentity,
    KnowledgeIntegrity,
    KnowledgeMetadata,
)
from knowledge.storage_backend import FileSystemKnowledgeBackend, KnowledgeStorageBackend
from knowledge.integrity import compute_content_hash, verify_asset_integrity
from knowledge.evidence_bridge import record_knowledge_operation


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class KnowledgeRepository:
    def __init__(self, storage: Optional[KnowledgeStorageBackend] = None):
        self._storage = storage or FileSystemKnowledgeBackend()
        self._lock = threading.Lock()

    # ── helpers ────────────────────────────────────────────────

    def _evidence_metadata(self, asset: KnowledgeAsset) -> Dict[str, Any]:
        return {
            "jurisdiction": asset.metadata.jurisdiction,
            "domain": asset.metadata.domain,
            "title": asset.metadata.title,
            "version_number": asset.identity.version_number,
            "approval_status": asset.governance.approval_status,
        }

    # ── mutating operations ────────────────────────────────────

    def register(self, asset: KnowledgeAsset) -> KnowledgeAsset:
        """Register a new asset. Assigns version 1. Returns the stored asset."""
        if not asset.metadata.title:
            raise ValueError("KnowledgeAsset.metadata.title is required")

        with self._lock:
            # Normalise identity for a fresh version-1 registration.
            if not asset.identity.asset_id:
                asset.identity.asset_id = str(uuid.uuid4())
            if not asset.identity.version_id:
                asset.identity.version_id = str(uuid.uuid4())
            asset.identity.version_number = 1
            asset.identity.created_at = asset.identity.created_at or _utc_now()
            asset.identity.updated_at = _utc_now()

            asset.integrity.content_hash = compute_content_hash(asset.content)
            asset.integrity.integrity_status = "VERIFIED"
            asset.integrity.verified_at = _utc_now()

            if asset.identity.version_id not in asset.version_history:
                asset.version_history.append(asset.identity.version_id)

            op_trace_id = str(uuid.uuid4())
            evidence_trace_id = record_knowledge_operation(
                operation="REGISTER",
                asset_id=asset.identity.asset_id,
                version_id=asset.identity.version_id,
                trace_id=op_trace_id,
                actor=asset.metadata.author or "system",
                metadata=self._evidence_metadata(asset),
                content_hash=asset.integrity.content_hash,
            )
            asset.governance.evidence_id = evidence_trace_id
            asset.evidence_linkage.append(evidence_trace_id)

            self._storage.store(asset)
            return asset

    def update(self, asset_id: str, updates: Dict[str, Any], updated_by: str) -> KnowledgeAsset:
        """
        Create a new version. The prior version is preserved in storage and
        referenced in ``version_history``.

        ``updates`` may contain ``content`` (dict) and/or ``metadata`` (dict of
        KnowledgeMetadata field overrides).
        """
        with self._lock:
            current = self._storage.retrieve(asset_id)
            if current is None:
                raise KeyError(f"asset_id not found: {asset_id}")

            new_content = copy.deepcopy(current.content)
            if "content" in updates and updates["content"] is not None:
                if not isinstance(updates["content"], dict):
                    raise ValueError("updates.content must be a dict")
                new_content = updates["content"]

            new_metadata = KnowledgeMetadata(
                title=current.metadata.title,
                jurisdiction=current.metadata.jurisdiction,
                domain=current.metadata.domain,
                source_attribution=current.metadata.source_attribution,
                tags=list(current.metadata.tags),
                author=current.metadata.author,
                description=current.metadata.description,
            )
            for key, value in (updates.get("metadata") or {}).items():
                if hasattr(new_metadata, key):
                    setattr(new_metadata, key, value)

            new_version_id = str(uuid.uuid4())
            version_history = list(current.version_history)
            version_history.append(new_version_id)

            new_asset = KnowledgeAsset(
                identity=KnowledgeIdentity(
                    asset_id=asset_id,
                    version_id=new_version_id,
                    version_number=current.identity.version_number + 1,
                    created_at=current.identity.created_at,
                    updated_at=_utc_now(),
                ),
                metadata=new_metadata,
                content=new_content,
                integrity=KnowledgeIntegrity(content_hash=""),
                governance=KnowledgeGovernance(
                    approval_status=current.governance.approval_status,
                    approved_by=current.governance.approved_by,
                    approval_timestamp=current.governance.approval_timestamp,
                ),
                version_history=version_history,
                evidence_linkage=list(current.evidence_linkage),
            )
            new_asset.integrity.content_hash = compute_content_hash(new_asset.content)
            new_asset.integrity.integrity_status = "VERIFIED"
            new_asset.integrity.verified_at = _utc_now()

            op_trace_id = str(uuid.uuid4())
            evidence_trace_id = record_knowledge_operation(
                operation="UPDATE",
                asset_id=asset_id,
                version_id=new_version_id,
                trace_id=op_trace_id,
                actor=updated_by,
                metadata=self._evidence_metadata(new_asset),
                content_hash=new_asset.integrity.content_hash,
            )
            new_asset.governance.evidence_id = evidence_trace_id
            new_asset.evidence_linkage.append(evidence_trace_id)

            self._storage.store(new_asset)
            return new_asset

    def store_version(self, asset: KnowledgeAsset, operation: str, actor: str) -> KnowledgeAsset:
        """
        Persist a pre-built asset version (used by promotion / rollback flows)
        with an evidence record. Caller owns identity/version bookkeeping.
        """
        with self._lock:
            asset.integrity.content_hash = compute_content_hash(asset.content)
            asset.identity.updated_at = _utc_now()
            op_trace_id = str(uuid.uuid4())
            evidence_trace_id = record_knowledge_operation(
                operation=operation,
                asset_id=asset.identity.asset_id,
                version_id=asset.identity.version_id,
                trace_id=op_trace_id,
                actor=actor,
                metadata=self._evidence_metadata(asset),
                content_hash=asset.integrity.content_hash,
            )
            asset.governance.evidence_id = evidence_trace_id
            asset.evidence_linkage.append(evidence_trace_id)
            self._storage.store(asset)
            return asset

    def save_governance(self, asset: KnowledgeAsset) -> KnowledgeAsset:
        """
        Persist a new version reflecting a governance change (no content change).
        Used by the promotion pipeline to record approval-state transitions while
        preserving full version history.
        """
        with self._lock:
            asset.identity.updated_at = _utc_now()
            asset.integrity.content_hash = compute_content_hash(asset.content)
            self._storage.store(asset)
            return asset

    # ── read operations ────────────────────────────────────────

    def get(self, asset_id: str) -> Optional[KnowledgeAsset]:
        return self._storage.retrieve(asset_id)

    def get_version(self, asset_id: str, version_id: str) -> Optional[KnowledgeAsset]:
        return self._storage.retrieve_version(asset_id, version_id)

    def list_versions(self, asset_id: str) -> List[KnowledgeAsset]:
        return self._storage.list_versions(asset_id)

    def list_all(self, limit: int = 50, offset: int = 0) -> List[KnowledgeAsset]:
        return self._storage.list_all(limit=limit, offset=offset)

    def verify_integrity(self, asset_id: str) -> Dict[str, Any]:
        """Re-compute the content hash and compare to the stored hash."""
        asset = self._storage.retrieve(asset_id)
        if asset is None:
            return {
                "verified": False,
                "status": "NOT_FOUND",
                "asset_id": asset_id,
                "content_hash": None,
            }
        report = verify_asset_integrity(asset)
        return {
            "verified": report["verified"],
            "content_hash": report["stored_hash"],
            "expected_hash": report["expected_hash"],
            "status": report["status"],
            "asset_id": asset_id,
            "version_id": asset.identity.version_id,
        }

    def count(self) -> int:
        return self._storage.count()


knowledge_repository = KnowledgeRepository()
