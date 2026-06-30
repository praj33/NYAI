"""
SHA-256 integrity verification for knowledge assets — Phase V.

These are pure functions (no I/O, no timestamps in the hash inputs) and are
therefore *deterministic* and *hash-verified* in the strict sense defined in
Implementation.md Section 12.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List

from knowledge.models import KnowledgeAsset


def compute_content_hash(content: Dict[str, Any]) -> str:
    """SHA-256 of ``json.dumps(content, sort_keys=True)``. Deterministic."""
    canonical = json.dumps(content, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()


def verify_asset_integrity(asset: KnowledgeAsset) -> Dict[str, Any]:
    """
    Recompute the content hash and compare against the stored value.

    Returns ``{verified, expected_hash, stored_hash, status}``.
    """
    expected_hash = compute_content_hash(asset.content)
    stored_hash = asset.integrity.content_hash
    verified = expected_hash == stored_hash
    status = "VERIFIED" if verified else "TAMPERED"
    return {
        "verified": verified,
        "expected_hash": expected_hash,
        "stored_hash": stored_hash,
        "status": status,
        "asset_id": asset.identity.asset_id,
        "version_id": asset.identity.version_id,
        "verified_at": datetime.now(timezone.utc).isoformat(),
    }


def compute_version_chain_hash(version_ids: List[str], content_hashes: List[str]) -> str:
    """
    Chain hash across all versions of an asset. Deterministic over its inputs.

    Each link folds the previous chain value with ``version_id:content_hash``.
    """
    chain = ""
    for vid, chash in zip(version_ids, content_hashes):
        link = f"{chain}|{vid}:{chash}"
        chain = hashlib.sha256(link.encode()).hexdigest()
    return chain
