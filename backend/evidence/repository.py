from __future__ import annotations
import json, logging
from typing import Any, Dict, List, Optional
from evidence.models import EvidencePackage
from evidence.storage_backend import EvidenceStorageBackend, FileSystemBackend

logger = logging.getLogger("nyai.evidence.repository")

class EvidenceRepository:
    def __init__(self, storage: Optional[EvidenceStorageBackend] = None):
        self._storage = storage or FileSystemBackend()

    def get_by_trace_id(self, trace_id: str) -> Optional[EvidencePackage]:
        if hasattr(self._storage, "retrieve_as_evidence"):
            return self._storage.retrieve_as_evidence(trace_id)
        entry = self._storage.retrieve(trace_id)
        if not entry:
            return None
        try:
            return EvidencePackage.from_stored_entry(entry)
        except Exception:
            return None

    def get_raw_by_trace_id(self, trace_id: str) -> Optional[Dict[str, Any]]:
        entry = self._storage.retrieve(trace_id)
        if not entry:
            return None
        return entry.get("full_response") or entry

    def list_evidence(self, limit: int = 50, offset: int = 0) -> List[EvidencePackage]:
        entries = self._storage.list_all(limit=limit, offset=offset)
        result = []
        for entry in entries:
            try:
                result.append(EvidencePackage.from_stored_entry(entry))
            except Exception as e:
                logger.warning("Failed to parse entry: %s", e)
        return result

    def _entry_timestamp(self, entry: Dict[str, Any]) -> str:
        return entry.get("timestamp") or (entry.get("full_response") or {}).get("timestamp", "")

    def search_by_date_range(
        self, date_from: str, date_to: str, limit: int = 50, offset: int = 0
    ) -> List[EvidencePackage]:
        all_entries = self._storage.list_all()
        results, skipped = [], 0
        for entry in all_entries:
            ts = self._entry_timestamp(entry)
            if not ts or ts < date_from or ts > date_to:
                continue
            if skipped < offset:
                skipped += 1
                continue
            try:
                results.append(EvidencePackage.from_stored_entry(entry))
            except Exception:
                pass
            if len(results) >= limit:
                break
        return results

    def search_by_evidence_version(
        self, version: str, limit: int = 50, offset: int = 0
    ) -> List[EvidencePackage]:
        all_entries = self._storage.list_all()
        results, skipped = [], 0
        for entry in all_entries:
            try:
                pkg = EvidencePackage.from_stored_entry(entry)
            except Exception:
                continue
            if pkg.identity.evidence_version != version:
                continue
            if skipped < offset:
                skipped += 1
                continue
            results.append(pkg)
            if len(results) >= limit:
                break
        return results

    def search_by_recommendation(self, rec_type: str, limit: int = 50, offset: int = 0) -> List[EvidencePackage]:
        all_entries = self._storage.list_all()
        results, skipped = [], 0
        for entry in all_entries:
            full = entry.get("full_response") or {}
            rec = full.get("recommendation") or {}
            if hasattr(rec, "dict"):
                rec = rec.dict()
            rt = rec.get("type", "") if isinstance(rec, dict) else ""
            if hasattr(rt, "value"):
                rt = rt.value
            if str(rt) == rec_type:
                if skipped < offset:
                    skipped += 1
                    continue
                try:
                    results.append(EvidencePackage.from_stored_entry(entry))
                except Exception:
                    pass
                if len(results) >= limit:
                    break
        return results

    def search_by_jurisdiction(self, jurisdiction: str, limit: int = 50, offset: int = 0) -> List[EvidencePackage]:
        all_entries = self._storage.list_all()
        results, skipped = [], 0
        for entry in all_entries:
            full = entry.get("full_response") or {}
            j = (full.get("jurisdiction_detected") or full.get("jurisdiction") or "").lower()
            if jurisdiction.lower() in j:
                if skipped < offset:
                    skipped += 1
                    continue
                try:
                    results.append(EvidencePackage.from_stored_entry(entry))
                except Exception:
                    pass
                if len(results) >= limit:
                    break
        return results

    def search_by_input_hash(self, input_hash: str) -> Optional[EvidencePackage]:
        for entry in self._storage.list_all():
            if entry.get("input_hash") == input_hash:
                try:
                    return EvidencePackage.from_stored_entry(entry)
                except Exception:
                    pass
        return None

    def search_by_statute(self, keyword: str, limit: int = 50) -> List[EvidencePackage]:
        results, kw = [], keyword.lower()
        for entry in self._storage.list_all():
            full = entry.get("full_response") or {}
            for s in full.get("statutes") or []:
                if kw in json.dumps(s, default=str).lower():
                    try:
                        results.append(EvidencePackage.from_stored_entry(entry))
                    except Exception:
                        pass
                    break
            if len(results) >= limit:
                break
        return results

    def get_ledger_entry_for_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        try:
            from provenance_chain.hash_chain_ledger import HashChainLedger
            for entry in HashChainLedger().get_all_entries():
                signed = entry.get("signed_event") or {}
                if signed.get("trace_id") == trace_id:
                    return entry
        except Exception:
            pass
        return None

    def count(self) -> int:
        return self._storage.count()


evidence_repository = EvidenceRepository()
