"""
Raj's Schema Integration — Advisory Layer
Integrates Raj's procedural intelligence with the reasoning layer.
NOTE: Enforcement engine removed — all decisions are advisory only.
"""
from typing import Dict, Any
from .schema_consumer import (
    RajSchemaConsumer,
    FailurePath,
    EvidenceReadiness,
    SystemCompliance,
    get_raj_consumer
)


class RajReasoningIntegrator:
    """Integrator that connects Raj's schemas to the reasoning layer (advisory only)."""

    def __init__(self):
        self.raj_consumer = get_raj_consumer()

    def analyze_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive analysis against Raj's schemas. Advisory only."""
        return {
            'failure_paths_check': self._check_failure_paths(context),
            'evidence_readiness_check': self._check_evidence_readiness(context),
            'compliance_check': self._check_compliance(context)
        }

    def _check_failure_paths(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check against Raj's failure paths."""
        case_context = {
            'country': context.get('country', ''),
            'domain': context.get('domain', ''),
            'procedure_id': context.get('procedure_id', ''),
            'original_confidence': context.get('original_confidence', 0.0),
            'user_request': context.get('user_request', '')
        }
        relevant_paths = self.raj_consumer.find_relevant_failure_paths(case_context)
        return {
            'relevant_paths': [path.path_id for path in relevant_paths],
            'escalation_required': any(path.escalation_required for path in relevant_paths),
            'count': len(relevant_paths)
        }

    def _check_evidence_readiness(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check evidence readiness using Raj's schemas."""
        readiness_result = self.raj_consumer.check_evidence_readiness(
            context.get('domain', ''),
            []
        )
        return readiness_result

    def _check_compliance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance using Raj's schemas."""
        compliance_results = []
        jurisdiction_check = self.raj_consumer.validate_system_compliance(
            "SC_LEGAL_001",
            {
                'source_country': context.get('country', ''),
                'routed_to': context.get('jurisdiction_routed_to', '')
            }
        )
        compliance_results.append(jurisdiction_check)
        return {
            'checks_performed': compliance_results,
            'all_compliant': all(check.get('compliant', True) for check in compliance_results)
        }


_raj_reasoning_integrator_instance = None


def get_raj_reasoning_integrator():
    """Get the global Raj reasoning integrator instance"""
    global _raj_reasoning_integrator_instance
    if _raj_reasoning_integrator_instance is None:
        _raj_reasoning_integrator_instance = RajReasoningIntegrator()
    return _raj_reasoning_integrator_instance