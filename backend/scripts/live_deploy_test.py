"""Live deployment smoke test for Render + Vercel."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

RENDER = "https://nyai-backend-n9h8.onrender.com"
FRONTEND = "https://frontend-xi-three-imewbfjyjk.vercel.app"


def load_key() -> str:
    for line in Path(__file__).resolve().parents[1].joinpath(".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("NYAI_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("NYAI_API_KEY not found")


def req(method: str, url: str, body=None, headers=None):
    h = dict(headers or {})
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Content-Type", "application/json")
    for k, v in h.items():
        request.add_header(k, v)
    try:
        with urllib.request.urlopen(request, timeout=120) as resp:
            raw = resp.read().decode()
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, raw[:300]
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, raw[:300]


def main() -> int:
    key = load_key()
    auth = {"X-API-Key": key}
    results: list[tuple[str, bool, str]] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        results.append((name, ok, detail[:200]))
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail[:150]}")

    status, body = req("GET", f"{RENDER}/health")
    check("GET /health", status == 200 and isinstance(body, dict) and body.get("status") == "healthy", str(body))

    status, body = req("GET", f"{RENDER}/health/ready")
    ok_ready = status == 200 and isinstance(body, dict)
    detail = f"status={body.get('status')} checks={body.get('checks_passed')}/{body.get('checks_total')}" if ok_ready else str(body)
    check("GET /health/ready", ok_ready, detail)
    if isinstance(body, dict):
        for name, dep in (body.get("dependencies") or {}).items():
            print(f"       {name}: {dep.get('status')} - {str(dep.get('detail', ''))[:80]}")

    status, body = req("GET", f"{RENDER}/")
    check("GET / (API root)", status == 200 and isinstance(body, dict) and "endpoints" in body, "gateway ok" if status == 200 else str(body)[:80])

    status, _ = req("GET", f"{RENDER}/evidence/search?limit=1")
    check("Auth no key -> 401", status == 401, str(status))

    try:
        status, _ = req("GET", f"{RENDER}/debug/nonce-state")
        check("Debug routes disabled", status == 404, str(status))
    except Exception as exc:
        check("Debug routes disabled", False, f"timeout/error: {exc}")

    query_body = {
        "query": "assault case in India",
        "jurisdiction_hint": "India",
        "user_context": {"role": "citizen", "confidence_required": True},
    }
    status, body = req("POST", f"{RENDER}/nyaya/query", query_body, auth)
    trace = body.get("trace_id") if isinstance(body, dict) and not body.get("error_code") else None
    rec = (body.get("recommendation") or {}).get("type") if isinstance(body, dict) else None
    check("POST /nyaya/query", status == 200 and bool(trace) and rec is not None, f"trace={trace} rec={rec}")

    if trace:
        status, body = req("GET", f"{RENDER}/nyaya/trace/{trace}", headers=auth)
        check("GET /nyaya/trace/{id}", status == 200, "replay ok" if status == 200 else str(body)[:80])

        status, body = req("GET", f"{RENDER}/evidence/search?limit=5", headers=auth)
        count = body.get("count") if isinstance(body, dict) else None
        check("GET /evidence/search", status == 200 and isinstance(body, dict), f"count={count}")

        for ep in ("case_summary", "legal_routes", "timeline", "glossary", "recommendation_status"):
            status, ep_body = req("GET", f"{RENDER}/nyaya/{ep}?trace_id={trace}", headers=auth)
            extra = ""
            if ep == "case_summary" and isinstance(ep_body, dict):
                extra = f" statutes={len(ep_body.get('key_statutes') or [])}"
            check(f"GET /nyaya/{ep}", status == 200, str(status) + extra)

        status, body = req("POST", f"{RENDER}/evidence/verify", {"trace_id": trace}, auth)
        check(
            "POST /evidence/verify",
            status == 200 and isinstance(body, dict) and body.get("verified") is not None,
            str(body.get("integrity_status")) if isinstance(body, dict) else str(body),
        )

        status, body = req("POST", f"{RENDER}/evidence/export", {"trace_id": trace, "format": "summary"}, auth)
        check(
            "POST /evidence/export",
            status == 200 and isinstance(body, dict) and "evidence_id" in body,
            str(body.get("recommendation")) if isinstance(body, dict) else str(body),
        )

        status, body = req("POST", f"{RENDER}/evidence/export", {"trace_id": trace, "format": "json"}, auth)
        check(
            "POST /evidence/export json",
            status == 200 and isinstance(body, dict) and body.get("export_format") == "nyai_evidence_v1" and "evidence" in body,
            "json export ok" if status == 200 else str(body)[:80],
        )

        status, body = req("GET", f"{RENDER}/evidence/{trace}", headers=auth)
        check("GET /evidence/{trace_id}", status == 200, "ok" if status == 200 else str(body)[:100])
    else:
        check("trace-dependent tests", False, "query failed - no trace_id")

    try:
        request = urllib.request.Request(FRONTEND, method="GET")
        with urllib.request.urlopen(request, timeout=30) as resp:
            html = resp.read(800).decode(errors="replace")
            check("Frontend HTML loads", resp.status == 200 and len(html) > 100, f"status={resp.status}")
    except Exception as exc:
        check("Frontend HTML loads", False, str(exc))

    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    print(f"\n=== LIVE SUMMARY: {passed}/{total} passed ===")
    print(f"Backend: {RENDER}")
    print(f"Frontend: {FRONTEND}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
