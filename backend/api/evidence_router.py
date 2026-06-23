from __future__ import annotations
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

logger = logging.getLogger("nyai.evidence.api")
evidence_router = APIRouter(prefix="/evidence", tags=["evidence"])


class VerifyRequest(BaseModel):
    trace_id: str


class ExportRequest(BaseModel):
    trace_id: str
    format: str = "json"


class CompareRequest(BaseModel):
    trace_id_a: str
    trace_id_b: str


def _evidence():
    from services.evidence_service import evidence_service
    return evidence_service


def _replay():
    from services.replay_service import replay_service
    return replay_service


def _verify():
    from services.verification_service import verification_service
    return verification_service


# ── SPECIFIC ROUTES FIRST ──────────────────────────────────────

@evidence_router.get("/search")
async def search_evidence(
    recommendation: Optional[str] = Query(None),
    jurisdiction: Optional[str] = Query(None),
    statute: Optional[str] = Query(None),
    input_hash: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None, description="ISO date lower bound (inclusive)"),
    date_to: Optional[str] = Query(None, description="ISO date upper bound (inclusive)"),
    evidence_version: Optional[str] = Query(None, description="Filter by evidence format version e.g. 1.0.0"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return _evidence().search(
        recommendation=recommendation, jurisdiction=jurisdiction,
        statute_keyword=statute, input_hash=input_hash,
        date_from=date_from, date_to=date_to, evidence_version=evidence_version,
        limit=limit, offset=offset,
    )


@evidence_router.get("/hash/{input_hash}")
async def get_by_hash(input_hash: str):
    pkg = _evidence().search_by_input_hash(input_hash)
    if not pkg:
        raise HTTPException(status_code=404, detail={"error_code": "EVIDENCE_NOT_FOUND", "input_hash": input_hash})
    return pkg.to_dict()


@evidence_router.get("/recommendation/{rec_type}")
async def get_by_recommendation(rec_type: str, limit: int = Query(20, ge=1, le=100)):
    valid = {"INFORM", "REVIEW", "ESCALATE", "INSUFFICIENT_DATA"}
    if rec_type.upper() not in valid:
        raise HTTPException(status_code=400, detail={"error_code": "INVALID_RECOMMENDATION_TYPE", "valid": list(valid)})
    results = _replay().replay_by_recommendation(rec_type.upper(), limit=limit)
    return {"recommendation_type": rec_type.upper(), "count": len(results), "results": results}


@evidence_router.get("/jurisdiction/{country}")
async def get_by_jurisdiction(country: str, limit: int = Query(20, ge=1, le=100)):
    results = _replay().replay_by_jurisdiction(country, limit=limit)
    return {"jurisdiction": country, "count": len(results), "results": results}


@evidence_router.get("/statute")
async def get_by_statute(keyword: str = Query(...), limit: int = Query(20, ge=1, le=50)):
    results = _replay().replay_by_statute(keyword, limit=limit)
    return {"statute_keyword": keyword, "count": len(results), "results": results}


@evidence_router.get("/version/{evidence_version}")
async def get_by_evidence_version(evidence_version: str, limit: int = Query(20, ge=1, le=100)):
    packages = _evidence().list_by_evidence_version(evidence_version, limit=limit)
    return {
        "evidence_version": evidence_version,
        "count": len(packages),
        "results": [
            {
                "trace_id": p.identity.trace_id,
                "evidence_id": p.identity.evidence_id,
                "recommendation_type": p.decision.recommendation_type,
                "created_at": p.identity.created_at,
            }
            for p in packages
        ],
    }


@evidence_router.post("/verify")
async def verify_evidence(request: VerifyRequest):
    return _verify().verify_by_trace_id(request.trace_id)


@evidence_router.post("/verify/chain")
async def verify_chain():
    return _verify().verify_chain()


@evidence_router.post("/compare")
async def compare_evidence(request: CompareRequest):
    return _replay().compare_evidence(request.trace_id_a, request.trace_id_b)


@evidence_router.post("/export")
async def export_evidence(request: ExportRequest):
    result = _evidence().export(request.trace_id, fmt=request.format)
    if not result:
        raise HTTPException(status_code=404, detail={"error_code": "EVIDENCE_NOT_FOUND", "trace_id": request.trace_id})
    return result


# ── CATCH-ALL LAST ─────────────────────────────────────────────

@evidence_router.get("/{trace_id}")
async def get_evidence(trace_id: str):
    pkg = _evidence().get_by_trace_id(trace_id)
    if not pkg:
        raise HTTPException(status_code=404, detail={"error_code": "EVIDENCE_NOT_FOUND", "trace_id": trace_id})
    return pkg.to_dict()
