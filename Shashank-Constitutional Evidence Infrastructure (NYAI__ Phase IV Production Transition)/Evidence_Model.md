# Evidence Model — `evidence_v1`

## Schema Version

- `EVIDENCE_SCHEMA_VERSION = "evidence_v1"`
- `EVIDENCE_FORMAT_VERSION = "1.0.0"`

## Dataclasses

### EvidenceIdentity
| Field | Type | Description |
|-------|------|-------------|
| `trace_id` | str | Unified trace from middleware through response |
| `request_id` | str | Deterministic request identifier from input hash |
| `evidence_id` | str | SHA256 identity digest (see below) |
| `schema_version` | str | Always `evidence_v1` |
| `evidence_version` | str | Format version `1.0.0` |
| `origin` | str | `nyai-legal-engine` |
| `created_at` | str | ISO timestamp from stored entry |

### EvidenceInput
| Field | Type | Description |
|-------|------|-------------|
| `raw_query` | str | Original user query |
| `cleaned_query` | str | Post-`clean_query()` text |
| `jurisdiction_hint` | Optional[str] | Detected or user-provided jurisdiction |
| `domain_hint` | Optional[str] | Classified legal domain |
| `input_hash` | str | SHA256 of canonical input payload |

### EvidenceDecision
| Field | Type | Description |
|-------|------|-------------|
| `recommendation_type` | str | INFORM / REVIEW / ESCALATE / INSUFFICIENT_DATA |
| `confidence` | float | Overall recommendation confidence |
| `rationale` | str | Human-readable recommendation rationale |
| `jurisdiction` | str | Resolved jurisdiction code |
| `domain` | str | Resolved domain |
| `jurisdiction_confidence` | float | Jurisdiction detector confidence |

### EvidenceReasoning
| Field | Type | Description |
|-------|------|-------------|
| `facts` | List[Dict] | Structured Fact objects |
| `applicable_statutes` | List[Dict] | Matched statutes |
| `case_laws` | List[Dict] | Retrieved case law |
| `explanation_chain` | List[Dict] | ExplanationStep objects |
| `rule_application` | List[Dict] | RuleApplication from analysis |
| `observer_steps` | List[Dict] | ObserverPipeline stage records |
| `observer_validation` | Dict | Schema validation gate result |

### EvidenceHashes
| Field | Type | Description |
|-------|------|-------------|
| `input_hash` | str | Determinism input hash |
| `output_hash` | str | Determinism output hash |
| `entry_hash` | str | OutputBucket entry tamper seal |
| `determinism_version` | str | e.g. `3.0.0` |

### EvidenceStorageMetadata
| Field | Type | Description |
|-------|------|-------------|
| `stored_at` | str | Bucket storage timestamp |
| `storage_file` | str | `output_logs/nyai_output_log.jsonl` |
| `ledger_index` | Optional[int] | Future ledger cross-reference |
| `replay_source` | str | `output_bucket` |

### EvidenceReplayMetadata
| Field | Type | Description |
|-------|------|-------------|
| `is_replayable` | bool | Default `True` |
| `replay_inputs` | Optional[Dict] | `{trace_id, input_hash}` |
| `last_replayed_at` | Optional[str] | Future replay tracking |
| `replay_count` | int | Future replay counter |

### EvidencePackage (root)
Combines all sections above plus:
- `integrity_status`: `UNVERIFIED` → `VERIFIED` or `TAMPERED`
- `attachments`: timeline, glossary, legal_route, risk_flags, full_response, etc.

## evidence_id Computation

```
evidence_id = SHA256(f"{trace_id}:{request_id}:{timestamp}")
```

## from_stored_entry() Mapping

| OutputBucket JSONL field | EvidencePackage field |
|--------------------------|----------------------|
| `trace_id` | `identity.trace_id` |
| `full_response.request_id` | `identity.request_id` |
| `timestamp` | `identity.created_at`, `storage.stored_at` |
| `input_hash` | `input.input_hash`, `hashes.input_hash` |
| `output_hash` | `hashes.output_hash` |
| `entry_hash` | `hashes.entry_hash` |
| `full_response.recommendation` | `decision.*` |
| `full_response.statutes` | `reasoning.applicable_statutes` |
| `full_response.observer_steps` | `reasoning.observer_steps` |
| Remaining response fields | `attachments.*` |

## integrity_status Lifecycle

```
UNVERIFIED  →  (verify_by_trace_id)  →  VERIFIED | TAMPERED | UNKNOWN
```

- **UNVERIFIED**: Default on package creation
- **VERIFIED**: `entry_hash` recomputation matches stored hash
- **TAMPERED**: Hash mismatch detected
- **UNKNOWN**: Evidence not found in bucket

## Complete EvidencePackage JSON Example

Structurally complete example with all top-level sections. Arrays are condensed to one representative item each.

> For a production-scale export (full statutes, observer_steps, attachments), see [`example_exported_evidence.json`](./example_exported_evidence.json) (`export_format: nyai_evidence_v1`).

```json
{
  "identity": {
    "trace_id": "097792dd-40f3-443b-905d-10208e89a138",
    "request_id": "req_780eafc1be76",
    "evidence_id": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
    "schema_version": "evidence_v1",
    "evidence_version": "1.0.0",
    "origin": "nyai-legal-engine",
    "created_at": "2026-06-11T06:07:00.965329"
  },
  "input": {
    "raw_query": "theft of mobile phone",
    "cleaned_query": "theft of mobile phone",
    "jurisdiction_hint": "India",
    "domain_hint": "criminal",
    "input_hash": "780eafc1be76cfb8cb22ea90bfc20e01ec2b5e27a26de424f69ba0038e804330"
  },
  "decision": {
    "recommendation_type": "INFORM",
    "confidence": 0.75,
    "rationale": "Query resolved with 2 statute(s) at 75% confidence",
    "jurisdiction": "IN",
    "domain": "criminal",
    "jurisdiction_confidence": 1.0
  },
  "reasoning": {
    "facts": [
      {
        "fact_id": "F1",
        "statement": "User query: theft of mobile phone",
        "source": "input"
      }
    ],
    "applicable_statutes": [
      {
        "act": "Indian Penal Code",
        "year": 1860,
        "section": "378",
        "title": "Theft"
      }
    ],
    "case_laws": [],
    "explanation_chain": [
      {
        "step_number": 1,
        "description": "Query received and cleaned",
        "source": "QueryCleaner"
      }
    ],
    "rule_application": [
      {
        "application": "Theft",
        "law_id": "Indian Penal Code:378"
      }
    ],
    "observer_steps": [
      {
        "stage": "query_received",
        "trace_id": "097792dd-40f3-443b-905d-10208e89a138",
        "timestamp": "2026-06-11T06:07:00.965329",
        "observed": {"raw_query": "theft of mobile phone"}
      }
    ],
    "observer_validation": {
      "schema_valid": true,
      "determinism_verified": true,
      "validation_status": "PASS",
      "violations": []
    }
  },
  "hashes": {
    "input_hash": "780eafc1be76cfb8cb22ea90bfc20e01ec2b5e27a26de424f69ba0038e804330",
    "output_hash": "461b94d02f3b43ab3769ab88ad37d4fce9822095cf24cd0feec44abca095d1c6",
    "entry_hash": "cb88284c78f65c7515bed693e06538070942220123042d8e0de8cca506e4a55c",
    "determinism_version": "3.0.0"
  },
  "storage": {
    "stored_at": "2026-06-11T06:07:00.965329",
    "storage_file": "output_logs/nyai_output_log.jsonl",
    "ledger_index": null,
    "replay_source": "output_bucket"
  },
  "replay": {
    "is_replayable": true,
    "replay_inputs": {
      "trace_id": "097792dd-40f3-443b-905d-10208e89a138",
      "input_hash": "780eafc1be76cfb8cb22ea90bfc20e01ec2b5e27a26de424f69ba0038e804330"
    },
    "last_replayed_at": null,
    "replay_count": 0
  },
  "integrity_status": "VERIFIED",
  "attachments": {
    "timeline": [
      {"step": "Filing of FIR", "eta": "Varies"}
    ],
    "glossary": [
      {"term": "Theft", "definition": "Dishonestly taking movable property"}
    ],
    "legal_route": [
      "query_cleaning",
      "query_understanding",
      "hybrid_retrieval"
    ],
    "risk_flags": [],
    "full_response": {}
  }
}
```
