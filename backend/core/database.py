from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect, text
from models.team import Base
from core.credentials import migrate_legacy_team_graph_secrets

DATABASE_URL = "sqlite+aiosqlite:///./multiagent.db"

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def _migrate_team_runs(sync_conn):
    inspector = inspect(sync_conn)
    if "team_runs" not in inspector.get_table_names():
        return

    existing_columns = {col["name"] for col in inspector.get_columns("team_runs")}
    needed_columns = {
        "selected_agent_id": "VARCHAR(255)",
        "selected_agent": "VARCHAR(255)",
        "selected_provider": "VARCHAR(64)",
        "selected_model": "VARCHAR(255)",
        "routing_reason": "TEXT",
        "decision_json": "TEXT",
    }

    for name, sql_type in needed_columns.items():
        if name in existing_columns:
            continue
        sync_conn.execute(text(f"ALTER TABLE team_runs ADD COLUMN {name} {sql_type}"))


def _migrate_credentials(sync_conn):
    inspector = inspect(sync_conn)
    if "credentials" not in inspector.get_table_names():
        return

    existing_columns = {col["name"] for col in inspector.get_columns("credentials")}
    if "provider" not in existing_columns:
        sync_conn.execute(
            text(
                "ALTER TABLE credentials ADD COLUMN provider VARCHAR(64) DEFAULT 'openai'"
            )
        )


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_migrate_team_runs)
        await conn.run_sync(_migrate_credentials)

    async with AsyncSessionLocal() as session:
        await migrate_legacy_team_graph_secrets(session)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
