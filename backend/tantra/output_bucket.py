"""
TANTRA Output Bucket — Logs every NYAI output to disk.
Each entry is reproducible, auditable, and retrievable by trace_id.
"""
import json
import hashlib
import os
import threading
from datetime import datetime
from typing import Dict, Any, Optional


class OutputBucket:
    """
    Append-only output log. Every NYAI response is stored here.
    Entries are retrievable by trace_id and re-verifiable by hash.
    """

    def __init__(self, bucket_dir: str = None):
        if bucket_dir is None:
            bucket_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output_logs")
        self.bucket_dir = bucket_dir
        os.makedirs(self.bucket_dir, exist_ok=True)
        self._log_file = os.path.join(self.bucket_dir, "nyai_output_log.jsonl")
        self._index: Dict[str, int] = {}  # trace_id → line offset
        self._lock = threading.Lock()
        self._rebuild_index()

    def _rebuild_index(self):
        """Rebuild in-memory index from existing log file."""
        if not os.path.exists(self._log_file):
            return
        try:
            with open(self._log_file, 'r', encoding='utf-8') as f:
                for offset, line in enumerate(f):
                    try:
                        entry = json.loads(line.strip())
                        tid = entry.get("trace_id")
                        if tid:
                            self._index[tid] = offset
                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass

    def store(self, response: Dict[str, Any]) -> Dict[str, str]:
        """
        Store a NYAI response. Returns storage receipt.
        """
        trace_id = response.get("trace_id", "UNKNOWN")
        proof = response.get("determinism_proof", {})
        if isinstance(proof, dict):
            input_hash = proof.get("input_hash", "")
            output_hash = proof.get("output_hash", "")
        else:
            input_hash = getattr(proof, "input_hash", "")
            output_hash = getattr(proof, "output_hash", "")

        entry = {
            "trace_id": trace_id,
            "input_hash": input_hash,
            "output_hash": output_hash,
            "timestamp": datetime.utcnow().isoformat(),
            "full_response": response,
        }

        # Compute verification hash of the entry
        entry_json = json.dumps(entry, sort_keys=True, default=str)
        entry_hash = hashlib.sha256(entry_json.encode('utf-8')).hexdigest()
        entry["entry_hash"] = entry_hash

        with self._lock:
            with open(self._log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, sort_keys=True, default=str) + "\n")
            self._index[trace_id] = len(self._index)

        return {
            "stored": "true",
            "trace_id": trace_id,
            "entry_hash": entry_hash,
            "bucket_file": self._log_file,
        }

    def retrieve(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a stored response by trace_id."""
        if not os.path.exists(self._log_file):
            return None

        with self._lock:
            with open(self._log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        if entry.get("trace_id") == trace_id:
                            return entry
                    except json.JSONDecodeError:
                        continue
        return None

    def verify(self, trace_id: str) -> Dict[str, Any]:
        """
        Retrieve and re-verify a stored response.
        Recomputes the output_hash and compares.
        """
        entry = self.retrieve(trace_id)
        if not entry:
            return {"verified": False, "reason": "trace_id not found in bucket"}

        stored_output_hash = entry.get("output_hash", "")
        stored_entry_hash = entry.get("entry_hash", "")

        # Re-verify entry hash
        entry_copy = {k: v for k, v in entry.items() if k != "entry_hash"}
        recomputed = hashlib.sha256(
            json.dumps(entry_copy, sort_keys=True, default=str).encode('utf-8')
        ).hexdigest()

        return {
            "verified": recomputed == stored_entry_hash,
            "trace_id": trace_id,
            "stored_entry_hash": stored_entry_hash,
            "recomputed_entry_hash": recomputed,
            "output_hash": stored_output_hash,
            "tamper_detected": recomputed != stored_entry_hash,
        }


# Module-level singleton
output_bucket = OutputBucket()
