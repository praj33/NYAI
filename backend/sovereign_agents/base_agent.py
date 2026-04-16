import asyncio
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime

class BaseAgent(ABC):
    """
    Base class for all sovereign agents in the Nyaya AI system.
    Provides core functionality for agent identification, processing, and event emission.
    """
    
    def __init__(self, agent_id: str = None, jurisdiction: str = None, capabilities: List[str] = None):
        self.agent_id = agent_id or str(uuid.uuid4())
        self.jurisdiction = jurisdiction
        self.capabilities = capabilities or []
        
    @abstractmethod
    async def process(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core async execution method that all agents must implement.
        
        Args:
            query: The input query/data to process
            
        Returns:
            Processed result dictionary
        """
        pass
    
    def emit_event(self, event_name: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Standardized logging event push method.
        
        Args:
            event_name: Name of the event from event_types
            details: Additional micro-trace details
            
        Returns:
            Formatted event dictionary
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": self.agent_id,
            "jurisdiction": self.jurisdiction,
            "event_name": event_name,
            "request_hash": hash(str(details)) % (10 ** 8),  # Simple hash for traceability
            "details": details or {}
        }
        return event
    
    def generate_confidence_score(self, result: Dict[str, Any]) -> float:
        """
        Generates a confidence metric for the agent's response.
        
        Args:
            result: The result from the agent's processing
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Default implementation - subclasses can override with domain-specific logic
        return 0.5