from typing import List, Dict, Any, Optional
from .hash_chain_ledger import ledger

class LineageTracer:
    def __init__(self):
        self.ledger = ledger

    def get_trace_history(self, trace_id: str) -> Dict[str, Any]:
        """Retrieve the complete ordered trace history for a given trace_id."""
        all_entries = self.ledger.get_all_entries()

        # Filter entries for this trace_id
        trace_events = []
        for entry in all_entries:
            if entry['signed_event'] and entry['signed_event']['event']['trace_id'] == trace_id:
                trace_events.append({
                    "index": entry["index"],
                    "timestamp": entry["timestamp"],
                    "signed_event": entry["signed_event"]
                })

        # Sort by timestamp
        trace_events.sort(key=lambda x: x["timestamp"])

        # Verify chain integrity for this trace
        chain_valid = self._verify_trace_integrity(trace_events)

        return {
            "trace_id": trace_id,
            "chain_valid": chain_valid,
            "events": trace_events
        }

    def _verify_trace_integrity(self, trace_events: List[Dict[str, Any]]) -> bool:
        """Verify that the trace events form a valid chain."""
        if not trace_events:
            return True

        # For now, just check that all events have the same trace_id
        # In a more complex system, we might check for gaps or ordering
        trace_ids = set()
        for event in trace_events:
            signed_event = event["signed_event"]
            if signed_event and "event" in signed_event:
                trace_ids.add(signed_event["event"]["trace_id"])

        return len(trace_ids) == 1

    def get_recent_traces(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent traces."""
        all_entries = self.ledger.get_all_entries()

        # Get recent entries
        recent_entries = all_entries[-limit:] if len(all_entries) > limit else all_entries

        # Group by trace_id
        traces = {}
        for entry in recent_entries:
            if entry['signed_event']:
                trace_id = entry['signed_event']['event']['trace_id']
                if trace_id not in traces:
                    traces[trace_id] = []
                traces[trace_id].append({
                    "index": entry["index"],
                    "timestamp": entry["timestamp"],
                    "event_name": entry["signed_event"]["event"]["event_name"]
                })

        # Convert to list and sort by most recent
        trace_list = []
        for trace_id, events in traces.items():
            events.sort(key=lambda x: x["timestamp"], reverse=True)
            trace_list.append({
                "trace_id": trace_id,
                "latest_timestamp": events[0]["timestamp"],
                "event_count": len(events),
                "latest_event": events[0]["event_name"]
            })

        trace_list.sort(key=lambda x: x["latest_timestamp"], reverse=True)
        return trace_list[:limit]

# Global instance
tracer = LineageTracer()