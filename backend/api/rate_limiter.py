# Pure stdlib sliding-window rate limiter (slowapi listed in requirements but not used here).
"""
Per-IP sliding window rate limiter for /nyaya/* routes.

Window: 60 seconds
Limit: RATE_LIMIT_PER_MINUTE env var (default 60)
"""
import os
import threading
import time
from collections import defaultdict, deque
from typing import Deque, Dict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

_PROTECTED_PREFIX = "/nyaya/"
_WINDOW_SECONDS = 60
_PRUNE_INTERVAL_SECONDS = 300


def _limit_per_minute() -> int:
    raw = os.environ.get("RATE_LIMIT_PER_MINUTE", "60")
    try:
        return max(1, int(raw))
    except ValueError:
        return 60


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _trace_id(request: Request) -> str:
    return getattr(request.state, "trace_id", "unknown")


class _SlidingWindowLimiter:
    def __init__(self) -> None:
        self._buckets: Dict[str, Deque[float]] = defaultdict(deque)
        self._locks: Dict[str, threading.Lock] = defaultdict(threading.Lock)
        self._global_lock = threading.Lock()
        self._last_prune = time.monotonic()

    def _get_lock(self, ip: str) -> threading.Lock:
        with self._global_lock:
            return self._locks[ip]

    def _prune_stale_ips(self, now: float) -> None:
        if now - self._last_prune < _PRUNE_INTERVAL_SECONDS:
            return
        cutoff = now - _WINDOW_SECONDS
        with self._global_lock:
            stale = [ip for ip, ts in self._buckets.items() if not ts or ts[-1] < cutoff]
            for ip in stale:
                self._buckets.pop(ip, None)
                self._locks.pop(ip, None)
            self._last_prune = now

    def check(self, ip: str, limit: int) -> tuple[bool, int]:
        now = time.monotonic()
        self._prune_stale_ips(now)
        lock = self._get_lock(ip)
        with lock:
            bucket = self._buckets[ip]
            cutoff = now - _WINDOW_SECONDS
            while bucket and bucket[0] < cutoff:
                bucket.popleft()

            if len(bucket) >= limit:
                retry_after = max(1, int(_WINDOW_SECONDS - (now - bucket[0]) + 1))
                return False, retry_after

            bucket.append(now)
            return True, 0

    def unrecord(self, ip: str) -> None:
        lock = self._get_lock(ip)
        with lock:
            bucket = self._buckets.get(ip)
            if bucket:
                bucket.pop()


_limiter = _SlidingWindowLimiter()


def reset_rate_limiter() -> None:
    """Reset in-memory rate limit state (used between isolated tests)."""
    with _limiter._global_lock:
        _limiter._buckets.clear()
        _limiter._locks.clear()
        _limiter._last_prune = time.monotonic()


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Sliding-window per-IP rate limiter for /nyaya/* routes."""

    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith(_PROTECTED_PREFIX):
            return await call_next(request)

        limit = _limit_per_minute()
        ip = _client_ip(request)
        allowed, retry_after = _limiter.check(ip, limit)
        if not allowed:
            error_code = "RATE_LIMIT_EXCEEDED"
            return JSONResponse(
                status_code=429,
                content={
                    "error_code": error_code,
                    "message": f"Rate limit of {limit} requests per minute exceeded",
                    "retry_after": retry_after,
                    "trace_id": _trace_id(request),
                },
            headers={
                "content-type": "application/json",
                "Retry-After": str(retry_after),
                "X-Error-Code": error_code,
            },
            )

        response = await call_next(request)
        return response
