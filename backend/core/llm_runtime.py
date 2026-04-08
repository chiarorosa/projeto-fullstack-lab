from __future__ import annotations

from typing import Any, Optional

import httpx


def _normalize_provider(provider: str) -> str:
    if provider in {"opencode"}:
        return "openrouter"
    if provider in {"ollama", "lmstudio"}:
        return "local"
    return provider


def _normalize_base_url(provider: str, base_url: Optional[str]) -> str:
    if base_url and base_url.strip():
        return base_url.strip().rstrip("/")

    defaults = {
        "openai": "https://api.openai.com/v1",
        "openrouter": "https://openrouter.ai/api/v1",
        "local": "http://localhost:11434/v1",
        "anthropic": "https://api.anthropic.com",
        "google": "https://generativelanguage.googleapis.com",
    }
    return defaults.get(provider, "https://api.openai.com/v1")


def _extract_openai_like_content(payload: dict[str, Any]) -> str:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""

    message = choices[0].get("message")
    if not isinstance(message, dict):
        return ""

    content = message.get("content")
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        return "\n".join(parts)

    return ""


def _extract_anthropic_content(payload: dict[str, Any]) -> str:
    content = payload.get("content")
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for item in content:
        if isinstance(item, dict) and item.get("type") == "text":
            text = item.get("text")
            if isinstance(text, str):
                parts.append(text)
    return "\n".join(parts)


def _extract_google_content(payload: dict[str, Any]) -> str:
    candidates = payload.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        return ""

    content = candidates[0].get("content")
    if not isinstance(content, dict):
        return ""

    parts = content.get("parts")
    if not isinstance(parts, list):
        return ""

    text_parts: list[str] = []
    for part in parts:
        if isinstance(part, dict) and isinstance(part.get("text"), str):
            text_parts.append(part["text"])
    return "\n".join(text_parts)


def _clean_error_text(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except Exception:
        payload = None

    message = None
    if isinstance(payload, dict):
        error = payload.get("error")
        if isinstance(error, dict):
            message = error.get("message")
        elif isinstance(error, str):
            message = error
        if not message and isinstance(payload.get("message"), str):
            message = payload.get("message")
        if not message and isinstance(payload.get("detail"), str):
            message = payload.get("detail")

    if not message:
        message = response.text or "Unknown provider error"

    compact = " ".join(str(message).split())
    return compact[:260]


async def generate_llm_response(
    llm_config: dict[str, Any],
    system_prompt: str,
    user_prompt: str,
) -> str:
    provider = _normalize_provider(str(llm_config.get("provider") or "openai"))
    model = str(llm_config.get("model") or "gpt-4o-mini")
    api_key = str(llm_config.get("api_key") or "").strip()
    base_url = _normalize_base_url(provider, llm_config.get("base_url"))

    if provider in {"openai", "openrouter", "anthropic", "google"} and not api_key:
        raise RuntimeError(f"{provider} API key is required for execution")

    timeout = httpx.Timeout(40.0)

    if provider in {"openai", "openrouter", "local"}:
        endpoint = f"{base_url}/chat/completions"
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        payload = {
            "model": model,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(endpoint, headers=headers, json=payload)

        if response.status_code < 200 or response.status_code >= 300:
            detail = _clean_error_text(response)
            if provider == "openrouter" and response.status_code in {401, 403}:
                auth_endpoint = f"{base_url}/auth/key"
                auth_headers = {"Authorization": f"Bearer {api_key}"}
                try:
                    async with httpx.AsyncClient(timeout=timeout) as auth_client:
                        auth_response = await auth_client.get(
                            auth_endpoint, headers=auth_headers
                        )
                    if 200 <= auth_response.status_code < 300:
                        raise RuntimeError(
                            "openrouter model access failed even though API key is valid. "
                            "Check model availability/permissions for this account and model id. "
                            f"Upstream detail: {detail}"
                        )
                except RuntimeError:
                    raise
                except Exception:
                    pass

            raise RuntimeError(
                f"{provider} completion failed ({response.status_code}): {detail}"
            )

        text = _extract_openai_like_content(response.json())
        if not text:
            raise RuntimeError(f"{provider} returned empty content")
        return text

    if provider == "anthropic":
        endpoint = f"{base_url}/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        }
        payload = {
            "model": model,
            "max_tokens": 1024,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        }

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(endpoint, headers=headers, json=payload)

        if response.status_code < 200 or response.status_code >= 300:
            raise RuntimeError(
                f"anthropic completion failed ({response.status_code}): {_clean_error_text(response)}"
            )

        text = _extract_anthropic_content(response.json())
        if not text:
            raise RuntimeError("anthropic returned empty content")
        return text

    if provider == "google":
        endpoint = f"{base_url}/v1beta/models/{model}:generateContent"
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {"temperature": 0.2},
        }

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                endpoint, params={"key": api_key}, json=payload
            )

        if response.status_code < 200 or response.status_code >= 300:
            raise RuntimeError(
                f"google completion failed ({response.status_code}): {_clean_error_text(response)}"
            )

        text = _extract_google_content(response.json())
        if not text:
            raise RuntimeError("google returned empty content")
        return text

    raise RuntimeError(f"Unsupported provider for execution: {provider}")
