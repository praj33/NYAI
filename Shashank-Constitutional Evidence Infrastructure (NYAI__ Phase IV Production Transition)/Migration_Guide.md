# Migration Guide — Phase IV Evidence Infrastructure

## Before

- **L1 only**: `response_cache` (OrderedDict, max 500 entries)
- Secondary endpoints (`/case_summary`, `/legal_routes`, `/timeline`, `/glossary`, `/recommendation_status`) returned **404 after server restart**
- No canonical evidence object or evidence API
- OutputBucket index used sequential count (O(n) linear scan)

## After

- **L1**: `response_cache` — unchanged, write-through on every `/query`
- **L2**: `EvidenceRepository` — persistent fallback from OutputBucket JSONL
- Secondary endpoints fall back to `evidence_repository.get_raw_by_trace_id()` when cache misses
- **No URL changes** for existing `/nyaya/*` consumers
- **320+ existing entries** in `output_logs/nyai_output_log.jsonl` are immediately accessible — no migration script required

## Consumer Impact

| Consumer | Action Required |
|----------|----------------|
| Frontend (`nyayaApi.js`) | None — `/nyaya/*` contract unchanged |
| `/nyaya/case_summary` etc. | None — now survives restart via L2 fallback |
| New evidence consumers | Add `X-API-Key` header, use `/evidence/*` endpoints |

## Before / After Data Shape

Phase IV does not require a migration script. Existing JSONL lines are read in place and wrapped on demand via `EvidencePackage.from_stored_entry()`. Field mapping is documented in [`Evidence_Model.md`](./Evidence_Model.md#from_stored_entry-mapping).

### Before — raw OutputBucket JSONL line

One line in `output_logs/nyai_output_log.jsonl` (tantra_v3 `full_response` nested inside):

```json
{
  "trace_id": "097792dd-40f3-443b-905d-10208e89a138",
  "input_hash": "780eafc1be76cfb8cb22ea90bfc20e01ec2b5e27a26de424f69ba0038e804330",
  "output_hash": "461b94d02f3b43ab3769ab88ad37d4fce9822095cf24cd0feec44abca095d1c6",
  "timestamp": "2026-06-11T06:07:00.965329",
  "entry_hash": "cb88284c78f65c7515bed693e06538070942220123042d8e0de8cca506e4a55c",
  "full_response": {
    "trace_id": "097792dd-40f3-443b-905d-10208e89a138",
    "request_id": "req_780eafc1be76",
    "schema_version": "tantra_v3",
    "reasoning_trace": {
      "original_query": "theft of mobile phone",
      "cleaned_query": "theft of mobile phone"
    },
    "jurisdiction": "India",
    "jurisdiction_detected": "India",
    "jurisdiction_confidence": 1.0,
    "domain": "criminal",
    "recommendation": {
      "type": "INFORM",
      "confidence": 0.75,
      "rationale": "Query resolved with 2 statute(s) at 75% confidence"
    },
    "facts": [{"fact_id": "F1", "statement": "User query: theft of mobile phone", "source": "input"}],
    "statutes": [{"act": "Indian Penal Code", "year": 1860, "section": "378", "title": "Theft"}],
    "determinism_proof": {
      "input_hash": "780eafc1be76cfb8cb22ea90bfc20e01ec2b5e27a26de424f69ba0038e804330",
      "output_hash": "461b94d02f3b43ab3769ab88ad37d4fce9822095cf24cd0feec44abca095d1c6",
      "version": "3.0.0"
    },
    "timeline": [{"step": "Filing of FIR", "eta": "Varies"}],
    "glossary": [{"term": "Theft", "definition": "Dishonestly taking movable property"}],
    "legal_route": ["query_cleaning", "hybrid_retrieval"]
  }
}
```

### After — canonical EvidencePackage

Same trace_id, mapped by `from_stored_entry()` to the constitutional evidence schema:

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
    "facts": [{"fact_id": "F1", "statement": "User query: theft of mobile phone", "source": "input"}],
    "applicable_statutes": [{"act": "Indian Penal Code", "year": 1860, "section": "378", "title": "Theft"}],
    "case_laws": [],
    "explanation_chain": [],
    "rule_application": [],
    "observer_steps": [],
    "observer_validation": {}
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
  "integrity_status": "UNVERIFIED",
  "attachments": {
    "timeline": [{"step": "Filing of FIR", "eta": "Varies"}],
    "glossary": [{"term": "Theft", "definition": "Dishonestly taking movable property"}],
    "legal_route": ["query_cleaning", "hybrid_retrieval"]
  }
}
```

## Deployment Steps

1. Deploy backend with Phase IV code
2. Verify `GET /health/ready` shows `evidence_repository: PASS`
3. Spot-check `GET /evidence/search?limit=3` with API key
4. Confirm existing trace_ids resolve via `/evidence/{trace_id}`

## Future Path

| Layer | Upgrade |
|-------|---------|
| L1 cache | Redis with TTL |
| L2 storage | S3/GCS JSONL with date-prefix sharding |
| Index | Redis HASH replacing in-memory `_index` dict |
