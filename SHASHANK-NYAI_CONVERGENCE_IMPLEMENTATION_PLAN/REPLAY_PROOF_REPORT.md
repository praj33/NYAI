# REPLAY PROOF REPORT

**Sprint:** NYAI Canonical Convergence Build  
**Branch:** `feature/tantra-convergence-ready`  
**Date:** 12 June 2026  
**Audit:** [CONVERGENCE_AUDIT_REPORT.md](./CONVERGENCE_AUDIT_REPORT.md)

---

## Replay Capability Matrix

| Capability | Before Sprint | After Sprint |
|------------|---------------|--------------|
| `GET /nyaya/trace/{trace_id}` | Hardcoded stub (empty event_chain) | Real data from `output_bucket` |
| `GET /nyaya/output/{trace_id}` | Not available | Full stored output + verification |
| Hash chain ledger | Disconnected | Appended after every query |
| Tamper detection | Bucket only | Bucket + trace endpoint `tamper_verified` |
| External auditor access | In-memory cache only | Disk-persisted JSONL + HTTP endpoints |

---

## curl Commands

```bash
# 1. Execute query
curl -s -X POST http://localhost:8000/nyaya/query \
  -H "Content-Type: application/json" \
  -d '{"query":"theft of mobile phone","jurisdiction_hint":"India","user_context":{"role":"citizen","confidence_required":true}}'

# 2. Replay trace
curl -s http://localhost:8000/nyaya/trace/{trace_id}

# 3. Retrieve stored output
curl -s http://localhost:8000/nyaya/output/{trace_id}
```

---

## Actual Response Samples (Phase 6)

**Trace replay** ([`trace_replay_proof.json`](./trace_replay_proof.json)):
- `trace_id`: `e20fb600-7104-43c5-9869-9c4aa8423d82`
- `event_chain`: 8 stages (non-empty)
- `tamper_verified`: `true`
- `input_hash`: `780eafc1be76cfb8cb22ea90bfc20e01ec2b5e27a26de424f69ba0038e804330`

**Output retrieval** ([`output_proof.json`](./output_proof.json)):
- `verification.verified`: `true`
- `hash_proof.tamper_detected`: `false`
- `stored_output.full_response.schema_version`: `tantra_v3`
- `stored_output.full_response.answer_disclaimer`: present

---

## Hash Chain Entry Example

```json
{
  "index": 1,
  "timestamp": "2026-06-11T06:07:00.967182Z",
  "event_hash": "44f40afd00e0f096badc84c1ef3a2896a9bfb1162558c83a240cecff29d79dca",
  "prev_hash": "genesis",
  "signed_event": {
    "trace_id": "097792dd-40f3-443b-905d-10208e89a138",
    "input_hash": "780eafc1be76cfb8cb22ea90bfc20e01ec2b5e27a26de424f69ba0038e804330",
    "output_hash": "461b94d02f3b43ab3769ab88ad37d4fce9822095cf24cd0feec44abca095d1c6",
    "schema_version": "tantra_v3",
    "recommendation_type": "INFORM"
  }
}
```

Chain integrity: each `prev_hash` links to previous `event_hash`.
