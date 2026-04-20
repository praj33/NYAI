"""
Observer Pipeline — TANTRA Compliance
Explicit, auditable pipeline stage that tracks every processing step.
No logic changes — extracts existing inline provenance into a structured observer.
"""
from datetime import datetime
from typing import Dict, Any, List, Optional


class ObserverPipeline:
    """Tracks and records every stage of the legal query pipeline."""

    def __init__(self, trace_id: str):
        self.trace_id = trace_id
        self._steps: List[Dict[str, Any]] = []
        self._created_at = datetime.utcnow().isoformat()

    def record(self, stage: str, data: Optional[Dict[str, Any]] = None):
        """Record an observer event at a pipeline stage."""
        self._steps.append({
            "stage": stage,
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": self.trace_id,
            "observed": data or {}
        })

    def get_observer_steps(self) -> List[Dict[str, Any]]:
        """Return the full list of observed pipeline steps."""
        return list(self._steps)

    def get_provenance_entry(
        self,
        agent: str,
        sections_found: int,
        case_laws_found: int,
        ontology_filtered: bool,
        domains: List[str],
        jurisdiction_detected: str,
        jurisdiction_confidence: float
    ) -> Dict[str, Any]:
        """Build a structured provenance chain entry from observer data."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "query_processed",
            "agent": agent,
            "sections_found": sections_found,
            "case_laws_found": case_laws_found,
            "ontology_filtered": ontology_filtered,
            "domains": domains,
            "jurisdiction_detected": jurisdiction_detected,
            "jurisdiction_confidence": jurisdiction_confidence,
            "observer_steps_count": len(self._steps)
        }

    def build_decision_basis(
        self,
        enforcement_result
    ) -> Dict[str, Any]:
        """Extract the decision basis from an enforcement result."""
        return {
            "enforcement_decision": enforcement_result.decision.value,
            "rule_id": enforcement_result.rule_id,
            "policy_source": enforcement_result.policy_source.value,
            "reasoning_summary": enforcement_result.reasoning_summary,
            "proof_hash": enforcement_result.proof_hash,
            "trace_id": enforcement_result.trace_id,
            "timestamp": enforcement_result.timestamp.isoformat() if enforcement_result.timestamp else None
        }

    def build_confidence_sources(
        self,
        sections_found: int,
        base_confidence: float,
        jurisdiction_confidence: float,
        domain_confidence: float,
        statute_match: float,
        understanding_source: str,
        statute_source: str
    ) -> Dict[str, Any]:
        """Document where each confidence score came from."""
        return {
            "overall_formula": "(base_confidence + statute_match + domain_confidence) / 3",
            "base_confidence": {
                "value": round(base_confidence, 4),
                "source": "EnhancedLegalAdvisor.confidence_score"
            },
            "jurisdiction_confidence": {
                "value": round(jurisdiction_confidence, 4),
                "source": "JurisdictionDetector.detect()"
            },
            "domain_confidence": {
                "value": round(domain_confidence, 4),
                "source": "keyword_match_in_query"
            },
            "statute_match": {
                "value": round(statute_match, 4),
                "source": f"sections_found={sections_found}, formula=min(0.95, 0.3 + count*0.1)"
            },
            "understanding_source": understanding_source,
            "statute_source": statute_source
        }
