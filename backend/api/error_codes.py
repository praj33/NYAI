"""
Central error code registry for NYAI API responses and telemetry.

Import ErrorCode constants across middleware, handlers, and health checks
instead of scattering string literals.
"""
from typing import Dict, TypedDict


class ErrorClassification(TypedDict):
    http_status: int
    category: str
    description: str


class ErrorCode:
    SCHEMA_VALIDATION_ERROR = "SCHEMA_VALIDATION_ERROR"
    TRACE_CONTINUITY_ERROR = "TRACE_CONTINUITY_ERROR"
    HASH_MISMATCH_ERROR = "HASH_MISMATCH_ERROR"
    DEPENDENCY_FAILURE = "DEPENDENCY_FAILURE"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    UNAUTHORIZED = "UNAUTHORIZED"
    INVALID_API_KEY = "INVALID_API_KEY"
    AUTH_CONFIGURATION_ERROR = "AUTH_CONFIGURATION_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    QUERY_PROCESSING_ERROR = "QUERY_PROCESSING_ERROR"
    ADVISOR_NOT_INITIALIZED = "ADVISOR_NOT_INITIALIZED"
    INVALID_NONCE = "INVALID_NONCE"


ERROR_CLASSIFICATION: Dict[str, ErrorClassification] = {
    ErrorCode.SCHEMA_VALIDATION_ERROR: {
        "http_status": 500,
        "category": "pipeline",
        "description": "Observer rejects response schema",
    },
    ErrorCode.TRACE_CONTINUITY_ERROR: {
        "http_status": 500,
        "category": "pipeline",
        "description": "trace_id mutated mid-pipeline",
    },
    ErrorCode.HASH_MISMATCH_ERROR: {
        "http_status": 500,
        "category": "pipeline",
        "description": "Ledger hash tamper detected",
    },
    ErrorCode.DEPENDENCY_FAILURE: {
        "http_status": 503,
        "category": "operational",
        "description": "Required dependency unavailable",
    },
    ErrorCode.INTERNAL_ERROR: {
        "http_status": 500,
        "category": "system",
        "description": "Unhandled exception",
    },
    ErrorCode.RATE_LIMIT_EXCEEDED: {
        "http_status": 429,
        "category": "security",
        "description": "Per-IP rate limit exceeded",
    },
    ErrorCode.UNAUTHORIZED: {
        "http_status": 401,
        "category": "security",
        "description": "Missing API key header",
    },
    ErrorCode.INVALID_API_KEY: {
        "http_status": 401,
        "category": "security",
        "description": "Wrong API key value",
    },
    ErrorCode.AUTH_CONFIGURATION_ERROR: {
        "http_status": 503,
        "category": "security",
        "description": "NYAI_API_KEY env var not set",
    },
    ErrorCode.VALIDATION_ERROR: {
        "http_status": 422,
        "category": "client",
        "description": "Pydantic schema rejection",
    },
    ErrorCode.NOT_FOUND: {
        "http_status": 404,
        "category": "client",
        "description": "Resource not found",
    },
    ErrorCode.QUERY_PROCESSING_ERROR: {
        "http_status": 500,
        "category": "pipeline",
        "description": "Query pipeline failure",
    },
    ErrorCode.ADVISOR_NOT_INITIALIZED: {
        "http_status": 503,
        "category": "operational",
        "description": "Legal advisor not initialized",
    },
    ErrorCode.INVALID_NONCE: {
        "http_status": 400,
        "category": "security",
        "description": "Nonce invalid or expired",
    },
}
