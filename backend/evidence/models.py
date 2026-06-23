from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict

EVIDENCE_SCHEMA_VERSION = "evidence_v1"
EVIDENCE_FORMAT_VERSION = "1.0.0"

@dataclass
class EvidenceIdentity:
    trace_id: str
    request_id: str
    evidence_id: str
    schema_version: str = EVIDENCE_SCHEMA_VERSION
    evidence_version: str = EVIDENCE_FORMAT_VERSION
    origin: str = "nyai-legal-engine"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@dataclass
class EvidenceInput:
    raw_query: str
    cleaned_query: str
    jurisdiction_hint: Optional[str]
    domain_hint: Optional[str]
    input_hash: str

@dataclass
class EvidenceDecision:
    recommendation_type: str
    confidence: float
    rationale: str
    jurisdiction: str
    domain: str
    jurisdiction_confidence: float

@dataclass
class EvidenceReasoning:
    facts: List[Dict[str, Any]]
    applicable_statutes: List[Dict[str, Any]]
    case_laws: List[Dict[str, Any]]
    explanation_chain: List[Dict[str, Any]]
    rule_application: List[Dict[str, Any]]
    observer_steps: List[Dict[str, Any]]
    observer_validation: Dict[str, Any]

@dataclass
class EvidenceHashes:
    input_hash: str
    output_hash: str
    entry_hash: str
    determinism_version: str

@dataclass
class EvidenceStorageMetadata:
    stored_at: str
    storage_file: str
    ledger_index: Optional[int]
    replay_source: str = "output_bucket"

@dataclass
class EvidenceReplayMetadata:
    is_replayable: bool = True
    replay_inputs: Optional[Dict[str, Any]] = None
    last_replayed_at: Optional[str] = None
    replay_count: int = 0

@dataclass
class EvidencePackage:
    identity: EvidenceIdentity
    input: EvidenceInput
    decision: EvidenceDecision
    reasoning: EvidenceReasoning
    hashes: EvidenceHashes
    storage: EvidenceStorageMetadata
    replay: EvidenceReplayMetadata
    integrity_status: str = "UNVERIFIED"
    attachments: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str, sort_keys=True)

    def compute_package_hash(self) -> str:
        canonical = {
            "identity": asdict(self.identity),
            "input": asdict(self.input),
            "decision": asdict(self.decision),
            "hashes": asdict(self.hashes),
        }
        return hashlib.sha256(
            json.dumps(canonical, sort_keys=True, default=str).encode()
        ).hexdigest()

    @classmethod
    def from_stored_entry(cls, entry: Dict[str, Any]) -> "EvidencePackage":
        full = entry.get("full_response") or entry
        proof = full.get("determinism_proof") or {}
        if hasattr(proof, "dict"):
            proof = proof.dict()
        if not isinstance(proof, dict):
            proof = {}

        trace_id = entry.get("trace_id") or full.get("trace_id", "UNKNOWN")
        request_id = full.get("request_id", "UNKNOWN")
        timestamp = entry.get("timestamp") or full.get("timestamp", "")
        evidence_id = hashlib.sha256(
            f"{trace_id}:{request_id}:{timestamp}".encode()
        ).hexdigest()

        rec = full.get("recommendation") or {}
        if hasattr(rec, "dict"):
            rec = rec.dict()
        if not isinstance(rec, dict):
            rec = {}

        analysis = full.get("analysis") or {}
        if hasattr(analysis, "dict"):
            analysis = analysis.dict()
        if not isinstance(analysis, dict):
            analysis = {}

        rec_type = rec.get("type", "UNKNOWN")
        if hasattr(rec_type, "value"):
            rec_type = rec_type.value

        return cls(
            identity=EvidenceIdentity(
                trace_id=trace_id, request_id=request_id,
                evidence_id=evidence_id, created_at=timestamp,
            ),
            input=EvidenceInput(
                raw_query=full.get("reasoning_trace", {}).get("original_query", ""),
                cleaned_query=full.get("reasoning_trace", {}).get("cleaned_query", ""),
                jurisdiction_hint=full.get("jurisdiction_detected"),
                domain_hint=full.get("domain"),
                input_hash=entry.get("input_hash") or full.get("input_hash", ""),
            ),
            decision=EvidenceDecision(
                recommendation_type=str(rec_type),
                confidence=float(rec.get("confidence", 0.0)),
                rationale=str(rec.get("rationale", "")),
                jurisdiction=str(full.get("jurisdiction", "")),
                domain=str(full.get("domain", "")),
                jurisdiction_confidence=float(full.get("jurisdiction_confidence", 0.0)),
            ),
            reasoning=EvidenceReasoning(
                facts=full.get("facts") or [],
                applicable_statutes=full.get("statutes") or [],
                case_laws=full.get("case_laws") or [],
                explanation_chain=full.get("explanation_chain") or [],
                rule_application=analysis.get("rule_application") or [],
                observer_steps=full.get("observer_steps") or [],
                observer_validation=full.get("observer_validation") or {},
            ),
            hashes=EvidenceHashes(
                input_hash=entry.get("input_hash") or full.get("input_hash", ""),
                output_hash=entry.get("output_hash") or proof.get("output_hash", ""),
                entry_hash=entry.get("entry_hash", ""),
                determinism_version=proof.get("version", "unknown"),
            ),
            storage=EvidenceStorageMetadata(
                stored_at=entry.get("timestamp", ""),
                storage_file="output_logs/nyai_output_log.jsonl",
                ledger_index=None,
            ),
            replay=EvidenceReplayMetadata(
                is_replayable=True,
                replay_inputs={"trace_id": trace_id, "input_hash": entry.get("input_hash", "")},
            ),
            integrity_status="UNVERIFIED",
            attachments={
                "timeline": full.get("timeline") or [],
                "glossary": full.get("glossary") or [],
                "legal_route": full.get("legal_route") or [],
                "risk_flags": full.get("risk_flags") or [],
                "procedural_steps": full.get("procedural_steps") or [],
                "remedies": full.get("remedies") or [],
                "answer": full.get("answer"),
                "answer_source": full.get("answer_source"),
                "reasoning_trace": full.get("reasoning_trace") or {},
                "confidence_sources": full.get("confidence_sources") or {},
                "full_response": full,
            }
        )
