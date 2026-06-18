"""
Health check endpoints for NYAI API gateway.
Liveness and readiness probes — no API key required.
"""
import os
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter
from fastapi.responses import JSONResponse

health_router = APIRouter(tags=["health"])

SERVICE_NAME = "nyaya-api-gateway"
SERVICE_VERSION = "1.0.0"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _basic_health_payload() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "timestamp": _utc_now_iso(),
    }


def output_bucket_check() -> Dict[str, str]:
    try:
        from tantra.output_bucket import output_bucket

        output_bucket.retrieve("__health_probe__")
        return {"status": "PASS", "detail": "output_bucket accessible"}
    except Exception as exc:
        return {"status": "FAIL", "detail": f"output_bucket error: {exc}"}


def ledger_check() -> Dict[str, str]:
    try:
        from provenance_chain.hash_chain_ledger import HashChainLedger

        ledger_path = os.environ.get("PROVENANCE_LEDGER_PATH", "provenance_ledger.json")
        ledger = HashChainLedger(ledger_path)
        ledger.verify_chain_integrity()
        return {"status": "PASS", "detail": "ledger accessible"}
    except Exception as exc:
        return {"status": "FAIL", "detail": f"ledger error: {exc}"}


def retriever_check() -> Dict[str, str]:
    try:
        import api.router as nyaya_router

        if getattr(nyaya_router, "advisor", None) is not None:
            return {"status": "PASS", "detail": "legal advisor initialized"}
        return {"status": "DEGRADED", "detail": "legal advisor not initialized"}
    except Exception as exc:
        return {"status": "DEGRADED", "detail": f"retriever check error: {exc}"}


def model_check() -> Dict[str, str]:
    if os.environ.get("GROQ_API_KEY"):
        return {"status": "PASS", "detail": "GROQ_API_KEY configured"}
    return {"status": "DEGRADED", "detail": "GROQ_API_KEY not set; LLM calls may fail"}


@health_router.get("/health")
async def health() -> Dict[str, Any]:
    return _basic_health_payload()


@health_router.get("/health/live")
async def health_live() -> Dict[str, Any]:
    return _basic_health_payload()


@health_router.get("/health/ready")
async def health_ready() -> JSONResponse:
    dependencies = {
        "output_bucket": output_bucket_check(),
        "ledger": ledger_check(),
        "retriever": retriever_check(),
        "model": model_check(),
    }

    statuses = [dep["status"] for dep in dependencies.values()]
    checks_passed = sum(1 for s in statuses if s == "PASS")
    checks_total = len(statuses)

    if any(s == "FAIL" for s in statuses):
        overall = "unavailable"
        http_status = 503
    elif any(s == "DEGRADED" for s in statuses):
        overall = "degraded"
        http_status = 200
    else:
        overall = "ready"
        http_status = 200

    body = {
        "status": overall,
        "timestamp": _utc_now_iso(),
        "dependencies": dependencies,
        "checks_passed": checks_passed,
        "checks_total": checks_total,
    }
    return JSONResponse(status_code=http_status, content=body)
