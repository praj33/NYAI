# Postman / Newman API Evidence Capture

## Import collection

1. Open Postman → **Import** → select `backend/Nyaya_AI_Backend.postman_collection.json`
2. Create environment variable `base_url` = `http://localhost:8000` (or `8001` on Windows if blocked)

## Manual run (screenshot evidence)

Run in order and capture screenshots of the **Response** panel:

| # | Request | Pass criteria |
|---|---------|---------------|
| 1 | `GET /health` | `status: healthy` |
| 2 | `POST /nyaya/query` | `schema_version: tantra_v3`, `metadata.formatted: true`, all 11 canonical fields |
| 3 | `GET /nyaya/trace/{trace_id}` | Non-empty `event_chain`, `tamper_verified: true` |
| 4 | `GET /nyaya/output/{trace_id}` | `verification.verified: true` |

Sample query body for step 2:

```json
{
  "query": "theft of mobile phone",
  "jurisdiction_hint": "India",
  "user_context": { "role": "citizen", "confidence_required": true }
}
```

## Newman export (CI-style evidence)

```bash
npm install -g newman
newman run backend/Nyaya_AI_Backend.postman_collection.json \
  --env-var base_url=http://localhost:8000 \
  --reporters cli,json \
  --reporter-json-export SHASHANK-NYAI_CONVERGENCE_IMPLEMENTATION_PLAN/api_evidence/postman_run_export.json
```

Save screenshots to this folder as `query_response.png`, `trace_replay.png`, etc.
