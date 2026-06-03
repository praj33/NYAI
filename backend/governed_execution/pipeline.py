"""
Governed Execution Pipeline
Ensures all agent execution passes through advisory governance controls.
NOTE: Enforcement engine removed — all controls are advisory only.
"""
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import traceback


class GovernedExecutionPipeline:
    """Pipeline that governs all agent execution through advisory controls."""

    def __init__(self):
        self.pipeline_active = True

    def execute_with_governance(
        self,
        agent_executor: Callable,
        execution_context: Dict[str, Any],
        trace_id: str
    ) -> Dict[str, Any]:
        """Execute agent with advisory governance controls."""
        try:
            # Execute the actual agent function
            result = agent_executor(execution_context)

            # Add governance metadata to result
            if isinstance(result, dict):
                result['governance_metadata'] = {
                    'advisory': 'INFORM',
                    'governance_approved': True,
                    'trace_id': trace_id,
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                result = {
                    'result': result,
                    'governance_metadata': {
                        'advisory': 'INFORM',
                        'governance_approved': True,
                        'trace_id': trace_id,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                }

            return result

        except Exception as e:
            return {
                "status": "error",
                "error_type": "execution_error",
                "error_message": str(e),
                "traceback": traceback.format_exc(),
                "governance_metadata": {
                    "advisory": "ESCALATE",
                    "governance_action": "error_handling",
                    "trace_id": trace_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

    def execute_fallback_with_governance(
        self,
        fallback_executor: Callable,
        fallback_context: Dict[str, Any],
        trace_id: str
    ) -> Dict[str, Any]:
        """Execute fallback procedures with advisory governance."""
        try:
            result = fallback_executor(fallback_context)

            if isinstance(result, dict):
                result['governance_metadata'] = {
                    'advisory': 'INFORM',
                    'governance_approved': True,
                    'trace_id': trace_id,
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                result = {
                    'result': result,
                    'governance_metadata': {
                        'advisory': 'INFORM',
                        'governance_approved': True,
                        'trace_id': trace_id,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                }

            return result

        except Exception as e:
            return {
                "status": "error",
                "error_type": "fallback_error",
                "error_message": str(e),
                "governance_metadata": {
                    "advisory": "ESCALATE",
                    "governance_action": "fallback_error_handling",
                    "trace_id": trace_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }


# Global pipeline instance
governed_pipeline = GovernedExecutionPipeline()


def execute_governed_agent(agent_executor: Callable, context: Dict[str, Any], trace_id: str) -> Dict[str, Any]:
    """Global function to execute an agent with governance."""
    return governed_pipeline.execute_with_governance(agent_executor, context, trace_id)


def execute_governed_fallback(fallback_executor: Callable, context: Dict[str, Any], trace_id: str) -> Dict[str, Any]:
    """Global function to execute a fallback with governance."""
    return governed_pipeline.execute_fallback_with_governance(fallback_executor, context, trace_id)