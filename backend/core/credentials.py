from __future__ import annotations

import json
from copy import deepcopy
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.secrets import decrypt_secret, encrypt_secret
from models.team import Credential, Team


_KEYED_PROVIDERS = {"openai", "openrouter", "anthropic", "google", "opencode"}


def _normalize_provider(provider: str) -> str:
    if provider == "opencode":
        return "openrouter"
    return provider


def provider_requires_secret(provider: str) -> bool:
    return _normalize_provider(provider) in _KEYED_PROVIDERS


async def create_credential(
    db: AsyncSession,
    *,
    provider: str,
    secret: str,
) -> str:
    credential_id = f"cred_{uuid4().hex}"
    credential = Credential(
        id=credential_id,
        provider=_normalize_provider(provider),
        secret_encrypted=encrypt_secret(secret),
    )
    db.add(credential)
    await db.flush()
    return credential_id


async def resolve_credential_secret(
    db: AsyncSession, credential_ref: str
) -> str | None:
    result = await db.execute(select(Credential).where(Credential.id == credential_ref))
    credential = result.scalar_one_or_none()
    if not credential:
        return None
    return decrypt_secret(credential.secret_encrypted)


def _extract_llm_node_data(graph_json: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = graph_json.get("nodes")
    if not isinstance(nodes, list):
        return []
    llm_nodes: list[dict[str, Any]] = []
    for node in nodes:
        if not isinstance(node, dict) or node.get("type") != "llmNode":
            continue
        data = node.get("data")
        if isinstance(data, dict):
            llm_nodes.append(data)
    return llm_nodes


async def transform_graph_secrets_for_storage(
    db: AsyncSession,
    graph_json: dict[str, Any],
) -> tuple[dict[str, Any], bool]:
    transformed = deepcopy(graph_json)
    changed = False

    for llm_data in _extract_llm_node_data(transformed):
        provider = str(llm_data.get("provider") or "openai")
        raw_api_key = str(llm_data.get("apiKey") or "").strip()

        if raw_api_key and provider_requires_secret(provider):
            llm_data["credentialRef"] = await create_credential(
                db,
                provider=provider,
                secret=raw_api_key,
            )
            changed = True

        if "apiKey" in llm_data:
            llm_data.pop("apiKey", None)
            changed = True

    return transformed, changed


async def migrate_legacy_team_graph_secrets(db: AsyncSession) -> int:
    result = await db.execute(select(Team).order_by(Team.id.asc()))
    teams = result.scalars().all()
    migrated_count = 0

    for team in teams:
        try:
            graph = json.loads(team.graph_json)
        except Exception:
            continue

        transformed, changed = await transform_graph_secrets_for_storage(db, graph)
        if not changed:
            continue

        team.graph_json = json.dumps(transformed)
        migrated_count += 1

    if migrated_count:
        await db.commit()

    return migrated_count


async def hydrate_compiled_agent_secrets(
    db: AsyncSession,
    compiled: dict[str, Any],
) -> None:
    for agent in compiled.get("agents", []):
        llm = agent.get("llm")
        if not isinstance(llm, dict):
            continue

        current_api_key = str(llm.get("api_key") or "").strip()
        if current_api_key:
            continue

        credential_ref = str(llm.get("credential_ref") or "").strip()
        if not credential_ref:
            continue

        secret = await resolve_credential_secret(db, credential_ref)
        if secret:
            llm["api_key"] = secret
