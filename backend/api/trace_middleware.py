"""
Trace ID injection middleware — assigns uuid4 to request.state.trace_id.
"""
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class TraceIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.trace_id = str(uuid.uuid4())
        return await call_next(request)
