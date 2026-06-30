"""
Promotion service — Phase V.

Thin orchestration layer over ``PromotionPipeline``. The API layer maps the
pipeline's exceptions (ValueError → 400, KeyError → 404) to HTTP responses.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from promotion.pipeline import promotion_pipeline
from promotion.states import AssetState


class PromotionService:
    def __init__(self, pipeline=None):
        self._pipeline = pipeline or promotion_pipeline

    def promote(self, asset_id: str, target_state: str, actor: str, rationale: str) -> Dict[str, Any]:
        # Convert here so an unknown state surfaces as ValueError (→ HTTP 400).
        target = AssetState(str(target_state))
        return self._pipeline.promote(asset_id, target, actor, rationale)

    def rollback(self, asset_id: str, target_version_id: str, actor: str, reason: str) -> Dict[str, Any]:
        return self._pipeline.rollback(asset_id, target_version_id, actor, reason)

    def get_state(self, asset_id: str) -> Dict[str, Any]:
        current_state = self._pipeline.get_current_state(asset_id)
        repo = self._pipeline._repo
        asset = repo.get(asset_id)
        return {
            "asset_id": asset_id,
            "current_state": current_state,
            "last_updated": asset.identity.updated_at if asset else None,
        }

    def get_approval_trail(self, asset_id: str) -> Dict[str, Any]:
        return self._pipeline.get_approval_trail(asset_id)


promotion_service = PromotionService()
