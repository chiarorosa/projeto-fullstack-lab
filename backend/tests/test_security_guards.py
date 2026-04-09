import unittest
from unittest.mock import patch

from fastapi import HTTPException
from starlette.requests import Request

from core.security import (
    InMemoryRateLimiter,
    SecuritySettings,
    rate_limit_execute,
    require_bearer_token,
)


def _build_request() -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [],
        "client": ("127.0.0.1", 12345),
    }
    return Request(scope)


class SecurityGuardsTests(unittest.IsolatedAsyncioTestCase):
    async def test_require_bearer_token_rejects_missing_token(self) -> None:
        settings = SecuritySettings(
            app_env="test",
            cors_allow_origins=["http://localhost:5173"],
            auth_enabled=True,
            api_bearer_token="test-token",
            rate_limit_enabled=True,
            rate_limit_window_seconds=60,
            rate_limit_execute_requests=5,
            rate_limit_provider_test_requests=5,
        )

        with patch("core.security.SECURITY_SETTINGS", settings):
            with self.assertRaises(HTTPException) as ctx:
                await require_bearer_token(_build_request(), authorization=None)

        self.assertEqual(ctx.exception.status_code, 401)

    async def test_require_bearer_token_accepts_valid_token(self) -> None:
        settings = SecuritySettings(
            app_env="test",
            cors_allow_origins=["http://localhost:5173"],
            auth_enabled=True,
            api_bearer_token="test-token",
            rate_limit_enabled=True,
            rate_limit_window_seconds=60,
            rate_limit_execute_requests=5,
            rate_limit_provider_test_requests=5,
        )

        request = _build_request()
        with patch("core.security.SECURITY_SETTINGS", settings):
            await require_bearer_token(request, authorization="Bearer test-token")

        self.assertTrue(hasattr(request.state, "auth_subject"))

    async def test_execute_rate_limit_returns_429_after_limit(self) -> None:
        settings = SecuritySettings(
            app_env="test",
            cors_allow_origins=["http://localhost:5173"],
            auth_enabled=False,
            api_bearer_token="",
            rate_limit_enabled=True,
            rate_limit_window_seconds=60,
            rate_limit_execute_requests=1,
            rate_limit_provider_test_requests=5,
        )

        request = _build_request()

        with (
            patch("core.security.SECURITY_SETTINGS", settings),
            patch("core.security._RATE_LIMITER", InMemoryRateLimiter()),
        ):
            await rate_limit_execute(request)

            with self.assertRaises(HTTPException) as ctx:
                await rate_limit_execute(request)

        self.assertEqual(ctx.exception.status_code, 429)
