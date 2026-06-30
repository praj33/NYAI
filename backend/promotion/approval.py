"""
Approval records + audit trail — Phase V promotion.

Append-only JSONL approval log at ``backend/promotion_logs/approval_log.jsonl``.
Every state transition and rollback produces an ``ApprovalRecord`` linked to an
evidence trace id.
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
class ApprovalRecord:
    record_id: str
    asset_id: str
    version_id: str
    from_state: str
    to_state: str
    actor: str
    rationale: str
    evidence_trace_id: str          # mandatory — every approval links to evidence
    operation: str = "PROMOTE"      # PROMOTE | ROLLBACK
    timestamp: str = field(default_factory=_utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ApprovalRecord":
        return cls(**data)


@dataclass
class ApprovalAuditTrail:
    asset_id: str
    records: List[ApprovalRecord]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "records": [r.to_dict() for r in self.records],
            "count": len(self.records),
        }


def _resolve_log_dir() -> str:
    configured = os.environ.get("PROMOTION_LOG_DIRECTORY", "").strip()
    if configured:
        return configured
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "promotion_logs")


class ApprovalStore:
    """Append-only JSONL approval log."""

    def __init__(self, log_dir: Optional[str] = None):
        if log_dir is None:
            log_dir = _resolve_log_dir()
        self._log_dir = log_dir
        os.makedirs(self._log_dir, exist_ok=True)
        self._file = os.path.join(self._log_dir, "approval_log.jsonl")
        self._lock = threading.Lock()

    def _read_all(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self._file):
            return []
        out: List[Dict[str, Any]] = []
        with open(self._file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return out

    def record(self, approval: ApprovalRecord) -> ApprovalRecord:
        if not approval.record_id:
            approval.record_id = str(uuid.uuid4())
        if not approval.timestamp:
            approval.timestamp = _utc_now()
        with self._lock:
            with open(self._file, "a", encoding="utf-8") as f:
                f.write(json.dumps(approval.to_dict(), sort_keys=True, default=str) + "\n")
        return approval

    def get_trail(self, asset_id: str) -> ApprovalAuditTrail:
        records = [
            ApprovalRecord.from_dict(r)
            for r in self._read_all()
            if r.get("asset_id") == asset_id
        ]
        records.sort(key=lambda r: r.timestamp)
        return ApprovalAuditTrail(asset_id=asset_id, records=records)

    def get_record(self, record_id: str) -> Optional[ApprovalRecord]:
        for r in self._read_all():
            if r.get("record_id") == record_id:
                return ApprovalRecord.from_dict(r)
        return None


def new_record_id() -> str:
    return str(uuid.uuid4())


approval_store = ApprovalStore()
