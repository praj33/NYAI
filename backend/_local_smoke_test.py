"""Local ARYA production hardening smoke tests against running uvicorn."""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
import httpx

load_dotenv(Path(__file__).resolve().parent / ".env")

KEY = os.environ.get("NYAI_API_KEY", "")
BASE = os.environ.get("SMOKE_BASE_URL", "http://127.0.0.1:8000")
PAYLOAD = {
    "query": "theft of mobile phone",
    "jurisdiction_hint": "India",
    "user_context": {"role": "citizen", "confidence_required": True},
}

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    status = "PASS" if ok else "FAIL"
    suffix = f" — {detail}" if detail else ""
    print(f"{status}: {name}{suffix}")


def main() -> int:
    if not KEY:
        print("FAIL: NYAI_API_KEY not set in backend/.env")
        return 1

    client = httpx.Client(base_url=BASE, timeout=120.0)

    r = client.get("/health")
    check("GET /health (no key)", r.status_code == 200, f"HTTP {r.status_code}")

    r = client.get("/health/ready")
    body = r.json()
    check(
        "GET /health/ready",
        r.status_code in (200, 503) and "dependencies" in body,
        f"status={body.get('status')}",
    )

    r = client.get("/metrics")
    metrics = r.json()
    check(
        "GET /metrics",
        r.status_code == 200 and "requests" in metrics and "uptime_seconds" in metrics,
        f"uptime={metrics.get('uptime_seconds')}s",
    )

    r = client.post("/nyaya/query", json=PAYLOAD)
    err = r.json().get("error_code") if r.headers.get("content-type", "").startswith("application/json") else ""
    check("POST /nyaya/query no key", r.status_code == 401, f"HTTP {r.status_code} error={err}")

    r = client.post("/nyaya/query", json=PAYLOAD, headers={"X-API-Key": KEY})
    trace = ""
    if r.headers.get("content-type", "").startswith("application/json"):
        trace = (r.json().get("trace_id") or "")[:8]
    check("POST /nyaya/query with key", r.status_code == 200, f"HTTP {r.status_code} trace={trace}...")
    if r.status_code == 200:
        rec = r.json().get("recommendation", {}).get("type")
        check(
            "recommendation.type present",
            rec in ("INFORM", "REVIEW", "ESCALATE", "INSUFFICIENT_DATA"),
            f"type={rec}",
        )

    r = client.post(
        "/nyaya/query",
        json=PAYLOAD,
        headers={"X-API-Key": "wrong-key"},
    )
    wrong = r.json().get("error_code") if r.headers.get("content-type", "").startswith("application/json") else ""
    check(
        "POST /nyaya/query wrong key",
        r.status_code == 401 and wrong == "INVALID_API_KEY",
        f"HTTP {r.status_code}",
    )

    failed = [x for x in results if not x[1]]
    print()
    print(f"Summary: {len(results) - len(failed)}/{len(results)} smoke checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
