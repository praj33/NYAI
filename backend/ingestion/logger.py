"""
Ingestion audit log — Phase V.

Append-only JSONL log at ``backend/ingestion_logs/ingestion_log.jsonl``.
Thread-safe, mirroring the OutputBucket persistence pattern.
"""
from __future__ import annotations

import json
import os
import threading
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class IngestionLogEntry:
    log_id: str
    asset_id: str
    version_id: str
    actor: str
    operation: str           # INGEST_NEW | INGEST_UPDATE | DUPLICATE_REJECTED | SCHEMA_REJECTED
    status: str              # SUCCESS | REJECTED
    content_hash: str
    evidence_trace_id: str
    rejection_reason: Optional[str] = None
    timestamp: str = field(default_factory=_utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IngestionLogEntry":
        return cls(**data)


def _resolve_log_dir() -> str:
    configured = os.environ.get("INGESTION_LOG_DIRECTORY", "").strip()
    if configured:
        return configured
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ingestion_logs")


class IngestionLog:
    """Append-only JSONL ingestion audit log."""

    def __init__(self, log_dir: Optional[str] = None):
        if log_dir is None:
            log_dir = _resolve_log_dir()
        self._log_dir = log_dir
        os.makedirs(self._log_dir, exist_ok=True)
        self._log_file = os.path.join(self._log_dir, "ingestion_log.jsonl")
        self._index: Dict[str, int] = {}   # log_id -> line number
        self._line_count = 0
        self._lock = threading.Lock()
        self._rebuild_index()

    def _rebuild_index(self) -> None:
        self._line_count = 0
        if not os.path.exists(self._log_file):
            return
        with open(self._log_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f):
                self._line_count = line_num + 1
                try:
                    entry = json.loads(line.strip())
                except json.JSONDecodeError:
                    continue
                lid = entry.get("log_id")
                if lid:
                    self._index[lid] = line_num

    def append(self, entry: IngestionLogEntry) -> int:
        """Append an entry. Returns its 0-based line index."""
        line = json.dumps(entry.to_dict(), sort_keys=True, default=str)
        with self._lock:
            line_num = self._line_count
            with open(self._log_file, "a", encoding="utf-8") as f:
                f.write(line + "\n")
            self._index[entry.log_id] = line_num
            self._line_count += 1
        return line_num

    def get(self, log_id: str) -> Optional[IngestionLogEntry]:
        if not os.path.exists(self._log_file):
            return None
        if log_id not in self._index:
            self._rebuild_index()
        if log_id not in self._index:
            return None
        target = self._index[log_id]
        with self._lock:
            with open(self._log_file, "r", encoding="utf-8") as f:
                for idx, line in enumerate(f):
                    if idx == target:
                        try:
                            return IngestionLogEntry.from_dict(json.loads(line.strip()))
                        except (json.JSONDecodeError, TypeError):
                            return None
        return None

    def list_all(self, limit: int = 50, offset: int = 0) -> List[IngestionLogEntry]:
        if not os.path.exists(self._log_file):
            return []
        entries: List[IngestionLogEntry] = []
        with self._lock:
            with open(self._log_file, "r", encoding="utf-8") as f:
                for idx, line in enumerate(f):
                    if idx < offset:
                        continue
                    if len(entries) >= limit:
                        break
                    try:
                        entries.append(IngestionLogEntry.from_dict(json.loads(line.strip())))
                    except (json.JSONDecodeError, TypeError):
                        continue
        return entries

    def count(self) -> int:
        with self._lock:
            return self._line_count


def new_log_id() -> str:
    return str(uuid.uuid4())


ingestion_log = IngestionLog()
