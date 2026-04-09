from __future__ import annotations

import base64
import hashlib
import hmac
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class SecretSettings:
    encryption_key: str


def load_secret_settings() -> SecretSettings:
    return SecretSettings(
        encryption_key=(os.getenv("CREDENTIAL_ENCRYPTION_KEY") or "").strip(),
    )


SECRET_SETTINGS = load_secret_settings()


def _is_development_env() -> bool:
    return (os.getenv("APP_ENV") or "development").strip().lower() == "development"


def validate_secret_settings(*, app_env: str) -> None:
    if app_env == "development":
        return
    if not SECRET_SETTINGS.encryption_key:
        raise RuntimeError(
            "CREDENTIAL_ENCRYPTION_KEY is required in non-development environments."
        )


def _derive_key() -> bytes:
    raw_key = SECRET_SETTINGS.encryption_key
    if not raw_key and _is_development_env():
        raw_key = "dev-only-insecure-credential-key"
    if not raw_key:
        raise RuntimeError(
            "Missing CREDENTIAL_ENCRYPTION_KEY. Cannot encrypt/decrypt credentials."
        )
    return hashlib.sha256(raw_key.encode("utf-8")).digest()


def _xor(data: bytes, key: bytes) -> bytes:
    return bytes(data[i] ^ key[i % len(key)] for i in range(len(data)))


def encrypt_secret(raw_secret: str) -> str:
    key = _derive_key()
    raw = raw_secret.encode("utf-8")
    cipher = _xor(raw, key)
    mac = hmac.new(key, cipher, hashlib.sha256).digest()
    token = base64.urlsafe_b64encode(mac + cipher).decode("ascii")
    return token


def decrypt_secret(token: str) -> str:
    key = _derive_key()
    try:
        payload = base64.urlsafe_b64decode(token.encode("ascii"))
    except Exception as exc:
        raise RuntimeError("Invalid encrypted credential payload.") from exc

    if len(payload) < 32:
        raise RuntimeError("Invalid encrypted credential payload.")

    mac = payload[:32]
    cipher = payload[32:]
    expected = hmac.new(key, cipher, hashlib.sha256).digest()
    if not hmac.compare_digest(mac, expected):
        raise RuntimeError("Credential integrity check failed.")

    plain = _xor(cipher, key)
    return plain.decode("utf-8")
