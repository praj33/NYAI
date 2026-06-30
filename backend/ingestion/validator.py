"""
Ingestion validation + duplicate detection — Phase V.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from knowledge.integrity import compute_content_hash
from knowledge.repository import KnowledgeRepository, knowledge_repository

# Required fields on every ingested document.
REQUIRED_STRING_FIELDS = ("title", "jurisdiction", "domain", "source_attribution")


def validate_schema(document: Dict[str, Any]) -> List[str]:
    """Return a list of validation errors. An empty list means the doc is valid."""
    errors: List[str] = []
    if not isinstance(document, dict):
        return ["document must be a JSON object"]

    for field_name in REQUIRED_STRING_FIELDS:
        value = document.get(field_name)
        if value is None or not isinstance(value, str) or not value.strip():
            errors.append(f"missing or empty required field: {field_name}")

    content = document.get("content")
    if content is None or not isinstance(content, dict) or len(content) == 0:
        errors.append("missing or empty required field: content (must be a non-empty object)")

    return errors


def detect_duplicate(
    content_hash: str,
    repository: Optional[KnowledgeRepository] = None,
) -> Optional[str]:
    """
    Return the asset_id of an existing asset with an identical content hash,
    or ``None`` if no duplicate exists.
    """
    repo = repository or knowledge_repository
    for asset in repo.list_all(limit=1_000_000, offset=0):
        if asset.integrity.content_hash == content_hash:
            return asset.identity.asset_id
    return None


def content_hash_of(document: Dict[str, Any]) -> str:
    """Compute the content hash used for duplicate detection."""
    return compute_content_hash(document.get("content") or {})
