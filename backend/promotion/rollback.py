"""
Rollback manager — Phase V promotion.

Restoring a previous version never overwrites history: it appends a NEW version
whose content is copied from the target version, and resets the asset to DRAFT.
Every rollback writes an evidence record and an ApprovalRecord.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from knowledge.models import (
    KnowledgeAsset,
    KnowledgeGovernance,
    KnowledgeIdentity,
    KnowledgeIntegrity,
    KnowledgeMetadata,
)
from knowledge.repository import knowledge_repository
from promotion.approval import ApprovalRecord, ApprovalStore, approval_store, new_record_id
from promotion.states import AssetState, coerce_state


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RollbackManager:
    def __init__(self, repository=None, approvals: Optional[ApprovalStore] = None):
        self._repo = repository or knowledge_repository
        self._approvals = approvals or approval_store

    def rollback(
        self,
        asset_id: str,
        target_version_id: str,
        actor: str,
        reason: str,
    ) -> Dict[str, Any]:
        current = self._repo.get(asset_id)
        if current is None:
            raise KeyError(f"asset_id not found: {asset_id}")

        target = self._repo.get_version(asset_id, target_version_id)
        if target is None:
            raise KeyError(f"target_version_id not found: {target_version_id}")

        from_state = coerce_state(current.governance.approval_status)

        new_version_id = str(uuid.uuid4())
        version_history = list(current.version_history)
        version_history.append(new_version_id)

        restored = KnowledgeAsset(
            identity=KnowledgeIdentity(
                asset_id=asset_id,
                version_id=new_version_id,
                version_number=current.identity.version_number + 1,
                created_at=current.identity.created_at,
                updated_at=_utc_now(),
            ),
            metadata=KnowledgeMetadata(
                title=target.metadata.title,
                jurisdiction=target.metadata.jurisdiction,
                domain=target.metadata.domain,
                source_attribution=target.metadata.source_attribution,
                tags=list(target.metadata.tags),
                author=target.metadata.author,
                description=target.metadata.description,
            ),
            content=dict(target.content),
            integrity=KnowledgeIntegrity(content_hash=""),
            governance=KnowledgeGovernance(approval_status=AssetState.DRAFT.value),
            version_history=version_history,
            evidence_linkage=list(current.evidence_linkage),
        )

        stored = self._repo.store_version(restored, operation="ROLLBACK", actor=actor)

        record = self._approvals.record(ApprovalRecord(
            record_id=new_record_id(),
            asset_id=asset_id,
            version_id=new_version_id,
            from_state=from_state.value,
            to_state=AssetState.DRAFT.value,
            actor=actor,
            rationale=reason,
            evidence_trace_id=stored.governance.evidence_id or "",
            operation="ROLLBACK",
        ))

        return {
            "asset_id": asset_id,
            "restored_version_id": target_version_id,
            "new_version_id": new_version_id,
            "record_id": record.record_id,
            "evidence_trace_id": stored.governance.evidence_id,
        }
