"""TANTRA Convergence — Final Determinism Proof + Schema Validation"""
import urllib.request, json, sys

QUERY = "theft of mobile phone"
RUNS = 3
hashes = []

for i in range(RUNS):
    try:
        req_obj = urllib.request.Request(
            'http://127.0.0.1:8000/nyaya/query',
            json.dumps({
                'query': QUERY,
                'jurisdiction_hint': 'India',
                'user_context': {'role': 'citizen', 'confidence_required': True}
            }).encode(),
            {'Content-Type': 'application/json'}
        )
        r = urllib.request.urlopen(req_obj, timeout=60)
        d = json.loads(r.read())
    except urllib.error.HTTPError as he:
        print(f"HTTP Error {he.code}: {he.reason}")
        print("Response body:")
        print(he.read().decode('utf-8'))
        sys.exit(1)
    except Exception as e:
        print(f"Error making request: {e}")
        sys.exit(1)

    # Check canonical fields
    canonical = ['trace_id','request_id','input_hash','legal_context','facts',
                'analysis','recommendation','explanation_chain','risk_flags',
                'determinism_proof','timestamp']
    missing = [f for f in canonical if f not in d]
    
    # Check forbidden old fields
    forbidden = ['enforcement_decision','decision_basis']
    present_forbidden = [f for f in forbidden if f in d]

    # Check forbidden old enum values
    rec = d.get('recommendation', {})
    rec_type = rec.get('type', '')

    proof = d.get('determinism_proof', {})
    ih = proof.get('input_hash', 'MISSING')
    oh = proof.get('output_hash', 'MISSING')
    hashes.append((ih, oh))

    # Check facts are structured objects
    facts = d.get('facts', [])
    facts_structured = all(isinstance(f, dict) and 'fact_id' in f for f in facts)

    # Check rule_application are structured
    analysis = d.get('analysis', {})
    rules = analysis.get('rule_application', [])
    rules_structured = all(isinstance(r, dict) and 'law_id' in r for r in rules)

    # Check explanation_chain are structured
    chain = d.get('explanation_chain', [])
    chain_structured = all(isinstance(s, dict) and 'step_number' in s for s in chain)

    # Check observer_validation
    obs = d.get('observer_validation', {})

    print(f"=== Run {i+1} ===")
    print(f"  input_hash:         {ih}")
    print(f"  output_hash:        {oh}")
    print(f"  version:            {proof.get('version', 'MISSING')}")
    print(f"  recommendation:     type={rec_type}, confidence={rec.get('confidence')}")
    print(f"  legal_context:      {d.get('legal_context', {})}")
    print(f"  facts:              {len(facts)} items, structured={facts_structured}")
    print(f"  rule_application:   {len(rules)} items, structured={rules_structured}")
    print(f"  explanation_chain:  {len(chain)} steps, structured={chain_structured}")
    print(f"  risk_flags:         {d.get('risk_flags', [])}")
    print(f"  observer_status:    {obs.get('validation_status', 'MISSING')}")
    print(f"  determinism_ok:     {obs.get('determinism_verified', 'MISSING')}")
    print(f"  trace_continuity:   {obs.get('trace_continuity_check', 'MISSING')}")
    print(f"  schema_valid:       {obs.get('schema_valid', 'MISSING')}")
    print(f"  metadata.schema:    {d.get('metadata', {}).get('schema', 'MISSING')}")
    if missing: print(f"  !! MISSING: {missing}")
    if present_forbidden: print(f"  !! FORBIDDEN: {present_forbidden}")
    if rec_type in ('ALLOW', 'DENY', 'BLOCK'): print(f"  !! OLD ENUM: {rec_type}")
    print()

print("=== DETERMINISM CHECK ===")
if len(set(h[0] for h in hashes)) == 1 and len(set(h[1] for h in hashes)) == 1:
    print(f"PASS: All {RUNS} runs produced identical hashes")
    print(f"  input_hash:  {hashes[0][0]}")
    print(f"  output_hash: {hashes[0][1]}")
else:
    print("FAIL: Hashes differ across runs")
    for i, (ih, oh) in enumerate(hashes):
        print(f"  Run {i+1}: input={ih[:16]}... output={oh[:16]}...")
