import sys
import os
from pathlib import Path
sys.path.append('.')
sys.path.append('..')

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv:
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
try:
    from api.router import router
except ImportError:
    from .router import router

from api.health import health_router
from api.metrics import metrics_router
from api.structured_logger import StructuredLoggingMiddleware
from api.rate_limiter import RateLimiterMiddleware
from api.security import APIKeyAuthMiddleware
from api.trace_middleware import TraceIdMiddleware
from api.error_codes import ErrorCode

import uvicorn

# Create FastAPI app
app = FastAPI(
    title="Nyaya Legal AI API Gateway",
    description="Sovereign-compliant API gateway for multi-agent legal intelligence",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    os.getenv("FRONTEND_URL", ""),
]
allowed_origins = [o for o in allowed_origins if o]

# Global exception handler — FAIL CLOSED
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    from fastapi.responses import JSONResponse
    trace_id = getattr(request.state, 'trace_id', 'unknown')
    return JSONResponse(
        status_code=500,
        content={
            "error_code": ErrorCode.INTERNAL_ERROR,
            "message": f"TANTRA FAIL CLOSED: {str(exc)}",
            "trace_id": trace_id
        }
    )

# Production hardening middleware (innermost registered first)
app.add_middleware(APIKeyAuthMiddleware)
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(StructuredLoggingMiddleware)
app.add_middleware(TraceIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers — health and metrics before nyaya (no auth required)
app.include_router(health_router)
app.include_router(metrics_router)
app.include_router(router)

# Include procedure router
try:
    from api.procedure_router import procedure_router
    app.include_router(procedure_router)
except ImportError:
    pass

# Include enhanced legal database endpoints
try:
    from legal_database.enhanced_procedure_endpoints import *
except ImportError:
    pass

# Include debug router (for development only)
try:
    from api.debug_router import debug_router
    app.include_router(debug_router)
except ImportError:
    pass

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Nyaya Legal AI API Gateway",
        "version": "1.0.0",
        "description": "Sovereign-compliant multi-agent legal intelligence platform",
        "endpoints": {
            "query": "POST /nyaya/query",
            "multi_jurisdiction": "POST /nyaya/multi_jurisdiction",
            "explain_reasoning": "POST /nyaya/explain_reasoning",
            "feedback": "POST /nyaya/feedback",
            "trace": "GET /nyaya/trace/{trace_id}",
            "case_summary": "GET /nyaya/case_summary?trace_id={trace_id}",
            "legal_routes": "GET /nyaya/legal_routes?trace_id={trace_id}",
            "timeline": "GET /nyaya/timeline?trace_id={trace_id}",
            "glossary": "GET /nyaya/glossary?trace_id={trace_id}",
            "jurisdiction_info": "GET /nyaya/jurisdiction_info?jurisdiction={code}",
            "recommendation_status": "GET /nyaya/recommendation_status?trace_id={trace_id}",
            "rl_signal": "POST /nyaya/rl_signal",
            "procedure_analyze": "POST /nyaya/procedures/analyze",
            "procedure_summary": "GET /nyaya/procedures/summary/{country}/{domain}",
            "evidence_assess": "POST /nyaya/procedures/evidence/assess",
            "failure_analyze": "POST /nyaya/procedures/failure/analyze",
            "procedure_compare": "POST /nyaya/procedures/compare",
            "procedure_list": "GET /nyaya/procedures/list",
            "procedure_schemas": "GET /nyaya/procedures/schemas",
            "enhanced_analysis": "GET /nyaya/procedures/enhanced_analysis/{jurisdiction}/{domain}",
            "domain_classification": "GET /nyaya/procedures/domain_classification/{jurisdiction}",
            "legal_sections": "GET /nyaya/procedures/legal_sections/{jurisdiction}/{domain}",
            "health": "GET /health",
            "health_live": "GET /health/live",
            "health_ready": "GET /health/ready",
            "metrics": "GET /metrics",
            "docs": "GET /docs"
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
