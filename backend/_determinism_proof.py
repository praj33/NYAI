import urllib.request, json

QUERY = "theft of mobile phone"
hashes = []

for i in range(3):
    r = urllib.request.urlopen(urllib.request.Request(
        'http://127.0.0.1:8000/nyaya/query',
        json.dumps({'query': QUERY, 'jurisdiction_hint': 'India', 'user_context': {'role': 'citizen', 'confidence_required': True}}).encode(),
        {'Content-Type': 'application/json'}
    ), timeout=60)
    d = json.loads(r.read())
    required = ['trace_id','request_id','input_hash','legal_context','facts','analysis','recommendation','explanation_chain','risk_flags','determinism_proof','timestamp']
    missing = [f for f in required if f not in d]
    forbidden = ['enforcement_decision','decision_basis']
    present_forbidden = [f for f in forbidden if f in d]
    proof = d.get('determinism_proof', {})
    hashes.append((proof.get('input_hash','X'), proof.get('output_hash','X')))
    rec = d.get('recommendation', {})
    lc = d.get('legal_context', {})
    an = d.get('analysis', {})
    print(f"=== Run {i+1} ===")
    print(f"  input_hash:        {hashes[-1][0]}")
    print(f"  output_hash:       {hashes[-1][1]}")
    print(f"  version:           {proof.get('version', 'MISSING')}")
    print(f"  recommendation:    type={rec.get('type')}, confidence={rec.get('confidence')}")
    print(f"  rationale:         {rec.get('rationale', '')[:80]}")
    print(f"  legal_context:     jurisdiction={lc.get('jurisdiction')}, domain={lc.get('domain')}, laws={lc.get('applicable_laws')}")
    print(f"  facts:             {len(d.get('facts', []))} items")
    print(f"  analysis keys:     {list(an.keys())}")
    print(f"  rule_application:  {an.get('rule_application', [])}")
    print(f"  explanation_chain: {len(d.get('explanation_chain', []))} steps")
    print(f"  risk_flags:        {d.get('risk_flags', [])}")
    if missing: print(f"  !! MISSING FIELDS: {missing}")
    if present_forbidden: print(f"  !! FORBIDDEN FIELDS: {present_forbidden}")
    print()

print("=== DETERMINISM CHECK ===")
if len(set(h[0] for h in hashes)) == 1 and len(set(h[1] for h in hashes)) == 1:
    print(f"PASS: All 3 runs produced identical hashes")
    print(f"  input_hash:  {hashes[0][0]}")
    print(f"  output_hash: {hashes[0][1]}")
else:
    print("FAIL: Hashes differ across runs")
