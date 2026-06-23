"""Replay service — reconstructs evidence from persistent storage."""
from __future__ import annotations

from typing import Any, Dict, List

from evidence.replay_engine import replay_engine


class ReplayService:
    def replay_by_trace(self, trace_id: str) -> Dict[str, Any]:
        return replay_engine.replay_by_trace(trace_id)

    def replay_by_recommendation(self, rec_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        return replay_engine.replay_by_recommendation(rec_type, limit=limit)

    def replay_by_jurisdiction(self, jurisdiction: str, limit: int = 10) -> List[Dict[str, Any]]:
        return replay_engine.replay_by_jurisdiction(jurisdiction, limit=limit)

    def replay_by_statute(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        return replay_engine.replay_by_statute(keyword, limit=limit)

    def compare_evidence(self, trace_id_a: str, trace_id_b: str) -> Dict[str, Any]:
        return replay_engine.compare_evidence(trace_id_a, trace_id_b)


replay_service = ReplayService()
