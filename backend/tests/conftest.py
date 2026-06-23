"""Shared pytest hooks for NYAI sprint test suites."""
import os
import pytest

_TEST_API_KEY = "test-key-production-hardening"


def pytest_configure(config):
    """Use a consistent test API key before test modules import the app."""
    os.environ["NYAI_API_KEY"] = _TEST_API_KEY


@pytest.fixture(autouse=True)
def _isolate_rate_limiter():
    """Reset in-memory rate limit buckets between tests."""
    from api.rate_limiter import reset_rate_limiter
    reset_rate_limiter()
    yield
    reset_rate_limiter()


@pytest.fixture(autouse=True)
def _inject_nyaya_auth_for_convergence(request, monkeypatch):
    """Convergence tests call /nyaya/* without headers; inject the test key."""
    if request.module.__name__ != "test_tantra_convergence":
        return
    monkeypatch.setenv("NYAI_API_KEY", _TEST_API_KEY)
    client = request.module.client
    original_post = client.post
    original_get = client.get

    def _with_auth(kwargs):
        headers = dict(kwargs.get("headers") or {})
        headers.setdefault("X-API-Key", _TEST_API_KEY)
        kwargs["headers"] = headers
        return kwargs

    def post(url, **kwargs):
        return original_post(url, **_with_auth(kwargs))

    def get(url, **kwargs):
        return original_get(url, **_with_auth(kwargs))

    monkeypatch.setattr(client, "post", post)
    monkeypatch.setattr(client, "get", get)
