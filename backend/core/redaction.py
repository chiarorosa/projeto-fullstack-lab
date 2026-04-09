from __future__ import annotations

import re
from typing import Any


_SENSITIVE_KEYS = {
    "apikey",
    "api_key",
    "authorization",
    "secret",
    "token",
    "x-api-key",
}

_SECRET_PATTERNS = [
    re.compile(r"\b(sk-[A-Za-z0-9_\-]{8,})\b"),
    re.compile(r"\b(sk-or-[A-Za-z0-9_\-]{8,})\b"),
    re.compile(r"(?i)(bearer\s+)([A-Za-z0-9_\-\.]{8,})"),
]


def redact_text(value: str) -> str:
    redacted = value
    for pattern in _SECRET_PATTERNS:
        redacted = pattern.sub(
            lambda m: (m.group(1) if m.lastindex and m.lastindex > 1 else "")
            + "[REDACTED]",
            redacted,
        )
    return redacted


def _looks_sensitive_key(key: str) -> bool:
    normalized = key.strip().lower().replace("-", "_")
    if normalized in _SENSITIVE_KEYS:
        return True
    return "secret" in normalized or "token" in normalized or "api_key" in normalized


def redact_payload(payload: Any) -> Any:
    if isinstance(payload, dict):
        out: dict[str, Any] = {}
        for key, value in payload.items():
            if _looks_sensitive_key(str(key)):
                out[key] = "[REDACTED]"
            else:
                out[key] = redact_payload(value)
        return out

    if isinstance(payload, list):
        return [redact_payload(item) for item in payload]

    if isinstance(payload, str):
        return redact_text(payload)

    return payload
