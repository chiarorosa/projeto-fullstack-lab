from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.database import init_db
from core.security import (
    SECURITY_SETTINGS,
    validate_security_settings,
)
from routes.teams import router as teams_router, llm_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_security_settings(SECURITY_SETTINGS)
    await init_db()
    yield


app = FastAPI(
    title="Visual Multi-Agent Team Builder API",
    description="Backend for orchestrating multi-agent AI teams.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=SECURITY_SETTINGS.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(teams_router)
app.include_router(llm_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "multi-agent-builder"}
