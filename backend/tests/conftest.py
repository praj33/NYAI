"""
Shared pytest configuration for NYAI backend tests.

Ensures NYAI_API_KEY is set before application import and injects the API key
into TestClient requests for convergence tests, while leaving auth-hardening
tests free to omit or override the header.
"""
import os

import pytest

os.environ.setdefault("NYAI_API_KEY", "test-key-ci-default")

_SKIP_AUTH_INJECT = (
    "authentication",
    "bypass",
    "metrics_endpoint",
    "deployment_validation",
)

from fastapi.testclient import TestClient as _TestClient

_original_request = _TestClient.request


def _patched_request(self, method, url, **kwargs):
    headers = dict(kwargs.get("headers") or {})
    current_test = os.environ.get("PYTEST_CURRENT_TEST", "")
    should_skip = any(token in current_test for token in _SKIP_AUTH_INJECT)
    if (
        not should_skip
        and "X-API-Key" not in headers
        and os.environ.get("NYAI_API_KEY")
    ):
        headers["X-API-Key"] = os.environ["NYAI_API_KEY"]
        kwargs["headers"] = headers
    return _original_request(self, method, url, **kwargs)


_TestClient.request = _patched_request


@pytest.fixture(autouse=True)
def _reset_rate_limiter_between_tests():
    from api.rate_limiter import reset_rate_limiter

    reset_rate_limiter()
    yield
    reset_rate_limiter()
