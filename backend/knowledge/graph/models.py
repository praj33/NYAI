"""
Knowledge graph models — Phase V.

Relationship types are GENERIC. No legal ontology is embedded in code; callers
supply whatever ``relationship_type`` strings their domain requires.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Entity:
    entity_id: str
    entity_type: str         # generic: "concept", "document", "rule", "source", ...
    label: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    asset_id: Optional[str] = None    # optional link to a KnowledgeAsset
    created_at: str = field(default_factory=_utc_now)
    evidence_trace_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Entity":
        return cls(**data)


@dataclass
class Relationship:
    relationship_id: str
    source_entity_id: str
    target_entity_id: str
    relationship_type: str   # generic, e.g. "CITES", "DEPENDS_ON", "SUPERSEDES", ...
    weight: float = 1.0
    attributes: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_utc_now)
    evidence_trace_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Relationship":
        return cls(**data)


def new_entity(
    entity_type: str,
    label: str,
    attributes: Optional[Dict[str, Any]] = None,
    asset_id: Optional[str] = None,
) -> Entity:
    return Entity(
        entity_id=str(uuid.uuid4()),
        entity_type=entity_type,
        label=label,
        attributes=dict(attributes or {}),
        asset_id=asset_id,
    )


def new_relationship(
    source_entity_id: str,
    target_entity_id: str,
    relationship_type: str,
    weight: float = 1.0,
    attributes: Optional[Dict[str, Any]] = None,
) -> Relationship:
    return Relationship(
        relationship_id=str(uuid.uuid4()),
        source_entity_id=source_entity_id,
        target_entity_id=target_entity_id,
        relationship_type=relationship_type,
        weight=weight,
        attributes=dict(attributes or {}),
    )
