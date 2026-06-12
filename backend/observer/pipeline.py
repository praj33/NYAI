"""
Observer Pipeline — TANTRA Compliance
Validates schema, hashes, and trace continuity.
If observer fails → response is BLOCKED.
Observer NEVER modifies data.
"""
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, List, Optional


class ObserverValidationResult:
    """Result of observer validation. If not valid, response must be blocked."""
    def __init__(self):
        self.validation_status: str = "PENDING"
        self.determinism_verified: bool = False
        self.trace_continuity_check: bool = False
        self.schema_valid: bool = False
        self.violations: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "validation_status": self.validation_status,
            "determinism_verified": self.determinism_verified,
            "trace_continuity_check": self.trace_continuity_check,
            "schema_valid": self.schema_valid,
            "violations": self.violations,
            "validated_at": datetime.utcnow().isoformat(),
        }

    @property
    def passed(self) -> bool:
        return (
            self.validation_status == "PASS"
            and self.determinism_verified
            and self.trace_continuity_check
            and self.schema_valid
            and len(self.violations) == 0
        )


class ObserverPipeline:
    """
    TANTRA Observer — validates every response before it leaves.
    Records pipeline steps AND validates output.
    If validation fails → blocks response.
    """

    CANONICAL_FIELDS = [
        "trace_id", "request_id", "input_hash", "legal_context",
        "facts", "analysis", "recommendation", "explanation_chain",
        "risk_flags", "determinism_proof", "timestamp",
    ]

    CONTRACT_FIELDS = ["schema_version", "answer_disclaimer"]
    SCHEMA_VERSION = "tantra_v3"

    VALID_RECOMMENDATION_TYPES = {"INFORM", "REVIEW", "ESCALATE", "INSUFFICIENT_DATA"}

    def __init__(self, trace_id: str):
        self.trace_id = trace_id
        self._steps: List[Dict[str, Any]] = []
        self._created_at = datetime.utcnow().isoformat()

    def record(self, stage: str, data: Optional[Dict[str, Any]] = None):
        """Record an observer event at a pipeline stage. No modification."""
        self._steps.append({
            "stage": stage,
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": self.trace_id,
            "observed": data or {}
        })

    def get_observer_steps(self) -> List[Dict[str, Any]]:
        """Return the full list of observed pipeline steps."""
        return list(self._steps)

    # ─── VALIDATION METHODS (new for TANTRA) ───

    def validate_response(self, response: dict) -> ObserverValidationResult:
        """
        Full TANTRA validation: schema + hashes + trace continuity.
        Returns ObserverValidationResult. Caller must check .passed.
        """
        result = ObserverValidationResult()

        # 1. Schema validation
        result.schema_valid = self._validate_schema(response, result.violations)

        # 2. Hash validation
        result.determinism_verified = self._validate_hashes(response, result.violations)

        # 3. Trace continuity
        result.trace_continuity_check = self._validate_trace_continuity(
            response, result.violations
        )

        # Final status
        if result.schema_valid and result.determinism_verified and result.trace_continuity_check:
            result.validation_status = "PASS"
        else:
            result.validation_status = "FAIL"

        # Record the validation itself
        self.record("observer_validation", result.to_dict())

        return result

    def _validate_schema(self, response: dict, violations: List[str]) -> bool:
        """Check all canonical fields are present and properly typed."""
        valid = True

        for field in self.CANONICAL_FIELDS:
            if field not in response or response[field] is None:
                violations.append(f"OBSERVER_SCHEMA: missing field '{field}'")
                valid = False

        for field in self.CONTRACT_FIELDS:
            if field not in response or response[field] is None:
                violations.append(f"OBSERVER_SCHEMA: missing contract field '{field}'")
                valid = False
        if response.get("schema_version") and response.get("schema_version") != self.SCHEMA_VERSION:
            violations.append(
                f"OBSERVER_SCHEMA: invalid schema_version='{response.get('schema_version')}'"
            )
            valid = False

        # Validate recommendation type
        rec = response.get("recommendation", {})
        rec_dict = rec if isinstance(rec, dict) else (rec.dict() if hasattr(rec, 'dict') else {})
        rec_type = rec_dict.get("type", "")
        rec_type_str = rec_type.value if hasattr(rec_type, 'value') else str(rec_type)
        if rec_type_str not in self.VALID_RECOMMENDATION_TYPES:
            violations.append(f"OBSERVER_SCHEMA: invalid recommendation.type='{rec_type_str}'")
            valid = False

        # Validate facts are structured objects
        facts = response.get("facts", [])
        if isinstance(facts, list):
            for i, fact in enumerate(facts):
                f = fact if isinstance(fact, dict) else (fact.dict() if hasattr(fact, 'dict') else {})
                if not f.get("fact_id") or not f.get("statement") or not f.get("source"):
                    violations.append(f"OBSERVER_SCHEMA: facts[{i}] missing required keys")
                    valid = False

        return valid

    def _validate_hashes(self, response: dict, violations: List[str]) -> bool:
        """Verify determinism_proof hashes are valid format."""
        valid = True
        proof = response.get("determinism_proof", {})
        proof_dict = proof if isinstance(proof, dict) else (proof.dict() if hasattr(proof, 'dict') else {})

        for hash_field in ["input_hash", "output_hash"]:
            h = str(proof_dict.get(hash_field, ""))
            if len(h) != 64 or not all(c in '0123456789abcdef' for c in h):
                violations.append(f"OBSERVER_HASH: {hash_field} is not 64-char hex")
                valid = False

        # Verify input_hash matches the response-level input_hash
        resp_input_hash = response.get("input_hash", "")
        proof_input_hash = proof_dict.get("input_hash", "")
        if resp_input_hash and proof_input_hash and resp_input_hash != proof_input_hash:
            violations.append("OBSERVER_HASH: input_hash mismatch between response and proof")
            valid = False

        return valid

    def _validate_trace_continuity(self, response: dict, violations: List[str]) -> bool:
        """Ensure trace_id has not mutated through the pipeline."""
        response_trace = response.get("trace_id", "")
        if response_trace != self.trace_id:
            violations.append(
                f"OBSERVER_TRACE: trace_id mutated from '{self.trace_id}' to '{response_trace}'"
            )
            return False
        return True

    # ─── PROVENANCE (kept from original) ───

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
