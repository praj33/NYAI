import hashlib
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import threading

class HashChainLedger:
    def __init__(self, ledger_file: str = 'provenance_ledger.json'):
        self.ledger_file = ledger_file
        self.lock = threading.Lock()
        self._ensure_ledger_exists()

    def _ensure_ledger_exists(self):
        if not os.path.exists(self.ledger_file):
            genesis_entry = {
                "index": 0,
                "timestamp": datetime.utcnow().isoformat() + 'Z',
                "event_hash": "genesis",
                "prev_hash": "0" * 64,  # 64 zeros for SHA256
                "signed_event": None
            }
            with open(self.ledger_file, 'w') as f:
                json.dump([genesis_entry], f, indent=2)

    def _load_ledger(self) -> List[Dict[str, Any]]:
        with open(self.ledger_file, 'r') as f:
            return json.load(f)

    def _save_ledger(self, ledger: List[Dict[str, Any]]):
        with open(self.ledger_file, 'w') as f:
            json.dump(ledger, f, indent=2)

    def _compute_event_hash(self, signed_event: Dict[str, Any]) -> str:
        """Compute SHA256 hash of the signed event."""
        canonical_json = json.dumps(signed_event, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical_json.encode()).hexdigest()

    def append_event(self, signed_event: Dict[str, Any]) -> int:
        """Append a signed event to the ledger and return its index."""
        with self.lock:
            ledger = self._load_ledger()
            prev_entry = ledger[-1]
            prev_hash = prev_entry['event_hash']

            event_hash = self._compute_event_hash(signed_event)

            new_entry = {
                "index": len(ledger),
                "timestamp": datetime.utcnow().isoformat() + 'Z',
                "event_hash": event_hash,
                "prev_hash": prev_hash,
                "signed_event": signed_event
            }

            ledger.append(new_entry)
            self._save_ledger(ledger)
            return new_entry["index"]

    def get_entry(self, index: int) -> Optional[Dict[str, Any]]:
        """Get a specific entry by index."""
        ledger = self._load_ledger()
        if 0 <= index < len(ledger):
            return ledger[index]
        return None

    def get_all_entries(self) -> List[Dict[str, Any]]:
        """Get all ledger entries."""
        return self._load_ledger()

    def verify_chain_integrity(self) -> bool:
        """Verify the entire chain's integrity."""
        ledger = self._load_ledger()
        for i in range(1, len(ledger)):
            current = ledger[i]
            previous = ledger[i-1]

            # Check prev_hash matches
            if current['prev_hash'] != previous['event_hash']:
                return False

            # Check event_hash is correct
            if current['signed_event']:
                expected_hash = self._compute_event_hash(current['signed_event'])
                if current['event_hash'] != expected_hash:
                    return False

        return True

    def get_chain_length(self) -> int:
        """Get the current length of the chain."""
        return len(self._load_ledger())

# Global instance
ledger = HashChainLedger(os.getenv("PROVENANCE_LEDGER_PATH", "provenance_ledger.json"))