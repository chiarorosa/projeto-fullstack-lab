from __future__ import annotations

import os
from typing import Optional

import httpx

from models.schemas import ProviderTestRequest, ProviderTestResponse


_PROVIDER_ENV_KEYS = {
    "openai": "OPENAI_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google": "GOOGLE_API_KEY",
}
_PROVIDER_LABELS = {
    "openai": "OpenAI",
    "openrouter": "OpenRouter",
    "anthropic": "Anthropic",
    "google": "Google",
}
_KEYED_PROVIDERS = set(_PROVIDER_ENV_KEYS.keys())


def _normalize_provider(provider: str) -> str:
    if provider == "opencode":
        return "openrouter"
    return provider


def provider_requires_api_key(provider: str) -> bool:
    return _normalize_provider(provider) in _KEYED_PROVIDERS


def provider_env_var_name(provider: str) -> Optional[str]:
    return _PROVIDER_ENV_KEYS.get(_normalize_provider(provider))


def resolve_provider_env_api_key(provider: str) -> Optional[str]:
    env_var = provider_env_var_name(provider)
    if not env_var:
        return None
    value = (os.getenv(env_var) or "").strip()
    return value or None


def resolve_effective_api_key(
    *,
    provider: str,
    api_key: Optional[str],
    credential_api_key: Optional[str],
) -> tuple[Optional[str], Optional[str]]:
    normalized = _normalize_provider(provider)
    if normalized not in _KEYED_PROVIDERS:
        return None, None

    explicit_api_key = (api_key or "").strip()
    if explicit_api_key:
        return explicit_api_key, "api_key"

    credential_key = (credential_api_key or "").strip()
    if credential_key:
        return credential_key, "credential_ref"

    env_key = resolve_provider_env_api_key(normalized)
    if env_key:
        return env_key, "environment"

    return None, None


def build_missing_api_key_message(provider: str) -> str:
    normalized = _normalize_provider(provider)
    provider_label = _PROVIDER_LABELS.get(normalized, normalized.capitalize())
    env_var = provider_env_var_name(normalized)
    if env_var:
        return (
            f"No API key available for {provider_label}. "
            f"Provide API Key input, set credentialRef, or configure {env_var} in the backend environment."
        )
    return f"{provider_label} API key is required."


def _normalize_base_url(base_url: Optional[str], default: str) -> str:
    value = (base_url or default).strip()
    return value.rstrip("/")


def _extract_error_message(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        payload = None

    message: Optional[str] = None
    if isinstance(payload, dict):
        error_value = payload.get("error")
        if isinstance(error_value, dict):
            message = error_value.get("message")
        elif isinstance(error_value, str):
            message = error_value
        if not message and isinstance(payload.get("message"), str):
            message = payload.get("message")
        if not message and isinstance(payload.get("detail"), str):
            message = payload.get("detail")

    if not message:
        message = response.text.strip() or "Unexpected provider response."

    compact = " ".join(message.split())
    return compact[:220]


def _safe_json(response: httpx.Response) -> Optional[dict]:
    try:
        payload = response.json()
    except ValueError:
        return None
    if isinstance(payload, dict):
        return payload
    return None


async def _check_openai_like(
    provider_label: str,
    api_key: str,
    base_url: str,
) -> ProviderTestResponse:
    endpoint = f"{base_url}/models"
    headers = {"Authorization": f"Bearer {api_key}"}

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(endpoint, headers=headers)

    payload = _safe_json(response)
    if (
        200 <= response.status_code < 300
        and payload
        and isinstance(payload.get("data"), list)
    ):
        return ProviderTestResponse(
            ok=True, message=f"{provider_label} credentials are valid."
        )

    if 200 <= response.status_code < 300:
        return ProviderTestResponse(
            ok=False,
            message=f"{provider_label} validation returned unexpected payload.",
        )

    detail = _extract_error_message(response)
    return ProviderTestResponse(
        ok=False,
        message=f"{provider_label} validation failed ({response.status_code}): {detail}",
    )


async def _check_openrouter(
    api_key: str,
    base_url: str,
    model: Optional[str] = None,
) -> ProviderTestResponse:
    headers = {"Authorization": f"Bearer {api_key}"}

    auth_endpoints = [f"{base_url}/auth/key", f"{base_url}/key"]
    auth_ok = False

    async with httpx.AsyncClient(timeout=15.0) as client:
        for endpoint in auth_endpoints:
            response = await client.get(endpoint, headers=headers)
            if response.status_code in (404, 405):
                continue
            payload = _safe_json(response)
            if 200 <= response.status_code < 300 and payload and "error" not in payload:
                auth_ok = True
                break

            detail = _extract_error_message(response)
            return ProviderTestResponse(
                ok=False,
                message=f"OpenRouter key validation failed ({response.status_code}): {detail}",
            )

    if not auth_ok:
        return ProviderTestResponse(
            ok=False,
            message=(
                "Could not validate OpenRouter key with authentication endpoint. "
                "Check Base URL (expected OpenRouter API URL) and try again."
            ),
        )

    if model:
        endpoint = f"{base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 8,
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(endpoint, headers=headers, json=payload)

        payload_json = _safe_json(response)
        if (
            200 <= response.status_code < 300
            and payload_json
            and "error" not in payload_json
        ):
            return ProviderTestResponse(
                ok=True,
                message=(f"OpenRouter credentials are valid for model '{model}'."),
            )

        detail = _extract_error_message(response)
        return ProviderTestResponse(
            ok=False,
            message=(
                f"OpenRouter key is valid, but model validation failed ({response.status_code}): {detail}"
            ),
        )

    return ProviderTestResponse(ok=True, message="OpenRouter credentials are valid.")


async def _check_anthropic(api_key: str, base_url: str) -> ProviderTestResponse:
    endpoint = f"{base_url}/v1/models"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(endpoint, headers=headers)

    payload = _safe_json(response)
    if (
        200 <= response.status_code < 300
        and payload
        and isinstance(payload.get("data"), list)
    ):
        return ProviderTestResponse(ok=True, message="Anthropic credentials are valid.")

    if 200 <= response.status_code < 300:
        return ProviderTestResponse(
            ok=False,
            message="Anthropic validation returned unexpected payload.",
        )

    detail = _extract_error_message(response)
    return ProviderTestResponse(
        ok=False,
        message=f"Anthropic validation failed ({response.status_code}): {detail}",
    )


async def _check_google(api_key: str, base_url: str) -> ProviderTestResponse:
    endpoint = f"{base_url}/v1beta/models"

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(endpoint, params={"key": api_key})

    payload = _safe_json(response)
    if (
        200 <= response.status_code < 300
        and payload
        and isinstance(payload.get("models"), list)
    ):
        return ProviderTestResponse(ok=True, message="Google credentials are valid.")

    if 200 <= response.status_code < 300:
        return ProviderTestResponse(
            ok=False,
            message="Google validation returned unexpected payload.",
        )

    detail = _extract_error_message(response)
    return ProviderTestResponse(
        ok=False,
        message=f"Google validation failed ({response.status_code}): {detail}",
    )


async def _check_local(base_url: str) -> ProviderTestResponse:
    candidates = [f"{base_url}/models"]
    if base_url.endswith("/v1"):
        candidates.append(f"{base_url[:-3]}/api/tags")
    else:
        candidates.append(f"{base_url}/api/tags")

    async with httpx.AsyncClient(timeout=10.0) as client:
        for endpoint in candidates:
            try:
                response = await client.get(endpoint)
            except httpx.HTTPError:
                continue
            if not (200 <= response.status_code < 300):
                continue

            payload = _safe_json(response)
            if not payload:
                continue

            if endpoint.endswith("/models") and isinstance(payload.get("data"), list):
                return ProviderTestResponse(
                    ok=True, message="Local provider is reachable."
                )

            if endpoint.endswith("/api/tags") and isinstance(
                payload.get("models"), list
            ):
                return ProviderTestResponse(
                    ok=True, message="Local provider is reachable."
                )

    return ProviderTestResponse(
        ok=False,
        message="Could not reach local provider. Check if runtime is running and Base URL is correct.",
    )


async def test_provider_configuration(
    payload: ProviderTestRequest,
    resolved_api_key: Optional[str] = None,
) -> ProviderTestResponse:
    provider = _normalize_provider(payload.provider)
    effective_api_key, _source = resolve_effective_api_key(
        provider=provider,
        api_key=payload.api_key,
        credential_api_key=resolved_api_key,
    )

    try:
        if provider == "openai":
            if not effective_api_key:
                return ProviderTestResponse(
                    ok=False, message=build_missing_api_key_message(provider)
                )
            return await _check_openai_like(
                provider_label="OpenAI",
                api_key=effective_api_key,
                base_url=_normalize_base_url(
                    payload.base_url, "https://api.openai.com/v1"
                ),
            )

        if provider == "openrouter":
            if not effective_api_key:
                return ProviderTestResponse(
                    ok=False, message=build_missing_api_key_message(provider)
                )
            return await _check_openrouter(
                api_key=effective_api_key,
                base_url=_normalize_base_url(
                    payload.base_url, "https://openrouter.ai/api/v1"
                ),
                model=payload.model,
            )

        if provider == "anthropic":
            if not effective_api_key:
                return ProviderTestResponse(
                    ok=False, message=build_missing_api_key_message(provider)
                )
            return await _check_anthropic(
                api_key=effective_api_key,
                base_url=_normalize_base_url(
                    payload.base_url, "https://api.anthropic.com"
                ),
            )

        if provider == "google":
            if not effective_api_key:
                return ProviderTestResponse(
                    ok=False, message=build_missing_api_key_message(provider)
                )
            return await _check_google(
                api_key=effective_api_key,
                base_url=_normalize_base_url(
                    payload.base_url,
                    "https://generativelanguage.googleapis.com",
                ),
            )

        if provider == "local":
            return await _check_local(
                _normalize_base_url(payload.base_url, "http://localhost:11434/v1")
            )

        return ProviderTestResponse(
            ok=False, message=f"Unsupported provider: {provider}"
        )

    except httpx.TimeoutException:
        return ProviderTestResponse(
            ok=False, message="Validation timed out. Please try again."
        )
    except httpx.HTTPError:
        return ProviderTestResponse(
            ok=False,
            message="Could not connect to provider endpoint. Check network and Base URL.",
        )
    except Exception:
        return ProviderTestResponse(
            ok=False,
            message="Unexpected error while validating provider configuration.",
        )
