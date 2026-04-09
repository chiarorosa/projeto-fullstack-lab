import json
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.team import Team, TeamRun
from models.schemas import (
    ExecuteRequest,
    ProviderTestRequest,
    ProviderTestResponse,
    TeamRunResponse,
    TeamCreate,
    TeamResponse,
    TeamUpdate,
)
from core.database import get_db
from core.compiler import compile_graph, execute_team_tasks
from core.provider_validation import test_provider_configuration
from core.credentials import (
    hydrate_compiled_agent_secrets,
    resolve_credential_secret,
    transform_graph_secrets_for_storage,
)
from core.redaction import redact_payload, redact_text
from core.security import (
    rate_limit_execute,
    rate_limit_provider_test,
    require_bearer_token,
)

router = APIRouter(prefix="/api/teams", tags=["teams"])
llm_router = APIRouter(prefix="/api/llm", tags=["llm"])


def _serialize_team_run(run: TeamRun) -> TeamRunResponse:
    routing_payload = None
    decision_payload = None
    if run.routing_json:
        try:
            routing_payload = json.loads(run.routing_json)
        except Exception:
            routing_payload = None
    if run.decision_json:
        try:
            decision_payload = json.loads(run.decision_json)
        except Exception:
            decision_payload = None

    return TeamRunResponse(
        id=run.id,
        team_id=run.team_id,
        execution_id=run.execution_id,
        task_index=run.task_index,
        task_input=redact_text(run.task_input),
        final_output=redact_text(run.final_output)
        if run.final_output
        else run.final_output,
        status=run.status,
        error_message=redact_text(run.error_message)
        if run.error_message
        else run.error_message,
        selected_agent_id=run.selected_agent_id,
        selected_agent=run.selected_agent,
        selected_provider=run.selected_provider,
        selected_model=run.selected_model,
        routing_reason=redact_text(run.routing_reason) if run.routing_reason else None,
        decision_json=redact_payload(decision_payload),
        routing_json=redact_payload(routing_payload),
        created_at=run.created_at.isoformat(),
    )


def _sanitize_graph_for_response(graph: dict) -> dict:
    sanitized = redact_payload(graph)
    nodes = sanitized.get("nodes") if isinstance(sanitized, dict) else None
    if isinstance(nodes, list):
        for node in nodes:
            if not isinstance(node, dict):
                continue
            data = node.get("data")
            if not isinstance(data, dict):
                continue
            data.pop("apiKey", None)
    return sanitized if isinstance(sanitized, dict) else graph


def _friendly_execution_error(error_message: str) -> str:
    text = error_message.strip()
    lower = text.lower()

    if "401" in lower and "openrouter" in lower:
        return (
            "OpenRouter authentication failed (401). "
            "Check the API Key configured in the connected LLM node and click 'Test Provider' in LLM Properties."
        )

    if "api key" in lower and "required" in lower:
        return (
            "Missing provider API key for the selected agent LLM. "
            "Set API Key in LLM Properties or configure the expected environment variable."
        )

    if "network error" in lower or "connect" in lower:
        return (
            "Could not connect to provider endpoint. "
            "Verify internet/network access and Base URL in LLM Properties."
        )

    return text


@router.get("/", response_model=list[TeamResponse])
async def list_teams(
    _auth: None = Depends(require_bearer_token),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Team).order_by(Team.updated_at.desc()))
    teams = result.scalars().all()
    return [
        TeamResponse(
            id=t.id,
            name=t.name,
            description=t.description,
            graph_json=_sanitize_graph_for_response(json.loads(t.graph_json)),
            created_at=t.created_at.isoformat(),
            updated_at=t.updated_at.isoformat(),
        )
        for t in teams
    ]


@router.post("/", response_model=TeamResponse, status_code=201)
async def create_team(
    payload: TeamCreate,
    _auth: None = Depends(require_bearer_token),
    db: AsyncSession = Depends(get_db),
):
    transformed_graph, _changed = await transform_graph_secrets_for_storage(
        db,
        payload.graph_json,
    )

    team = Team(
        name=payload.name,
        description=payload.description,
        graph_json=json.dumps(transformed_graph),
    )
    db.add(team)
    await db.commit()
    await db.refresh(team)
    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        graph_json=_sanitize_graph_for_response(json.loads(team.graph_json)),
        created_at=team.created_at.isoformat(),
        updated_at=team.updated_at.isoformat(),
    )


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int,
    _auth: None = Depends(require_bearer_token),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        graph_json=_sanitize_graph_for_response(json.loads(team.graph_json)),
        created_at=team.created_at.isoformat(),
        updated_at=team.updated_at.isoformat(),
    )


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    payload: TeamUpdate,
    _auth: None = Depends(require_bearer_token),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if payload.name is not None:
        team.name = payload.name
    if payload.description is not None:
        team.description = payload.description
    if payload.graph_json is not None:
        transformed_graph, _changed = await transform_graph_secrets_for_storage(
            db,
            payload.graph_json,
        )
        team.graph_json = json.dumps(transformed_graph)
    await db.commit()
    await db.refresh(team)
    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        graph_json=_sanitize_graph_for_response(json.loads(team.graph_json)),
        created_at=team.created_at.isoformat(),
        updated_at=team.updated_at.isoformat(),
    )


@router.delete("/{team_id}", status_code=204)
async def delete_team(
    team_id: int,
    _auth: None = Depends(require_bearer_token),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    await db.delete(team)
    await db.commit()


@router.get("/{team_id}/runs", response_model=list[TeamRunResponse])
async def list_team_runs(
    team_id: int,
    limit: int = 50,
    _auth: None = Depends(require_bearer_token),
    db: AsyncSession = Depends(get_db),
):
    team_result = await db.execute(select(Team).where(Team.id == team_id))
    team = team_result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    safe_limit = max(1, min(limit, 200))
    result = await db.execute(
        select(TeamRun)
        .where(TeamRun.team_id == team_id)
        .order_by(TeamRun.created_at.desc(), TeamRun.task_index.asc())
        .limit(safe_limit)
    )
    runs = result.scalars().all()
    return [_serialize_team_run(run) for run in runs]


@router.get("/{team_id}/runs/by-execution")
async def list_runs_grouped_by_execution(
    team_id: int,
    limit: int = 20,
    _auth: None = Depends(require_bearer_token),
    db: AsyncSession = Depends(get_db),
):
    team_result = await db.execute(select(Team).where(Team.id == team_id))
    team = team_result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    safe_limit = max(1, min(limit, 100))
    result = await db.execute(
        select(TeamRun)
        .where(TeamRun.team_id == team_id)
        .order_by(TeamRun.created_at.desc(), TeamRun.task_index.asc())
    )
    all_runs = result.scalars().all()

    grouped: dict[str, list[TeamRun]] = {}
    order: list[str] = []
    for run in all_runs:
        if run.execution_id not in grouped:
            grouped[run.execution_id] = []
            order.append(run.execution_id)
        grouped[run.execution_id].append(run)

    execution_items = []
    for execution_id in order[:safe_limit]:
        runs_for_execution = sorted(
            grouped[execution_id], key=lambda item: item.task_index
        )
        first_created = runs_for_execution[0].created_at.isoformat()
        execution_items.append(
            {
                "execution_id": execution_id,
                "created_at": first_created,
                "tasks": [
                    _serialize_team_run(run).model_dump() for run in runs_for_execution
                ],
            }
        )

    return {"executions": execution_items}


@router.post("/{team_id}/execute")
async def execute_team_route(
    team_id: int,
    payload: ExecuteRequest,
    _auth: None = Depends(require_bearer_token),
    _rate_limit: None = Depends(rate_limit_execute),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    graph = json.loads(team.graph_json)
    compiled = compile_graph(graph)
    await hydrate_compiled_agent_secrets(db, compiled)

    if not compiled["agents"]:
        raise HTTPException(
            status_code=400, detail="No agents found in this team graph."
        )

    graph_nodes = graph.get("nodes", [])
    task_nodes = [n for n in graph_nodes if n.get("type") == "taskNode"]
    task_inputs = payload.normalized_task_inputs()

    agent_llm_connections = [
        {
            "agent_id": agent.get("id"),
            "agent": agent.get("role"),
            "llm_connected": bool(agent.get("llm")),
            "llm_provider": (agent.get("llm") or {}).get("provider"),
            "llm_model": (agent.get("llm") or {}).get("model"),
            "eligible": bool(agent.get("eligible")),
            "reason": agent.get("skip_reason"),
        }
        for agent in compiled.get("agents", [])
    ]

    if task_nodes:
        task_node_data = task_nodes[0].get("data", {})
        node_task_input = (task_node_data.get("taskInput") or "").strip()
        node_task_inputs = [
            str(item).strip()
            for item in (task_node_data.get("taskInputs") or [])
            if str(item).strip()
        ]
        task_inputs = [item for item in [node_task_input, *node_task_inputs] if item]
    elif payload.task_inputs:
        pass
    elif payload.task_input:
        pass
    else:
        raise HTTPException(
            status_code=400,
            detail="Task Node is required as bootstrap input source, or provide task_input/task_inputs for compatibility.",
        )

    if not task_inputs:
        raise HTTPException(
            status_code=400,
            detail="No valid tasks provided. Fill Task Node input or request task_input/task_inputs.",
        )

    execution_id = uuid4().hex
    task_snapshots: dict[int, dict] = {}

    async def event_stream():
        compiled_summary_event = {
            "type": "graph_connectivity",
            "agents": agent_llm_connections,
        }
        yield f"data: {json.dumps(redact_payload(compiled_summary_event))}\n\n"

        try:
            async for chunk in execute_team_tasks(compiled, task_inputs):
                if chunk.startswith("data: "):
                    payload_text = chunk[len("data: ") :].strip()
                    try:
                        event = json.loads(payload_text)
                    except Exception:
                        event = None

                    if isinstance(event, dict):
                        event_type = event.get("type")
                        task_index = event.get("task_index")
                        if isinstance(task_index, int):
                            snapshot = task_snapshots.setdefault(
                                task_index,
                                {
                                    "task_input": "",
                                    "final_output": None,
                                    "status": "completed",
                                    "error_message": None,
                                    "routing_json": None,
                                    "selected_agent_id": None,
                                    "selected_agent": None,
                                    "selected_provider": None,
                                    "selected_model": None,
                                    "routing_reason": None,
                                    "decision_json": None,
                                },
                            )

                            if event_type == "task_start":
                                snapshot["task_input"] = redact_text(
                                    str(event.get("task_input") or "")
                                )
                                if event.get("routing") is not None:
                                    snapshot["routing_json"] = redact_payload(
                                        event.get("routing")
                                    )
                            elif event_type == "routing_decision":
                                snapshot["selected_agent_id"] = event.get(
                                    "selected_agent_id"
                                )
                                snapshot["selected_agent"] = event.get("selected_agent")
                                snapshot["routing_reason"] = redact_text(
                                    str(event.get("reason") or "")
                                )
                                selected_llm = event.get("selected_llm") or {}
                                if isinstance(selected_llm, dict):
                                    snapshot["selected_provider"] = selected_llm.get(
                                        "provider"
                                    )
                                    snapshot["selected_model"] = selected_llm.get(
                                        "model"
                                    )
                                snapshot["decision_json"] = redact_payload(
                                    {"scores": event.get("scores")}
                                )
                            elif event_type == "task_done":
                                snapshot["final_output"] = redact_text(
                                    str(event.get("final_output") or "")
                                )
                                snapshot["status"] = "completed"
                            elif event_type == "task_error":
                                snapshot["status"] = "failed"
                                snapshot["error_message"] = redact_text(
                                    str(event.get("message") or "")
                                )

                if chunk.startswith("data: "):
                    payload_text = chunk[len("data: ") :].strip()
                    try:
                        event_obj = json.loads(payload_text)
                        safe_event = redact_payload(event_obj)
                        yield f"data: {json.dumps(safe_event)}\n\n"
                    except Exception:
                        yield chunk
                else:
                    yield chunk
        except Exception as exc:
            friendly = redact_text(_friendly_execution_error(str(exc)))
            error_event = {
                "type": "error",
                "message": friendly,
            }
            yield f"data: {json.dumps(error_event)}\n\n"
        finally:
            if task_snapshots:
                for idx in sorted(task_snapshots.keys()):
                    snapshot = task_snapshots[idx]
                    db.add(
                        TeamRun(
                            team_id=team_id,
                            execution_id=execution_id,
                            task_index=idx,
                            task_input=snapshot["task_input"]
                            or redact_text(
                                task_inputs[idx] if idx < len(task_inputs) else ""
                            ),
                            final_output=snapshot["final_output"],
                            status=snapshot["status"],
                            error_message=snapshot["error_message"],
                            selected_agent_id=snapshot["selected_agent_id"],
                            selected_agent=snapshot["selected_agent"],
                            selected_provider=snapshot["selected_provider"],
                            selected_model=snapshot["selected_model"],
                            routing_reason=snapshot["routing_reason"],
                            decision_json=(
                                json.dumps(snapshot["decision_json"])
                                if snapshot["decision_json"] is not None
                                else None
                            ),
                            routing_json=(
                                json.dumps(snapshot["routing_json"])
                                if snapshot["routing_json"] is not None
                                else None
                            ),
                        )
                    )
                await db.commit()

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@llm_router.post("/test-provider", response_model=ProviderTestResponse)
async def test_llm_provider(
    payload: ProviderTestRequest,
    _auth: None = Depends(require_bearer_token),
    _rate_limit: None = Depends(rate_limit_provider_test),
    db: AsyncSession = Depends(get_db),
):
    resolved_secret = None
    if payload.credential_ref and not payload.api_key:
        resolved_secret = await resolve_credential_secret(db, payload.credential_ref)

    response = await test_provider_configuration(
        payload, resolved_api_key=resolved_secret
    )
    response.message = redact_text(response.message)
    return response
