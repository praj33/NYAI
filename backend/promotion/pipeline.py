"""
Promotion pipeline — Phase V.

State machine for governed knowledge-asset promotion. There is NO autonomous
promotion: every transition requires an explicit ``actor`` and ``rationale``,
writes an evidence record (via the repository's evidence bridge) and an
``ApprovalRecord``.
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
from promotion.rollback import RollbackManager
from promotion.states import AssetState, coerce_state, is_valid_transition


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class PromotionPipeline:
    def __init__(
        self,
        repository=None,
        approvals: Optional[ApprovalStore] = None,
        rollback_manager: Optional[RollbackManager] = None,
    ):
        self._repo = repository or knowledge_repository
        self._approvals = approvals or approval_store
        self._rollback = rollback_manager or RollbackManager(
            repository=self._repo, approvals=self._approvals
        )

    def promote(
        self,
        asset_id: str,
        target_state: AssetState,
        actor: str,
        rationale: str,
    ) -> Dict[str, Any]:
        if not actor or not str(actor).strip():
            raise ValueError("actor is required for promotion")
        if not rationale or not str(rationale).strip():
            raise ValueError("rationale is required for promotion")

        # Accept either an AssetState or a raw string; reject unknown states.
        target = target_state if isinstance(target_state, AssetState) else AssetState(str(target_state))

        current = self._repo.get(asset_id)
        if current is None:
            raise KeyError(f"asset_id not found: {asset_id}")

        from_state = coerce_state(current.governance.approval_status)
        if not is_valid_transition(from_state, target):
            raise ValueError(
                f"invalid transition: {from_state.value} -> {target.value}"
            )

        new_version_id = str(uuid.uuid4())
        version_history = list(current.version_history)
        version_history.append(new_version_id)

        governance = KnowledgeGovernance(
            approval_status=target.value,
            approved_by=actor if target == AssetState.APPROVED else current.governance.approved_by,
            approval_timestamp=_utc_now() if target == AssetState.APPROVED else current.governance.approval_timestamp,
            replay_id=current.governance.replay_id,
        )

        promoted = KnowledgeAsset(
            identity=KnowledgeIdentity(
                asset_id=asset_id,
                version_id=new_version_id,
                version_number=current.identity.version_number + 1,
                created_at=current.identity.created_at,
                updated_at=_utc_now(),
            ),
            metadata=KnowledgeMetadata(
                title=current.metadata.title,
                jurisdiction=current.metadata.jurisdiction,
                domain=current.metadata.domain,
                source_attribution=current.metadata.source_attribution,
                tags=list(current.metadata.tags),
                author=current.metadata.author,
                description=current.metadata.description,
            ),
            content=dict(current.content),
            integrity=KnowledgeIntegrity(content_hash=""),
            governance=governance,
            version_history=version_history,
            evidence_linkage=list(current.evidence_linkage),
        )

        stored = self._repo.store_version(promoted, operation="PROMOTE", actor=actor)

        record = self._approvals.record(ApprovalRecord(
            record_id=new_record_id(),
            asset_id=asset_id,
            version_id=new_version_id,
            from_state=from_state.value,
            to_state=target.value,
            actor=actor,
            rationale=rationale,
            evidence_trace_id=stored.governance.evidence_id or "",
            operation="PROMOTE",
        ))

        return {
            "asset_id": asset_id,
            "from_state": from_state.value,
            "to_state": target.value,
            "record_id": record.record_id,
            "evidence_trace_id": stored.governance.evidence_id,
        }

    def rollback(
        self,
        asset_id: str,
        target_version_id: str,
        actor: str,
        reason: str,
    ) -> Dict[str, Any]:
        if not actor or not str(actor).strip():
            raise ValueError("actor is required for rollback")
        if not reason or not str(reason).strip():
            raise ValueError("reason is required for rollback")
        return self._rollback.rollback(asset_id, target_version_id, actor, reason)

    def get_current_state(self, asset_id: str) -> str:
        current = self._repo.get(asset_id)
        if current is None:
            raise KeyError(f"asset_id not found: {asset_id}")
        return coerce_state(current.governance.approval_status).value

    def get_approval_trail(self, asset_id: str) -> Dict[str, Any]:
        return self._approvals.get_trail(asset_id).to_dict()


promotion_pipeline = PromotionPipeline()
