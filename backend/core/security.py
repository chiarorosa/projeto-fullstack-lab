from __future__ import annotations

import hashlib
import os
import secrets
import time
from collections import deque
from dataclasses import dataclass
from threading import Lock

from fastapi import Header, HTTPException, Request, status
from core.env import load_environment


load_environment()


_TRUE_VALUES = {"1", "true", "yes", "on"}
_VALID_ENVS = {"development", "staging", "production", "test"}


@dataclass(frozen=True)
class SecuritySettings:
    app_env: str
    cors_allow_origins: list[str]
    auth_enabled: bool
    api_bearer_token: str
    rate_limit_enabled: bool
    rate_limit_window_seconds: int
    rate_limit_execute_requests: int
    rate_limit_provider_test_requests: int


def _parse_bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in _TRUE_VALUES


def _parse_int_env(name: str, default: int, minimum: int = 1) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        parsed = int(raw.strip())
    except (TypeError, ValueError):
        return default
    return max(minimum, parsed)


def load_security_settings() -> SecuritySettings:
    app_env = (os.getenv("APP_ENV") or "development").strip().lower()
    if app_env not in _VALID_ENVS:
        app_env = "development"

    auth_default = app_env != "development"

    cors_allow_origins = [
        value.strip()
        for value in (
            os.getenv("CORS_ALLOW_ORIGINS")
            or "http://localhost:5173,http://localhost:3000"
        ).split(",")
        if value.strip()
    ]

    return SecuritySettings(
        app_env=app_env,
        cors_allow_origins=cors_allow_origins,
        auth_enabled=_parse_bool_env("AUTH_ENABLED", auth_default),
        api_bearer_token=(os.getenv("API_BEARER_TOKEN") or "").strip(),
        rate_limit_enabled=_parse_bool_env("RATE_LIMIT_ENABLED", True),
        rate_limit_window_seconds=_parse_int_env(
            "RATE_LIMIT_WINDOW_SECONDS", 60, minimum=1
        ),
        rate_limit_execute_requests=_parse_int_env(
            "RATE_LIMIT_EXECUTE_REQUESTS", 10, minimum=1
        ),
        rate_limit_provider_test_requests=_parse_int_env(
            "RATE_LIMIT_PROVIDER_TEST_REQUESTS", 30, minimum=1
        ),
    )


def validate_security_settings(settings: SecuritySettings) -> None:
    if settings.app_env == "development":
        return

    if not settings.cors_allow_origins:
        raise RuntimeError(
            "CORS_ALLOW_ORIGINS must contain at least one origin in non-development environments."
        )

    if settings.auth_enabled and not settings.api_bearer_token:
        raise RuntimeError(
            "API_BEARER_TOKEN is required when AUTH_ENABLED=true in non-development environments."
        )

    if settings.rate_limit_enabled:
        if settings.rate_limit_window_seconds <= 0:
            raise RuntimeError("RATE_LIMIT_WINDOW_SECONDS must be greater than zero.")
        if settings.rate_limit_execute_requests <= 0:
            raise RuntimeError("RATE_LIMIT_EXECUTE_REQUESTS must be greater than zero.")
        if settings.rate_limit_provider_test_requests <= 0:
            raise RuntimeError(
                "RATE_LIMIT_PROVIDER_TEST_REQUESTS must be greater than zero."
            )


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._buckets: dict[str, deque[float]] = {}
        self._lock = Lock()

    def consume(self, key: str, limit: int, window_seconds: int) -> tuple[bool, int]:
        now = time.time()
        with self._lock:
            bucket = self._buckets.setdefault(key, deque())
            while bucket and now - bucket[0] >= window_seconds:
                bucket.popleft()

            if len(bucket) >= limit:
                retry_after = max(1, int(window_seconds - (now - bucket[0])) + 1)
                return False, retry_after

            bucket.append(now)
            return True, 0


SECURITY_SETTINGS = load_security_settings()
_RATE_LIMITER = InMemoryRateLimiter()


def _unauthorized_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid bearer token.",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def require_bearer_token(
    request: Request, authorization: str | None = Header(default=None)
) -> None:
    if not SECURITY_SETTINGS.auth_enabled:
        return

    if not authorization:
        raise _unauthorized_exception()

    scheme, _, token = authorization.partition(" ")
    token = token.strip()
    if scheme.lower() != "bearer" or not token:
        raise _unauthorized_exception()

    if not secrets.compare_digest(token, SECURITY_SETTINGS.api_bearer_token):
        raise _unauthorized_exception()

    request.state.auth_subject = hashlib.sha256(token.encode("utf-8")).hexdigest()[:16]


def _request_identity(request: Request) -> str:
    auth_subject = getattr(request.state, "auth_subject", None)
    if auth_subject:
        return f"token:{auth_subject}"

    client_host = request.client.host if request.client else "unknown"
    return f"ip:{client_host}"


def _enforce_rate_limit(request: Request, *, scope: str, limit: int) -> None:
    if not SECURITY_SETTINGS.rate_limit_enabled:
        return

    bucket_key = f"{scope}:{_request_identity(request)}"
    allowed, retry_after = _RATE_LIMITER.consume(
        bucket_key,
        limit,
        SECURITY_SETTINGS.rate_limit_window_seconds,
    )

    if allowed:
        return

    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "code": "rate_limited",
            "message": "Too many requests.",
            "retry_after_seconds": retry_after,
        },
        headers={"Retry-After": str(retry_after)},
    )


async def rate_limit_execute(request: Request) -> None:
    _enforce_rate_limit(
        request,
        scope="execute",
        limit=SECURITY_SETTINGS.rate_limit_execute_requests,
    )


async def rate_limit_provider_test(request: Request) -> None:
    _enforce_rate_limit(
        request,
        scope="provider_test",
        limit=SECURITY_SETTINGS.rate_limit_provider_test_requests,
    )
