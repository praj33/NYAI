"""
Promotion state machine definitions — Phase V.

DRAFT → REVIEW → APPROVED → ARCHIVED, with only the transitions below allowed.
ARCHIVED is terminal; restoring an archived asset is done via rollback (which
creates a new DRAFT version), never via a forward transition.
"""
from __future__ import annotations

from enum import Enum
from typing import Dict, List


class AssetState(str, Enum):
    DRAFT = "DRAFT"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    ARCHIVED = "ARCHIVED"


VALID_TRANSITIONS: Dict[AssetState, List[AssetState]] = {
    AssetState.DRAFT: [AssetState.REVIEW, AssetState.ARCHIVED],
    AssetState.REVIEW: [AssetState.APPROVED, AssetState.DRAFT, AssetState.ARCHIVED],
    AssetState.APPROVED: [AssetState.ARCHIVED],
    AssetState.ARCHIVED: [],   # terminal
}

# Mapping of governance.approval_status values onto AssetState. Newly registered
# assets carry approval_status == "PENDING", which is treated as DRAFT.
APPROVAL_STATUS_TO_STATE: Dict[str, AssetState] = {
    "PENDING": AssetState.DRAFT,
    "DRAFT": AssetState.DRAFT,
    "REVIEW": AssetState.REVIEW,
    "APPROVED": AssetState.APPROVED,
    "ARCHIVED": AssetState.ARCHIVED,
    "REJECTED": AssetState.DRAFT,
}


def coerce_state(value: str) -> AssetState:
    """Map a stored approval_status / state string to an AssetState."""
    if isinstance(value, AssetState):
        return value
    return APPROVAL_STATUS_TO_STATE.get(str(value).upper(), AssetState.DRAFT)


def is_valid_transition(from_state: AssetState, to_state: AssetState) -> bool:
    return to_state in VALID_TRANSITIONS.get(from_state, [])
