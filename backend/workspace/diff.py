"""
Document diffing — Phase V workspace.

Pure, deterministic structured comparison between two document content dicts.
"""
from __future__ import annotations

from typing import Any, Dict


class DocumentDiffer:
    @staticmethod
    def compare(content_a: Dict[str, Any], content_b: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return a structured diff: ``{differences, summary, identical}``.

        ``differences`` is a list of per-field changes (added/removed/modified).
        """
        a = content_a or {}
        b = content_b or {}
        a_keys = set(a.keys())
        b_keys = set(b.keys())

        added = sorted(b_keys - a_keys)
        removed = sorted(a_keys - b_keys)
        modified = sorted(k for k in (a_keys & b_keys) if a.get(k) != b.get(k))

        differences = []
        for k in added:
            differences.append({"field": k, "change": "added", "new": b.get(k)})
        for k in removed:
            differences.append({"field": k, "change": "removed", "old": a.get(k)})
        for k in modified:
            differences.append({"field": k, "change": "modified", "old": a.get(k), "new": b.get(k)})

        return {
            "differences": differences,
            "identical": len(differences) == 0,
            "summary": {
                "added": len(added),
                "removed": len(removed),
                "modified": len(modified),
                "total_changes": len(differences),
            },
        }


document_differ = DocumentDiffer()
