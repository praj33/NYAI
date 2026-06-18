"""
Thread-safe in-memory metrics store for NYAI production observability.
Resets on process restart (no persistence in this sprint).
"""
import threading
from collections import deque
from datetime import datetime, timezone
from typing import Deque, List

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class MetricsStore:
    """Module-level singleton metrics store."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.started_at = _utc_now_iso()
        self.request_count = 0
        self.error_count = 0
        self.rate_limited_count = 0
        self.auth_failure_count = 0
        self.validation_error_count = 0
        self.errors_4xx = 0
        self.active_requests = 0
        self.latency_samples: Deque[float] = deque(maxlen=1000)

    def increment_active(self) -> None:
        with self._lock:
            self.active_requests += 1

    def decrement_active(self) -> None:
        with self._lock:
            self.active_requests = max(0, self.active_requests - 1)

    def record_request(
        self,
        *,
        path: str,
        status_code: int,
        duration_ms: float,
    ) -> None:
        if not path.startswith("/nyaya/"):
            return

        with self._lock:
            self.request_count += 1
            if status_code >= 500:
                self.error_count += 1
            if 400 <= status_code < 500:
                self.errors_4xx += 1
            if status_code == 429:
                self.rate_limited_count += 1
            if status_code == 401:
                self.auth_failure_count += 1
            if status_code == 422:
                self.validation_error_count += 1
            if path == "/nyaya/query" or path.endswith("/query"):
                self.latency_samples.append(duration_ms)

    def snapshot(self) -> dict:
        with self._lock:
            started = datetime.fromisoformat(self.started_at.replace("Z", "+00:00"))
            uptime = (datetime.now(timezone.utc) - started).total_seconds()
            samples: List[float] = list(self.latency_samples)
            avg_latency = sum(samples) / len(samples) if samples else 0.0
            return {
                "service": "nyaya-api-gateway",
                "started_at": self.started_at,
                "uptime_seconds": round(uptime, 1),
                "requests": {
                    "total": self.request_count,
                    "errors_5xx": self.error_count,
                    "errors_4xx": self.errors_4xx,
                    "rate_limited": self.rate_limited_count,
                    "auth_failures": self.auth_failure_count,
                    "validation_errors": self.validation_error_count,
                },
                "latency": {
                    "average_ms": round(avg_latency, 1),
                    "samples_window": 1000,
                },
                "active_requests": self.active_requests,
            }

    def reset_counters(self) -> None:
        with self._lock:
            self.request_count = 0
            self.error_count = 0
            self.rate_limited_count = 0
            self.auth_failure_count = 0
            self.validation_error_count = 0
            self.errors_4xx = 0
            self.latency_samples.clear()


metrics_store = MetricsStore()

metrics_router = APIRouter(tags=["metrics"])


@metrics_router.get("/metrics")
async def get_metrics(request: Request) -> JSONResponse:
    """Expose in-memory operational metrics (no auth required)."""
    return JSONResponse(content=metrics_store.snapshot())
