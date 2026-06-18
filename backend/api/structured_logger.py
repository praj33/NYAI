"""
Structured JSON access logging for NYAI HTTP requests.
One JSON object per line (NDJSON) written to stderr via stdlib logging.
"""
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class JsonFormatter(logging.Formatter):
    """Emit log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        message = record.getMessage()
        try:
            json.loads(message)
            return message
        except json.JSONDecodeError:
            pass
        payload = getattr(record, "json_payload", None)
        if isinstance(payload, dict):
            return json.dumps(payload, default=str)
        return json.dumps(
            {
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
                "message": message,
                "log_level": record.levelname,
            },
            default=str,
        )


def _configure_access_logger() -> logging.Logger:
    logger = logging.getLogger("nyai.access")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


access_logger = _configure_access_logger()


def _extract_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _extract_error_code(response: Response) -> Optional[str]:
    header_code = response.headers.get("X-Error-Code")
    if header_code:
        return header_code
    try:
        body = getattr(response, "body", None)
        if body:
            data = json.loads(body.decode("utf-8"))
            if isinstance(data, dict) and "error_code" in data:
                return data.get("error_code")
    except (json.JSONDecodeError, UnicodeDecodeError, AttributeError, TypeError):
        pass
    return None


def _log_level_for_status(status_code: int) -> str:
    if status_code >= 500:
        return "ERROR"
    if status_code >= 400:
        return "WARNING"
    return "INFO"


def log_access_entry(
    *,
    request: Request,
    status_code: int,
    duration_ms: float,
    error_code: Optional[str] = None,
    log_level: Optional[str] = None,
) -> None:
    trace_id = getattr(request.state, "trace_id", "unknown")
    level = log_level or _log_level_for_status(status_code)
    entry: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        "trace_id": trace_id,
        "request_id": str(uuid.uuid4()),
        "endpoint": request.url.path,
        "method": request.method,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 1),
        "client_ip": _extract_client_ip(request),
        "error_code": error_code,
        "log_level": level,
    }
    line = json.dumps(entry, default=str)
    log_fn = access_logger.info
    if level == "WARNING":
        log_fn = access_logger.warning
    elif level == "ERROR":
        log_fn = access_logger.error
    log_fn(line)


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Record one structured JSON log line per HTTP request."""

    async def dispatch(self, request: Request, call_next) -> Response:
        from api.metrics import metrics_store

        start = time.perf_counter()
        metrics_store.increment_active()
        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start) * 1000
            status_code = response.status_code
            error_code = _extract_error_code(response)
            log_access_entry(
                request=request,
                status_code=status_code,
                duration_ms=duration_ms,
                error_code=error_code,
            )
            metrics_store.record_request(
                path=request.url.path,
                status_code=status_code,
                duration_ms=duration_ms,
            )
            return response
        except Exception:
            duration_ms = (time.perf_counter() - start) * 1000
            log_access_entry(
                request=request,
                status_code=500,
                duration_ms=duration_ms,
                error_code="INTERNAL_ERROR",
                log_level="ERROR",
            )
            metrics_store.record_request(
                path=request.url.path,
                status_code=500,
                duration_ms=duration_ms,
            )
            raise
        finally:
            metrics_store.decrement_active()
