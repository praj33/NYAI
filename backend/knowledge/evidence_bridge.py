"""
Evidence bridge — links every knowledge operation to the Phase IV evidence
infrastructure.

Every create / update / promote / rollback / ingest / graph operation routes
through ``record_knowledge_operation()`` which:

1. Builds a full TANTRA-canonical evidence record (all 11 canonical fields +
   4 structural fields + contract fields).
2. Validates it through the *frozen* ``ResponseBuilder`` gate (FAIL CLOSED).
3. Persists it via ``output_bucket.store()`` so the operation surfaces in the
   existing ``/evidence/*`` API and is replayable / verifiable.

This is "stored record replay" — it reconstructs the evidence record from
storage; it does NOT re-execute the originating operation.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from tantra.output_bucket import output_bucket
from api.response_builder import ResponseBuilder, ANSWER_DISCLAIMER, DETERMINISM_VERSION

# Generic operations recorded by the knowledge layer.
KNOWLEDGE_OPERATIONS = {
    "REGISTER", "UPDATE", "PROMOTE", "ROLLBACK", "INGEST", "GRAPH_OP",
    "WORKSPACE_UPLOAD", "WORKSPACE_UPDATE", "ANNOTATION",
}

_response_builder = ResponseBuilder()


def _sha256(obj: Any) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, default=str).encode()
    ).hexdigest()


def record_knowledge_operation(
    operation: str,
    asset_id: str,
    version_id: str,
    trace_id: str,
    actor: str,
    metadata: Dict[str, Any],
    content_hash: str,
) -> str:
    """
    Write an evidence record for a knowledge operation to OutputBucket.

    ``trace_id`` is the originating operation trace; the evidence record itself
    is assigned a fresh, unique ``trace_id`` so it is independently
    retrievable / verifiable. Returns the evidence record's ``trace_id``.

    The record is validated by the frozen ResponseBuilder before storage, so it
    is guaranteed to satisfy TANTRA strict schema validation.
    """
    metadata = metadata or {}
    jurisdiction = str(metadata.get("jurisdiction") or "Global")
    domain = str(metadata.get("domain") or "general")

    evidence_trace_id = str(uuid.uuid4())
    request_id = str(uuid.uuid4())

    input_payload = {
        "asset_id": asset_id,
        "version_id": version_id,
        "operation": operation,
        "actor": actor,
        "origin_trace_id": trace_id,
    }
    input_hash = _sha256(input_payload)
    output_payload = {
        "operation": operation,
        "asset_id": asset_id,
        "version_id": version_id,
        "content_hash": content_hash,
        "metadata": metadata,
    }
    output_hash = _sha256(output_payload)

    timestamp = datetime.now(timezone.utc).isoformat()

    evidence_record: Dict[str, Any] = {
        # ── Determinism & tracing ──
        "trace_id": evidence_trace_id,
        "request_id": request_id,
        "input_hash": input_hash,
        "timestamp": timestamp,
        "schema_version": "tantra_v3",
        "answer_disclaimer": ANSWER_DISCLAIMER,
        # ── Legal context + structural fields ──
        "legal_context": {
            "jurisdiction": jurisdiction,
            "domain": domain,
            "applicable_laws": [],
        },
        "domain": domain,
        "jurisdiction": jurisdiction,
        "confidence": {
            "overall": 1.0,
            "jurisdiction": 1.0,
            "domain": 1.0,
            "statute_match": 0.0,
            "procedural_match": 0.0,
        },
        # ── Facts (structured, non-empty) ──
        "facts": [
            {
                "fact_id": "f1",
                "statement": f"Knowledge operation: {operation} on asset {asset_id}",
                "source": "knowledge_repository",
            }
        ],
        # ── Analysis ──
        "analysis": {
            "issues_identified": [],
            "rule_application": [],
            "conflicts": [],
        },
        # ── Recommendation (advisory only) ──
        "recommendation": {
            "type": "INFORM",
            "confidence": 1.0,
            "rationale": f"Knowledge operation {operation} completed",
        },
        # ── Explanation chain (structured, non-empty) ──
        "explanation_chain": [
            {
                "step_number": 1,
                "description": f"Performed {operation} on asset {asset_id} (version {version_id})",
                "source": "knowledge_repository",
            }
        ],
        # ── Risk + route ──
        "risk_flags": [],
        "legal_route": [],
        # ── Determinism proof ──
        "determinism_proof": {
            "input_hash": input_hash,
            "output_hash": output_hash,
            "version": DETERMINISM_VERSION,
        },
        # ── Knowledge-specific fields ──
        "knowledge_operation": operation,
        "asset_id": asset_id,
        "version_id": version_id,
        "content_hash": content_hash,
        "actor": actor,
        "origin_trace_id": trace_id,
        "knowledge_metadata": metadata,
    }

    # FAIL CLOSED: validate against the frozen TANTRA gate before persisting.
    validated = _response_builder.build(evidence_record)
    output_bucket.store(validated)
    return evidence_trace_id
