from enum import Enum

class EventType(Enum):
    """
    Enumeration of all event types in the Nyaya AI system.
    These events integrate with the Sovereign provenance ledger.
    """
    QUERY_RECEIVED = "query_received"
    AGENT_CLASSIFIED = "agent_classified"
    JURISDICTION_RESOLVED = "jurisdiction_resolved"
    REASONING_EXPLAINED = "reasoning_explained"
    EVIDENCE_CHAIN_GENERATED = "evidence_chain_generated"
    TRACE_COMPLETED = "trace_completed"