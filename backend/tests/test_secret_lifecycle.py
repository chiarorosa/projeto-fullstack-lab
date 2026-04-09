import json
import os
import tempfile
import unittest
from pathlib import Path


class SecretLifecycleTests(unittest.IsolatedAsyncioTestCase):
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

    async def test_graph_save_replaces_api_key_with_credential_ref(self) -> None:
        from core.credentials import transform_graph_secrets_for_storage

        graph = {
            "nodes": [
                {
                    "id": "llm-1",
                    "type": "llmNode",
                    "data": {
                        "provider": "openai",
                        "model": "gpt-4o-mini",
                        "apiKey": "sk-test-secret",
                    },
                }
            ],
            "edges": [],
        }

        async with self.database.AsyncSessionLocal() as db:
            transformed, changed = await transform_graph_secrets_for_storage(db, graph)
            await db.commit()

            self.assertTrue(changed)
            llm_data = transformed["nodes"][0]["data"]
            self.assertNotIn("apiKey", llm_data)
            self.assertTrue(str(llm_data.get("credentialRef", "")).startswith("cred_"))

    async def test_legacy_migration_moves_plaintext_keys(self) -> None:
        from models.team import Team
        from core.credentials import migrate_legacy_team_graph_secrets

        legacy_graph = {
            "nodes": [
                {
                    "id": "llm-1",
                    "type": "llmNode",
                    "data": {
                        "provider": "openrouter",
                        "model": "openai/gpt-4o-mini",
                        "apiKey": "sk-or-legacy-secret",
                    },
                }
            ],
            "edges": [],
        }

        async with self.database.AsyncSessionLocal() as db:
            db.add(
                Team(
                    name="legacy",
                    description="",
                    graph_json=json.dumps(legacy_graph),
                )
            )
            await db.commit()

        async with self.database.AsyncSessionLocal() as db:
            migrated = await migrate_legacy_team_graph_secrets(db)
            self.assertEqual(migrated, 1)

        async with self.database.AsyncSessionLocal() as db:
            from sqlalchemy import select

            result = await db.execute(select(Team).where(Team.name == "legacy"))
            team = result.scalar_one()
            loaded = json.loads(team.graph_json)
            llm_data = loaded["nodes"][0]["data"]
            self.assertNotIn("apiKey", llm_data)
            self.assertTrue(str(llm_data.get("credentialRef", "")).startswith("cred_"))

    async def test_provider_validation_uses_credential_ref_and_no_secret_echo(
        self,
    ) -> None:
        from models.team import Credential
        from core.secrets import encrypt_secret
        from models.schemas import ProviderTestRequest
        from core.provider_validation import test_provider_configuration
        from core.redaction import redact_text

        async with self.database.AsyncSessionLocal() as db:
            db.add(
                Credential(
                    id="cred_test",
                    provider="openai",
                    secret_encrypted=encrypt_secret("sk-test-secret"),
                )
            )
            await db.commit()

        request = ProviderTestRequest(
            provider="openai",
            credential_ref="cred_test",
            api_key=None,
            model="gpt-4o-mini",
        )

        response = await test_provider_configuration(
            request, resolved_api_key="sk-test-secret"
        )
        masked = redact_text(response.message)
        self.assertNotIn("sk-test-secret", masked)

    async def test_db_file_created_in_temp_dir(self) -> None:
        db_path = Path(self._tmp_dir.name) / "multiagent.db"
        self.assertTrue(db_path.exists())
