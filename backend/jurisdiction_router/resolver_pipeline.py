import uuid
import asyncio
from typing import Dict, Any, List
from sovereign_agents.legal_agent import LegalAgent
from sovereign_agents.constitutional_agent import ConstitutionalAgent
from events.event_types import EventType

class ResolverPipeline:
    """
    Handles agent dispatch and structured result returns.
    Takes jurisdiction result and calls respective agent.
    """
    
    def __init__(self):
        # Agent registry - maps jurisdictions to agent instances
        self.agent_registry = {
            "IN": {
                "legal": LegalAgent(jurisdiction="IN"),
                "constitutional": ConstitutionalAgent(jurisdiction="IN")
            },
            "UK": {
                "legal": LegalAgent(jurisdiction="UK"),
                "constitutional": ConstitutionalAgent(jurisdiction="UK")
            },
            "UAE": {
                "legal": LegalAgent(jurisdiction="UAE"),
                "constitutional": ConstitutionalAgent(jurisdiction="UAE")
            }
        }
        
        # Default agent type
        self.default_agent_type = "legal"
    
    async def resolve_and_dispatch(self, jurisdiction: str, query: str, trace_id: str = None) -> Dict[str, Any]:
        """
        Resolve jurisdiction and dispatch to appropriate agent.
        
        Args:
            jurisdiction: Target jurisdiction
            query: Query to process
            trace_id: Optional trace ID for tracking
            
        Returns:
            Structured response object
        """
        if trace_id is None:
            trace_id = str(uuid.uuid4())
            
        # Select appropriate agent
        agent_type = self._determine_agent_type(query)
        agent = self._get_agent(jurisdiction, agent_type)
        
        if not agent:
            # Fallback to default agent
            agent = self._get_agent(jurisdiction, self.default_agent_type)
            
        if not agent:
            raise ValueError(f"No agent available for jurisdiction {jurisdiction}")
        
        # Prepare query for agent
        agent_query = {
            "text": query,
            "jurisdiction": jurisdiction,
            "trace_id": trace_id
        }
        
        # Process with agent
        agent_result = await agent.process(agent_query)
        
        # Log events
        routing_event = agent.emit_event(EventType.AGENT_CLASSIFIED.value, {
            "classification": agent_type,
            "target_agent": agent.__class__.__name__,
            "jurisdiction": jurisdiction
        })
        
        # Build structured response
        response = {
            "jurisdiction": jurisdiction,
            "selected_agent": agent.__class__.__name__,
            "response": agent_result,
            "confidence": agent_result.get("confidence", 0.5),
            "trace_id": trace_id,
            "routing_path": [agent.__class__.__name__]
        }
        
        return response
    
    def _determine_agent_type(self, query: str) -> str:
        """
        Determine which type of agent should handle the query.
        
        Args:
            query: Query text to analyze
            
        Returns:
            Agent type string
        """
        query_lower = query.lower()
        
        # Simple heuristic for constitutional queries
        constitutional_keywords = [
            "constitution", "fundamental rights", "article", "amendment",
            "supreme court", "judicial review", "basic structure"
        ]
        
        for keyword in constitutional_keywords:
            if keyword in query_lower:
                return "constitutional"
                
        return "legal"
    
    def _get_agent(self, jurisdiction: str, agent_type: str):
        """
        Get agent instance for jurisdiction and type.
        
        Args:
            jurisdiction: Target jurisdiction
            agent_type: Type of agent needed
            
        Returns:
            Agent instance or None
        """
        if jurisdiction in self.agent_registry and agent_type in self.agent_registry[jurisdiction]:
            return self.agent_registry[jurisdiction][agent_type]
        return None
    
    def register_agent(self, jurisdiction: str, agent_type: str, agent_instance):
        """
        Register a new agent in the pipeline.
        
        Args:
            jurisdiction: Jurisdiction code
            agent_type: Type of agent
            agent_instance: Agent instance to register
        """
        if jurisdiction not in self.agent_registry:
            self.agent_registry[jurisdiction] = {}
            
        self.agent_registry[jurisdiction][agent_type] = agent_instance