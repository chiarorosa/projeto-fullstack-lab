import json
import asyncio
import os
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient


class ProviderTestFlowTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self._cwd = os.getcwd()
        self._tmp_dir = tempfile.TemporaryDirectory()
        os.chdir(self._tmp_dir.name)

        os.environ["APP_ENV"] = "test"
        os.environ["AUTH_ENABLED"] = "false"
        os.environ["RATE_LIMIT_ENABLED"] = "false"
        os.environ["CREDENTIAL_ENCRYPTION_KEY"] = "test-encryption-key"

        from core import secrets

        secrets.SECRET_SETTINGS = secrets.load_secret_settings()

        from core import database

        database.DATABASE_URL = "sqlite+aiosqlite:///./multiagent.db"
        database.engine = database.create_async_engine(
            database.DATABASE_URL, echo=False, future=True
        )
        database.AsyncSessionLocal = database.sessionmaker(
            database.engine,
            class_=database.AsyncSession,
            expire_on_commit=False,
        )

        self.database = database
        await self.database.init_db()

    async def asyncTearDown(self) -> None:
        await self.database.engine.dispose()
        os.chdir(self._cwd)
        self._tmp_dir.cleanup()

    def _set_provider_env(self) -> None:
        os.environ["OPENAI_API_KEY"] = "env-openai"
        os.environ["OPENROUTER_API_KEY"] = "env-openrouter"
        os.environ["ANTHROPIC_API_KEY"] = "env-anthropic"
        os.environ["GOOGLE_API_KEY"] = "env-google"

    async def _create_team(self, graph_json: dict) -> int:
        from models.team import Team

        async with self.database.AsyncSessionLocal() as db:
            team = Team(
                name="team-under-test",
                description="",
                graph_json=json.dumps(graph_json),
            )
            db.add(team)
            await db.commit()
            await db.refresh(team)
            return team.id

    async def test_env_fallback_resolution_for_keyed_providers(self) -> None:
        from core.provider_validation import resolve_effective_api_key

        self._set_provider_env()

        expected = {
            "openai": "env-openai",
            "openrouter": "env-openrouter",
            "opencode": "env-openrouter",
            "anthropic": "env-anthropic",
            "google": "env-google",
        }

        for provider, expected_key in expected.items():
            key, source = resolve_effective_api_key(
                provider=provider,
                api_key=None,
                credential_api_key=None,
            )
            self.assertEqual(key, expected_key)
            self.assertEqual(source, "environment")

    async def test_key_resolution_precedence(self) -> None:
        from core.provider_validation import resolve_effective_api_key

        os.environ["OPENAI_API_KEY"] = "env-openai"

        explicit_key, explicit_source = resolve_effective_api_key(
            provider="openai",
            api_key="explicit-openai",
            credential_api_key="cred-openai",
        )
        self.assertEqual(explicit_key, "explicit-openai")
        self.assertEqual(explicit_source, "api_key")

        credential_key, credential_source = resolve_effective_api_key(
            provider="openai",
            api_key="",
            credential_api_key="cred-openai",
        )
        self.assertEqual(credential_key, "cred-openai")
        self.assertEqual(credential_source, "credential_ref")

        env_key, env_source = resolve_effective_api_key(
            provider="openai",
            api_key=None,
            credential_api_key=None,
        )
        self.assertEqual(env_key, "env-openai")
        self.assertEqual(env_source, "environment")

    async def test_missing_key_errors_are_actionable(self) -> None:
        from models.schemas import ProviderTestRequest
        from core.provider_validation import test_provider_configuration

        provider_env = {
            "openai": "OPENAI_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "google": "GOOGLE_API_KEY",
        }

        for provider, env_var in provider_env.items():
            os.environ.pop(env_var, None)
            response = await test_provider_configuration(
                ProviderTestRequest(provider=provider),
                resolved_api_key=None,
            )
            self.assertFalse(response.ok)
            self.assertIn(env_var, response.message)
            self.assertIn("credentialRef", response.message)

    async def test_successful_provider_test_persists_new_credential_ref(self) -> None:
        from models.schemas import ProviderTestRequest, ProviderTestResponse
        from routes.teams import test_llm_provider
        from models.team import Team
        from core.credentials import resolve_credential_secret
        from sqlalchemy import select

        team_id = await self._create_team(
            {
                "nodes": [
                    {
                        "id": "llm-1",
                        "type": "llmNode",
                        "data": {
                            "provider": "openai",
                            "model": "gpt-4o-mini",
                            "apiKey": "should-be-removed",
                        },
                    }
                ],
                "edges": [],
            }
        )

        payload = ProviderTestRequest(
            provider="openai",
            api_key="sk-new-secret",
            model="gpt-4o-mini",
            team_id=team_id,
            node_id="llm-1",
        )

        with patch(
            "routes.teams.test_provider_configuration",
            new=AsyncMock(return_value=ProviderTestResponse(ok=True, message="ok")),
        ):
            async with self.database.AsyncSessionLocal() as db:
                response = await test_llm_provider(
                    payload,
                    _auth=None,
                    _rate_limit=None,
                    db=db,
                )

        self.assertTrue(response.ok)
        self.assertTrue(str(response.credential_ref or "").startswith("cred_"))

        async with self.database.AsyncSessionLocal() as db:
            team_result = await db.execute(select(Team).where(Team.id == team_id))
            team = team_result.scalar_one()
            graph = json.loads(team.graph_json)
            node_data = graph["nodes"][0]["data"]
            self.assertEqual(node_data.get("credentialRef"), response.credential_ref)
            self.assertNotIn("apiKey", node_data)

            secret = await resolve_credential_secret(db, str(response.credential_ref))
            self.assertEqual(secret, "sk-new-secret")

    async def test_openrouter_key_valid_but_model_limited_still_persists_credential(
        self,
    ) -> None:
        from models.schemas import ProviderTestRequest, ProviderTestResponse
        from routes.teams import test_llm_provider
        from models.team import Team
        from core.credentials import resolve_credential_secret
        from sqlalchemy import select

        team_id = await self._create_team(
            {
                "nodes": [
                    {
                        "id": "llm-or-1",
                        "type": "llmNode",
                        "data": {
                            "provider": "openrouter",
                            "model": "google/gemma-4-31b-it:free",
                        },
                    }
                ],
                "edges": [],
            }
        )

        payload = ProviderTestRequest(
            provider="openrouter",
            api_key="or-test-key",
            model="google/gemma-4-31b-it:free",
            team_id=team_id,
            node_id="llm-or-1",
        )

        provider_message = (
            "OpenRouter key is valid, but model validation failed (429): "
            "Rate limit exceeded: free-models-per-day."
        )

        with patch(
            "routes.teams.test_provider_configuration",
            new=AsyncMock(
                return_value=ProviderTestResponse(ok=False, message=provider_message)
            ),
        ):
            async with self.database.AsyncSessionLocal() as db:
                response = await test_llm_provider(
                    payload,
                    _auth=None,
                    _rate_limit=None,
                    db=db,
                )

        self.assertFalse(response.ok)
        self.assertTrue(str(response.credential_ref or "").startswith("cred_"))

        async with self.database.AsyncSessionLocal() as db:
            team_result = await db.execute(select(Team).where(Team.id == team_id))
            team = team_result.scalar_one()
            graph = json.loads(team.graph_json)
            node_data = graph["nodes"][0]["data"]
            self.assertEqual(node_data.get("credentialRef"), response.credential_ref)
            self.assertNotIn("apiKey", node_data)

            secret = await resolve_credential_secret(db, str(response.credential_ref))
            self.assertEqual(secret, "or-test-key")

    async def test_successful_provider_test_rotates_existing_node_credential(
        self,
    ) -> None:
        from models.schemas import ProviderTestRequest, ProviderTestResponse
        from routes.teams import test_llm_provider
        from models.team import Team, Credential
        from core.secrets import encrypt_secret
        from core.credentials import resolve_credential_secret
        from sqlalchemy import select

        async with self.database.AsyncSessionLocal() as db:
            db.add(
                Credential(
                    id="cred_existing",
                    provider="openai",
                    secret_encrypted=encrypt_secret("old-secret"),
                )
            )
            db.add(
                Team(
                    name="team-rotation",
                    description="",
                    graph_json=json.dumps(
                        {
                            "nodes": [
                                {
                                    "id": "llm-1",
                                    "type": "llmNode",
                                    "data": {
                                        "provider": "openai",
                                        "model": "gpt-4o-mini",
                                        "credentialRef": "cred_existing",
                                    },
                                }
                            ],
                            "edges": [],
                        }
                    ),
                )
            )
            await db.commit()

            team_result = await db.execute(
                select(Team).where(Team.name == "team-rotation")
            )
            team = team_result.scalar_one()
            team_id = team.id

        payload = ProviderTestRequest(
            provider="openai",
            api_key="rotated-secret",
            model="gpt-4o-mini",
            team_id=team_id,
            node_id="llm-1",
        )

        with patch(
            "routes.teams.test_provider_configuration",
            new=AsyncMock(return_value=ProviderTestResponse(ok=True, message="ok")),
        ):
            async with self.database.AsyncSessionLocal() as db:
                response = await test_llm_provider(
                    payload,
                    _auth=None,
                    _rate_limit=None,
                    db=db,
                )

        self.assertTrue(response.ok)
        self.assertEqual(response.credential_ref, "cred_existing")

        async with self.database.AsyncSessionLocal() as db:
            secret = await resolve_credential_secret(db, "cred_existing")
            self.assertEqual(secret, "rotated-secret")

    async def test_failed_provider_test_does_not_mutate_credential_or_graph(
        self,
    ) -> None:
        from models.schemas import ProviderTestRequest, ProviderTestResponse
        from routes.teams import test_llm_provider
        from models.team import Team, Credential
        from core.secrets import encrypt_secret
        from core.credentials import resolve_credential_secret
        from sqlalchemy import select

        async with self.database.AsyncSessionLocal() as db:
            db.add(
                Credential(
                    id="cred_existing",
                    provider="openai",
                    secret_encrypted=encrypt_secret("unchanged-secret"),
                )
            )
            db.add(
                Team(
                    name="team-no-mutation",
                    description="",
                    graph_json=json.dumps(
                        {
                            "nodes": [
                                {
                                    "id": "llm-1",
                                    "type": "llmNode",
                                    "data": {
                                        "provider": "openai",
                                        "model": "gpt-4o-mini",
                                        "credentialRef": "cred_existing",
                                    },
                                }
                            ],
                            "edges": [],
                        }
                    ),
                )
            )
            await db.commit()

            team_result = await db.execute(
                select(Team).where(Team.name == "team-no-mutation")
            )
            team = team_result.scalar_one()
            team_id = team.id

        payload = ProviderTestRequest(
            provider="openai",
            api_key="new-secret-that-must-not-persist",
            model="gpt-4o-mini",
            team_id=team_id,
            node_id="llm-1",
        )

        with patch(
            "routes.teams.test_provider_configuration",
            new=AsyncMock(
                return_value=ProviderTestResponse(ok=False, message="validation failed")
            ),
        ):
            async with self.database.AsyncSessionLocal() as db:
                response = await test_llm_provider(
                    payload,
                    _auth=None,
                    _rate_limit=None,
                    db=db,
                )

        self.assertFalse(response.ok)
        self.assertIsNone(response.credential_ref)

        async with self.database.AsyncSessionLocal() as db:
            secret = await resolve_credential_secret(db, "cred_existing")
            self.assertEqual(secret, "unchanged-secret")

            team_result = await db.execute(select(Team).where(Team.id == team_id))
            team = team_result.scalar_one()
            graph = json.loads(team.graph_json)
            node_data = graph["nodes"][0]["data"]
            self.assertEqual(node_data.get("credentialRef"), "cred_existing")

    async def test_webhook_trigger_valid_unknown_and_malformed(self) -> None:
        from main import app
        from models.team import Team, TeamRun, WebhookTrigger
        from sqlalchemy import select

        graph = {
            "nodes": [
                {
                    "id": "wh-1",
                    "type": "webhookNode",
                    "data": {
                        "label": "Webhook",
                        "webhookId": "wh_test_123",
                        "method": "POST",
                    },
                },
                {
                    "id": "agent-1",
                    "type": "agentNode",
                    "data": {"role": "Agent", "goal": "Handle task", "backstory": ""},
                },
                {
                    "id": "llm-1",
                    "type": "llmNode",
                    "data": {
                        "provider": "openai",
                        "model": "gpt-4o-mini",
                        "apiKey": "sk-test",
                    },
                },
            ],
            "edges": [
                {"id": "e-1", "source": "wh-1", "target": "agent-1"},
                {"id": "e-2", "source": "llm-1", "target": "agent-1"},
            ],
        }

        async with self.database.AsyncSessionLocal() as db:
            team = Team(
                name="webhook-team", description="", graph_json=json.dumps(graph)
            )
            db.add(team)
            await db.flush()
            db.add(
                WebhookTrigger(
                    webhook_id="wh_test_123",
                    team_id=int(team.id),
                    node_id="wh-1",
                )
            )
            await db.commit()

        async def _fake_execute(_compiled, task_inputs, execution_context=None):
            task_text = task_inputs[0] if task_inputs else ""
            yield f"data: {json.dumps({'type': 'task_start', 'task_index': 0, 'task_input': task_text, 'routing': {'activated_agents': [{'id': 'agent-1', 'agent': 'Agent'}], 'skipped_agents': []}, 'bootstrap': execution_context or {}})}\n\n"
            yield f"data: {json.dumps({'type': 'routing_decision', 'task_index': 0, 'selected_agent_id': 'agent-1', 'selected_agent': 'Agent', 'selected_llm': {'provider': 'openai', 'model': 'gpt-4o-mini'}, 'reason': 'test', 'scores': []})}\n\n"
            yield f"data: {json.dumps({'type': 'task_done', 'task_index': 0, 'final_output': 'ok'})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'final_output': 'done'})}\n\n"

        with (
            patch(
                "routes.webhooks.hydrate_compiled_agent_secrets",
                new=AsyncMock(return_value=None),
            ),
            patch(
                "core.compiler.generate_llm_response", new=AsyncMock(return_value="ok")
            ),
            patch("routes.webhooks.execute_team_tasks", new=_fake_execute),
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(
                transport=transport, base_url="http://testserver"
            ) as client:
                ok_response = await client.post(
                    "/api/webhooks/wh_test_123",
                    json={"task": "from webhook"},
                    headers={
                        "content-type": "application/json",
                        "x-test-origin": "in-app-webhook-console",
                    },
                )
                self.assertEqual(ok_response.status_code, 202)
                payload = ok_response.json()
                self.assertTrue(payload.get("ok"))
                self.assertTrue(payload.get("execution_id"))
                self.assertEqual(payload.get("trigger_id"), "wh_test_123")
                self.assertEqual(payload.get("test_origin"), "in-app-webhook-console")

                await asyncio.sleep(0.05)

                not_found_response = await client.post(
                    "/api/webhooks/wh_missing",
                    json={"task": "nope"},
                    headers={"content-type": "application/json"},
                )
                self.assertEqual(not_found_response.status_code, 404)

                malformed_response = await client.post(
                    "/api/webhooks/wh_test_123",
                    json={"foo": "bar"},
                    headers={"content-type": "application/json"},
                )
                self.assertEqual(malformed_response.status_code, 400)

        async with self.database.AsyncSessionLocal() as db:
            result = await db.execute(
                select(TeamRun).where(TeamRun.source == "webhook")
            )
            runs = result.scalars().all()
            self.assertTrue(len(runs) >= 1)
            self.assertEqual(runs[0].trigger_id, "wh_test_123")
            self.assertTrue(runs[0].correlation_id)
            self.assertIsNotNone(runs[0].trigger_timestamp)

    async def test_bootstrap_compatibility_task_webhook_and_mixed_graphs(self) -> None:
        from core.compiler import compile_graph, execute_team_tasks

        async def collect_selected_agent_ids(graph: dict, source: str) -> list[str]:
            compiled = compile_graph(graph)
            selected_ids: list[str] = []
            async for chunk in execute_team_tasks(
                compiled,
                ["do work"],
                execution_context={
                    "source": source,
                    "trigger_id": "wh_ctx" if source == "webhook" else None,
                    "timestamp": "2026-04-09T00:00:00Z",
                    "correlation_id": "corr-1",
                },
            ):
                if not chunk.startswith("data: "):
                    continue
                payload = json.loads(chunk[len("data: ") :].strip())
                if payload.get("type") == "routing_decision":
                    selected_ids.append(str(payload.get("selected_agent_id") or ""))
            return selected_ids

        task_only_graph = {
            "nodes": [
                {
                    "id": "task-1",
                    "type": "taskNode",
                    "data": {"taskInput": "from task node", "taskInputs": []},
                },
                {
                    "id": "agent-task",
                    "type": "agentNode",
                    "data": {
                        "role": "Task Agent",
                        "goal": "Task work",
                        "backstory": "",
                    },
                },
                {
                    "id": "llm-task",
                    "type": "llmNode",
                    "data": {"provider": "openai", "model": "gpt-4o-mini"},
                },
            ],
            "edges": [
                {"id": "e1", "source": "task-1", "target": "agent-task"},
                {"id": "e2", "source": "llm-task", "target": "agent-task"},
            ],
        }

        webhook_only_graph = {
            "nodes": [
                {
                    "id": "wh-1",
                    "type": "webhookNode",
                    "data": {"webhookId": "wh_abc", "method": "POST"},
                },
                {
                    "id": "agent-wh",
                    "type": "agentNode",
                    "data": {
                        "role": "Webhook Agent",
                        "goal": "Webhook work",
                        "backstory": "",
                    },
                },
                {
                    "id": "llm-wh",
                    "type": "llmNode",
                    "data": {"provider": "openai", "model": "gpt-4o-mini"},
                },
            ],
            "edges": [
                {"id": "e1", "source": "wh-1", "target": "agent-wh"},
                {"id": "e2", "source": "llm-wh", "target": "agent-wh"},
            ],
        }

        mixed_graph = {
            "nodes": [
                {
                    "id": "task-1",
                    "type": "taskNode",
                    "data": {"taskInput": "from task node", "taskInputs": []},
                },
                {
                    "id": "wh-1",
                    "type": "webhookNode",
                    "data": {"webhookId": "wh_mix", "method": "POST"},
                },
                {
                    "id": "agent-task",
                    "type": "agentNode",
                    "data": {
                        "role": "Task Agent",
                        "goal": "Task work",
                        "backstory": "",
                    },
                },
                {
                    "id": "agent-wh",
                    "type": "agentNode",
                    "data": {
                        "role": "Webhook Agent",
                        "goal": "Webhook work",
                        "backstory": "",
                    },
                },
                {
                    "id": "llm-task",
                    "type": "llmNode",
                    "data": {"provider": "openai", "model": "gpt-4o-mini"},
                },
                {
                    "id": "llm-wh",
                    "type": "llmNode",
                    "data": {"provider": "openai", "model": "gpt-4o-mini"},
                },
            ],
            "edges": [
                {"id": "e1", "source": "task-1", "target": "agent-task"},
                {"id": "e2", "source": "wh-1", "target": "agent-wh"},
                {"id": "e3", "source": "llm-task", "target": "agent-task"},
                {"id": "e4", "source": "llm-wh", "target": "agent-wh"},
            ],
        }

        with patch(
            "core.compiler.generate_llm_response", new=AsyncMock(return_value="ok")
        ):
            task_selected = await collect_selected_agent_ids(task_only_graph, "task")
            self.assertEqual(task_selected, ["agent-task"])

            webhook_selected = await collect_selected_agent_ids(
                webhook_only_graph, "webhook"
            )
            self.assertEqual(webhook_selected, ["agent-wh"])

            mixed_task_selected = await collect_selected_agent_ids(mixed_graph, "task")
            mixed_webhook_selected = await collect_selected_agent_ids(
                mixed_graph, "webhook"
            )
            self.assertEqual(mixed_task_selected, ["agent-task"])
            self.assertEqual(mixed_webhook_selected, ["agent-wh"])

    async def test_openrouter_429_message_is_normalized_for_execution(self) -> None:
        from core.compiler import _friendly_provider_error

        raw = (
            "openrouter rate/usage limit reached for selected model (429). "
            "Retry shortly or switch model. Automatic fallback to openrouter/auto also failed. "
            "Upstream detail: Rate limit exceeded: free-models-per-day"
        )
        normalized = _friendly_provider_error(
            raw, "openrouter", "google/gemma-4-31b-it:free"
        )

        self.assertIn(
            "OpenRouter key is valid, but model execution failed (429)", normalized
        )
        self.assertIn("Rate limit exceeded: free-models-per-day", normalized)

    async def test_run_metadata_distinguishes_task_vs_webhook_sources(self) -> None:
        from main import app
        from models.team import Team, TeamRun, WebhookTrigger
        from sqlalchemy import select

        graph = {
            "nodes": [
                {
                    "id": "task-1",
                    "type": "taskNode",
                    "data": {
                        "label": "Task",
                        "taskInput": "from task",
                        "taskInputs": [],
                    },
                },
                {
                    "id": "wh-1",
                    "type": "webhookNode",
                    "data": {
                        "label": "Webhook",
                        "webhookId": "wh_meta_1",
                        "method": "POST",
                    },
                },
                {
                    "id": "agent-task",
                    "type": "agentNode",
                    "data": {
                        "role": "Task Agent",
                        "goal": "Task goal",
                        "backstory": "",
                    },
                },
                {
                    "id": "agent-wh",
                    "type": "agentNode",
                    "data": {
                        "role": "Webhook Agent",
                        "goal": "Webhook goal",
                        "backstory": "",
                    },
                },
                {
                    "id": "llm-task",
                    "type": "llmNode",
                    "data": {
                        "provider": "openai",
                        "model": "gpt-4o-mini",
                        "apiKey": "sk-test",
                    },
                },
                {
                    "id": "llm-wh",
                    "type": "llmNode",
                    "data": {
                        "provider": "openai",
                        "model": "gpt-4o-mini",
                        "apiKey": "sk-test",
                    },
                },
            ],
            "edges": [
                {"id": "e1", "source": "task-1", "target": "agent-task"},
                {"id": "e2", "source": "wh-1", "target": "agent-wh"},
                {"id": "e3", "source": "llm-task", "target": "agent-task"},
                {"id": "e4", "source": "llm-wh", "target": "agent-wh"},
            ],
        }

        async with self.database.AsyncSessionLocal() as db:
            team = Team(
                name="metadata-team", description="", graph_json=json.dumps(graph)
            )
            db.add(team)
            await db.flush()
            db.add(
                WebhookTrigger(
                    webhook_id="wh_meta_1",
                    team_id=int(team.id),
                    node_id="wh-1",
                )
            )
            await db.commit()
            team_id = int(team.id)

        with (
            patch(
                "routes.teams.hydrate_compiled_agent_secrets",
                new=AsyncMock(return_value=None),
            ),
            patch(
                "routes.webhooks.hydrate_compiled_agent_secrets",
                new=AsyncMock(return_value=None),
            ),
            patch(
                "core.compiler.generate_llm_response", new=AsyncMock(return_value="ok")
            ),
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(
                transport=transport, base_url="http://testserver"
            ) as client:
                task_response = await client.post(
                    f"/api/teams/{team_id}/execute", json={}
                )
                self.assertEqual(task_response.status_code, 200)
                _ = task_response.text

                webhook_response = await client.post(
                    "/api/webhooks/wh_meta_1",
                    json={"task": "from webhook"},
                    headers={
                        "content-type": "application/json",
                        "x-correlation-id": "corr-meta",
                    },
                )
                self.assertEqual(webhook_response.status_code, 202)
                await asyncio.sleep(0.08)

        async with self.database.AsyncSessionLocal() as db:
            result = await db.execute(
                select(TeamRun)
                .where(TeamRun.team_id == team_id)
                .order_by(TeamRun.created_at.asc(), TeamRun.id.asc())
            )
            runs = result.scalars().all()

            task_runs = [r for r in runs if (r.source or "task") == "task"]
            webhook_runs = [r for r in runs if r.source == "webhook"]

            self.assertTrue(task_runs)
            self.assertTrue(webhook_runs)

            self.assertIsNone(task_runs[0].trigger_id)
            self.assertIsNone(task_runs[0].trigger_timestamp)
            self.assertEqual(task_runs[0].correlation_id, task_runs[0].execution_id)

            self.assertEqual(webhook_runs[0].trigger_id, "wh_meta_1")
            self.assertEqual(webhook_runs[0].correlation_id, "corr-meta")
            self.assertIsNotNone(webhook_runs[0].trigger_timestamp)
