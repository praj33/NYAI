"""
Metadata extraction from raw documents — Phase V.

Pure extraction: maps a raw document dict to a ``KnowledgeMetadata`` object.
All optional fields degrade gracefully — never raises on missing optional data.
"""
from __future__ import annotations

from typing import Any, Dict

from knowledge.models import KnowledgeMetadata


def extract_metadata(document: Dict[str, Any]) -> KnowledgeMetadata:
    """
    Extract KnowledgeMetadata from a raw document dict.

    Required-by-convention fields (title, jurisdiction, domain,
    source_attribution) fall back to safe defaults here; *validation* of their
    presence is the job of ``ingestion.validator``. This keeps extraction pure
    and non-raising.
    """
    document = document or {}
    tags = document.get("tags") or []
    if not isinstance(tags, list):
        tags = [str(tags)]

    return KnowledgeMetadata(
        title=str(document.get("title", "")).strip(),
        jurisdiction=str(document.get("jurisdiction", "Global")).strip() or "Global",
        domain=str(document.get("domain", "general")).strip() or "general",
        source_attribution=str(document.get("source_attribution", "")).strip(),
        tags=[str(t) for t in tags],
        author=document.get("author"),
        description=document.get("description"),
    )
