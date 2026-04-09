import json
import os
import tempfile
import unittest
from unittest.mock import AsyncMock, patch


class ProviderTestFlowTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self._cwd = os.getcwd()
        self._tmp_dir = tempfile.TemporaryDirectory()
        os.chdir(self._tmp_dir.name)

        os.environ["APP_ENV"] = "test"
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
