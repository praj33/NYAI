"""End-to-end smoke test for NYAI Phase IV + secondary endpoints."""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

LOG_PATH = Path(__file__).resolve().parents[2] / "debug-8a8fb3.log"


def _agent_log(location: str, message: str, data: dict, hypothesis_id: str, run_id: str) -> None:
    # #region agent log
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "sessionId": "8a8fb3",
                        "location": location,
                        "message": message,
                        "data": data,
                        "hypothesisId": hypothesis_id,
                        "timestamp": int(time.time() * 1000),
                        "runId": run_id,
                    }
                )
                + "\n"
            )
    except Exception:
        pass
    # #endregion


def _load_api_key() -> str:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("NYAI_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("NYAI_API_KEY not found in backend/.env")


def _http(method: str, url: str, headers: dict | None = None, body: dict | None = None) -> tuple[int, dict | str]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode()
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, raw
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, raw


def _test_live(base: str, key: str, run_id: str) -> list[dict]:
    results: list[dict] = []
    auth = {"X-API-Key": key}

    def record(name: str, status: int, ok: bool, detail: str = "") -> None:
        results.append({"name": name, "status": status, "ok": ok, "detail": detail[:200]})
        _agent_log("smoke_test_all.py", name, {"status": status, "ok": ok, "detail": detail[:200]}, "E2E", run_id)

    # Health (no auth)
    for path in ("/health", "/health/ready"):
        status, body = _http("GET", f"{base}{path}")
        ok = status == 200 and isinstance(body, dict)
        record(f"GET {path}", status, ok, str(body.get("status", body))[:200])

    # Auth guard
    status, _ = _http("GET", f"{base}/evidence/search?limit=1")
    record("GET /evidence/search no key", status, status == 401)

    # Query with correct schema
    query_body = {
        "query": "assault case in India",
        "jurisdiction_hint": "India",
        "user_context": {"role": "citizen", "confidence_required": True},
    }
    status, body = _http("POST", f"{base}/nyaya/query", headers=auth, body=query_body)
    trace_id = body.get("trace_id") if isinstance(body, dict) else None
    record("POST /nyaya/query", status, status == 200 and bool(trace_id), f"trace_id={trace_id}")

    if not trace_id:
        # Fallback to known stored trace
        trace_id = "410e46a5-57e0-4c78-8de8-c5e68a37f561"
        record("fallback trace", 0, True, trace_id)

    secondary = [
        f"/nyaya/case_summary?trace_id={trace_id}",
        f"/nyaya/legal_routes?trace_id={trace_id}",
        f"/nyaya/timeline?trace_id={trace_id}",
        f"/nyaya/glossary?trace_id={trace_id}",
        f"/nyaya/recommendation_status?trace_id={trace_id}",
    ]
    for path in secondary:
        status, body = _http("GET", f"{base}{path}", headers=auth)
        ok = status == 200
        detail = ""
        if path.startswith("/nyaya/case_summary") and isinstance(body, dict):
            statutes = body.get("key_statutes") or []
            detail = f"statutes={len(statutes)}"
            if statutes and isinstance(statutes[0], dict):
                title = statutes[0].get("title")
                ok = ok and isinstance(title, str) and not callable(title)
        record(f"GET {path.split('?')[0]}", status, ok, detail)

    status, body = _http("POST", f"{base}/evidence/verify", headers=auth, body={"trace_id": trace_id})
    ok = status == 200 and isinstance(body, dict) and body.get("verified") is True
    record("POST /evidence/verify", status, ok, str(body.get("integrity_status", body))[:200])

    status, body = _http(
        "POST",
        f"{base}/evidence/export",
        headers=auth,
        body={"trace_id": trace_id, "format": "summary"},
    )
    record("POST /evidence/export summary", status, status == 200, str(body.get("evidence_id", ""))[:200] if isinstance(body, dict) else "")

    status, body = _http("GET", f"{base}/evidence/{trace_id}", headers=auth)
    record("GET /evidence/{trace_id}", status, status == 200)

    status, body = _http("GET", f"{base}/evidence/search?limit=3", headers=auth)
    ok = status == 200 and isinstance(body, dict) and "results" in body
    record("GET /evidence/search", status, ok, f"count={body.get('count') if isinstance(body, dict) else ''}")

    return results


def _test_testclient(run_id: str) -> list[dict]:
    from fastapi.testclient import TestClient
    from api.main import app
    from api.router import response_cache

    os.environ.setdefault("NYAI_API_KEY", _load_api_key())
    key = os.environ["NYAI_API_KEY"]
    client = TestClient(app, raise_server_exceptions=False)
    results: list[dict] = []

    def record(name: str, status: int, ok: bool, detail: str = "") -> None:
        results.append({"name": name, "status": status, "ok": ok, "detail": detail[:200]})
        _agent_log("smoke_test_all.py:testclient", name, {"status": status, "ok": ok, "detail": detail[:200]}, "E2E", run_id)

    tid = "410e46a5-57e0-4c78-8de8-c5e68a37f561"
    with response_cache.lock:
        response_cache.cache.clear()

    r = client.get(f"/nyaya/case_summary?trace_id={tid}", headers={"X-API-Key": key})
    body = r.json()
    statutes = body.get("key_statutes") or []
    title_ok = bool(statutes) and isinstance(statutes[0].get("title"), str)
    record("TestClient case_summary L2", r.status_code, r.status_code == 200 and title_ok, str(statutes[:1]))

    r = client.post("/evidence/verify", json={"trace_id": tid}, headers={"X-API-Key": key})
    record("TestClient evidence/verify", r.status_code, r.status_code == 200 and r.json().get("verified"))

    return results


def main() -> int:
    run_id = "agent-smoke"
    if LOG_PATH.exists():
        LOG_PATH.unlink()

    key = _load_api_key()
    base = os.environ.get("SMOKE_BASE_URL", "http://localhost:8000").rstrip("/")
    render_base = os.environ.get("RENDER_BASE_URL", "https://nyaya-ai-0f02.onrender.com").rstrip("/")

    print("=== TestClient (L2 persistence) ===")
    tc_results = _test_testclient(run_id)
    for r in tc_results:
        mark = "PASS" if r["ok"] else "FAIL"
        print(f"  [{mark}] {r['name']} ({r['status']}) {r['detail']}")

    print("\n=== Live server smoke (local) ===")
    try:
        live_results = _test_live(base, key, run_id)
        for r in live_results:
            mark = "PASS" if r["ok"] else "FAIL"
            print(f"  [{mark}] {r['name']} ({r['status']}) {r['detail']}")
    except urllib.error.URLError as e:
        print(f"  [SKIP] Live server not reachable at {base}: {e}")
        live_results = []

    print(f"\n=== Render smoke ({render_base}) ===")
    try:
        render_results = _test_live(render_base, key, run_id)
        for r in render_results:
            mark = "PASS" if r["ok"] else "FAIL"
            print(f"  [{mark}] {r['name']} ({r['status']}) {r['detail']}")
    except urllib.error.URLError as e:
        print(f"  [SKIP] Render not reachable at {render_base}: {e}")
        render_results = []

    all_results = tc_results + live_results + render_results
    passed = sum(1 for r in all_results if r["ok"])
    total = len(all_results)
    print(f"\n=== SUMMARY: {passed}/{total} passed ===")
    _agent_log("smoke_test_all.py", "summary", {"passed": passed, "total": total}, "E2E", run_id)
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
