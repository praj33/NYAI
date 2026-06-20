"""
Per-IP sliding window rate limiter for /nyaya/* routes.

Window: 60 seconds (RATE_LIMIT_PER_MINUTE)
Burst: 1 second (RATE_LIMIT_BURST) — limits rapid-fire requests per IP
"""
import os
import threading
import time
from collections import defaultdict, deque
from typing import Deque, Dict, Tuple

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from api.error_codes import ErrorCode

_PROTECTED_PREFIX = "/nyaya/"
_WINDOW_SECONDS = 60
_BURST_WINDOW_SECONDS = 1
_PRUNE_INTERVAL_SECONDS = 300


def _limit_per_minute() -> int:
    raw = os.environ.get("RATE_LIMIT_PER_MINUTE", "60")
    try:
        return max(1, int(raw))
    except ValueError:
        return 60


def _burst_limit() -> int:
    raw = os.environ.get("RATE_LIMIT_BURST", "10")
    try:
        return max(1, int(raw))
    except ValueError:
        return 10


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
        self._burst_buckets: Dict[str, Deque[float]] = defaultdict(deque)
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
            stale = [
                ip
                for ip, ts in self._buckets.items()
                if not ts or ts[-1] < cutoff
            ]
            for ip in stale:
                self._buckets.pop(ip, None)
                self._burst_buckets.pop(ip, None)
                self._locks.pop(ip, None)
            self._last_prune = now

    def _check_window(
        self,
        bucket: Deque[float],
        *,
        now: float,
        window_seconds: float,
        limit: int,
    ) -> Tuple[bool, int]:
        cutoff = now - window_seconds
        while bucket and bucket[0] < cutoff:
            bucket.popleft()

        if len(bucket) >= limit:
            retry_after = max(1, int(window_seconds - (now - bucket[0]) + 1))
            return False, retry_after

        bucket.append(now)
        return True, 0

    def check(self, ip: str, limit: int, burst_limit: int) -> Tuple[bool, int, str]:
        now = time.monotonic()
        self._prune_stale_ips(now)
        lock = self._get_lock(ip)
        with lock:
            burst_ok, burst_retry = self._check_window(
                self._burst_buckets[ip],
                now=now,
                window_seconds=_BURST_WINDOW_SECONDS,
                limit=burst_limit,
            )
            if not burst_ok:
                if self._burst_buckets[ip]:
                    self._burst_buckets[ip].pop()
                return False, burst_retry, "burst"

            minute_ok, minute_retry = self._check_window(
                self._buckets[ip],
                now=now,
                window_seconds=_WINDOW_SECONDS,
                limit=limit,
            )
            if not minute_ok:
                if self._burst_buckets[ip]:
                    self._burst_buckets[ip].pop()
                return False, minute_retry, "minute"

            return True, 0, ""

    def unrecord(self, ip: str) -> None:
        lock = self._get_lock(ip)
        with lock:
            for store in (self._buckets, self._burst_buckets):
                bucket = store.get(ip)
                if bucket:
                    bucket.pop()


_limiter = _SlidingWindowLimiter()


def reset_rate_limiter() -> None:
    """Reset in-memory rate limit state (used between isolated tests)."""
    with _limiter._global_lock:
        _limiter._buckets.clear()
        _limiter._burst_buckets.clear()
        _limiter._locks.clear()
        _limiter._last_prune = time.monotonic()


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Sliding-window per-IP rate limiter with burst protection for /nyaya/* routes."""

    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith(_PROTECTED_PREFIX):
            return await call_next(request)

        limit = _limit_per_minute()
        burst = _burst_limit()
        ip = _client_ip(request)
        allowed, retry_after, limit_type = _limiter.check(ip, limit, burst)
        if not allowed:
            if limit_type == "burst":
                message = (
                    f"Burst limit of {burst} requests per second exceeded"
                )
            else:
                message = (
                    f"Rate limit of {limit} requests per minute exceeded"
                )
            return JSONResponse(
                status_code=429,
                content={
                    "error_code": ErrorCode.RATE_LIMIT_EXCEEDED,
                    "message": message,
                    "retry_after": retry_after,
                    "trace_id": _trace_id(request),
                },
                headers={
                    "content-type": "application/json",
                    "Retry-After": str(retry_after),
                    "X-Error-Code": ErrorCode.RATE_LIMIT_EXCEEDED,
                },
            )

        response = await call_next(request)
        return response
