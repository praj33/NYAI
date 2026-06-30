"""
Storage backend abstraction for the governed knowledge repository — Phase V.

Follows the Protocol pattern from ``evidence/storage_backend.py`` and the
thread-safe / append-only JSONL pattern from ``tantra/output_bucket.py``.

``FileSystemKnowledgeBackend`` stores one JSONL file per asset_id under
``backend/knowledge_store/``. Each line is a full versioned ``KnowledgeAsset``
snapshot, so history is never overwritten.
"""
from __future__ import annotations

import json
import os
import threading
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from knowledge.models import KnowledgeAsset


@runtime_checkable
class KnowledgeStorageBackend(Protocol):
    """Interface for durable knowledge storage (filesystem, Redis, object store)."""

    def store(self, asset: KnowledgeAsset) -> str: ...                       # returns asset_id

    def retrieve(self, asset_id: str) -> Optional[KnowledgeAsset]: ...

    def retrieve_version(self, asset_id: str, version_id: str) -> Optional[KnowledgeAsset]: ...

    def list_versions(self, asset_id: str) -> List[KnowledgeAsset]: ...

    def list_all(self, limit: int = 50, offset: int = 0) -> List[KnowledgeAsset]: ...

    def count(self) -> int: ...

    def delete(self, asset_id: str) -> bool: ...                            # soft-delete only


def _resolve_store_dir() -> str:
    configured = os.environ.get("KNOWLEDGE_STORE_DIRECTORY", "").strip()
    if configured:
        return configured
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "knowledge_store"
    )


class FileSystemKnowledgeBackend:
    """
    JSONL-per-asset append-only storage.

    Storage: ``backend/knowledge_store/<asset_id>.jsonl``
    Index:   in-memory dict ``{ asset_id -> [version_id, ...] }``.
    Thread-safe via ``threading.Lock()`` — mirrors OutputBucket exactly.
    """

    def __init__(self, store_dir: Optional[str] = None):
        if store_dir is None:
            store_dir = _resolve_store_dir()
        self._store_dir = store_dir
        os.makedirs(self._store_dir, exist_ok=True)
        self._index: Dict[str, List[str]] = {}   # asset_id -> [version_id, ...]
        self._deleted: set = set()
        self._lock = threading.Lock()
        self._rebuild_index()

    # ── internals ──────────────────────────────────────────────

    def _asset_path(self, asset_id: str) -> str:
        safe = asset_id.replace(os.sep, "_").replace("/", "_")
        return os.path.join(self._store_dir, f"{safe}.jsonl")

    def _rebuild_index(self) -> None:
        self._index = {}
        self._deleted = set()
        if not os.path.isdir(self._store_dir):
            return
        for name in os.listdir(self._store_dir):
            if not name.endswith(".jsonl"):
                continue
            path = os.path.join(self._store_dir, name)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            entry = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        identity = entry.get("identity", {})
                        aid = identity.get("asset_id")
                        vid = identity.get("version_id")
                        if aid and vid:
                            self._index.setdefault(aid, []).append(vid)
                        gov = entry.get("governance", {})
                        if gov.get("approval_status") == "DELETED":
                            self._deleted.add(aid)
            except Exception:
                continue

    def _read_lines(self, asset_id: str) -> List[Dict[str, Any]]:
        path = self._asset_path(asset_id)
        if not os.path.exists(path):
            return []
        entries: List[Dict[str, Any]] = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return entries

    # ── public API ─────────────────────────────────────────────

    def store(self, asset: KnowledgeAsset) -> str:
        asset_id = asset.identity.asset_id
        version_id = asset.identity.version_id
        line = json.dumps(asset.to_dict(), sort_keys=True, default=str)
        with self._lock:
            path = self._asset_path(asset_id)
            with open(path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
            self._index.setdefault(asset_id, []).append(version_id)
        return asset_id

    def retrieve(self, asset_id: str) -> Optional[KnowledgeAsset]:
        """Return the latest version of an asset (last appended line)."""
        with self._lock:
            entries = self._read_lines(asset_id)
        if not entries:
            return None
        return KnowledgeAsset.from_dict(entries[-1])

    def retrieve_version(self, asset_id: str, version_id: str) -> Optional[KnowledgeAsset]:
        with self._lock:
            entries = self._read_lines(asset_id)
        for entry in entries:
            if entry.get("identity", {}).get("version_id") == version_id:
                return KnowledgeAsset.from_dict(entry)
        return None

    def list_versions(self, asset_id: str) -> List[KnowledgeAsset]:
        with self._lock:
            entries = self._read_lines(asset_id)
        return [KnowledgeAsset.from_dict(e) for e in entries]

    def list_all(self, limit: int = 50, offset: int = 0) -> List[KnowledgeAsset]:
        with self._lock:
            asset_ids = [a for a in self._index.keys() if a not in self._deleted]
        latest: List[KnowledgeAsset] = []
        for aid in asset_ids:
            asset = self.retrieve(aid)
            if asset is not None:
                latest.append(asset)
        latest.sort(key=lambda a: a.identity.created_at)
        return latest[offset:offset + limit]

    def count(self) -> int:
        with self._lock:
            return len([a for a in self._index.keys() if a not in self._deleted])

    def delete(self, asset_id: str) -> bool:
        """Soft-delete: append a DELETED-marked version. History is preserved."""
        asset = self.retrieve(asset_id)
        if asset is None:
            return False
        asset.governance.approval_status = "DELETED"
        self.store(asset)
        with self._lock:
            self._deleted.add(asset_id)
        return True


class RedisKnowledgeBackend:
    """Future: Redis-backed knowledge store. Phase V stub (see Future_Extensibility.md)."""

    def store(self, asset: KnowledgeAsset) -> str:
        raise NotImplementedError("RedisKnowledgeBackend is a future stub")

    def retrieve(self, asset_id: str) -> Optional[KnowledgeAsset]:
        raise NotImplementedError("RedisKnowledgeBackend is a future stub")

    def retrieve_version(self, asset_id: str, version_id: str) -> Optional[KnowledgeAsset]:
        raise NotImplementedError("RedisKnowledgeBackend is a future stub")

    def list_versions(self, asset_id: str) -> List[KnowledgeAsset]:
        raise NotImplementedError("RedisKnowledgeBackend is a future stub")

    def list_all(self, limit: int = 50, offset: int = 0) -> List[KnowledgeAsset]:
        raise NotImplementedError("RedisKnowledgeBackend is a future stub")

    def count(self) -> int:
        raise NotImplementedError("RedisKnowledgeBackend is a future stub")

    def delete(self, asset_id: str) -> bool:
        raise NotImplementedError("RedisKnowledgeBackend is a future stub")
