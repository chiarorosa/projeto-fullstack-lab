from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.compiler import compile_graph, execute_team_tasks
from core.credentials import hydrate_compiled_agent_secrets
from core import database as core_database
from core.redaction import redact_payload, redact_text
from models.team import Team, TeamRun, WebhookTrigger

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


def _canonical_task_inputs_from_payload(body: object, request: Request) -> list[str]:
    if isinstance(body, dict):
        task_input = str(
            body.get("task") or body.get("task_input") or body.get("input") or ""
        ).strip()
        task_inputs = body.get("task_inputs")

        values: list[str] = []
        if task_input:
            values.append(task_input)

        if isinstance(task_inputs, list):
            for item in task_inputs:
                normalized = str(item).strip()
                if normalized:
                    values.append(normalized)

        if values:
            return values

    query_task = (request.query_params.get("task") or "").strip()
    query_input = (request.query_params.get("input") or "").strip()
    if query_task:
        return [query_task]
    if query_input:
        return [query_input]

    raise HTTPException(
        status_code=400,
        detail="Webhook payload must include task/task_input or task_inputs (or task/input query parameter).",
    )


def _event_snapshot() -> dict:
    return {
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
    }


async def _run_webhook_execution(
    *,
    team_id: int,
    webhook_id: str,
    execution_id: str,
    correlation_id: str,
    test_origin: str | None,
    trigger_timestamp: datetime,
    compiled: dict,
    task_inputs: list[str],
) -> None:
    async with core_database.AsyncSessionLocal() as db:
        snapshots: dict[int, dict] = {}

        try:
            async for chunk in execute_team_tasks(
                compiled,
                task_inputs,
                execution_context={
                    "source": "webhook",
                    "trigger_id": webhook_id,
                    "timestamp": trigger_timestamp.isoformat(),
                    "correlation_id": correlation_id,
                    "test_origin": test_origin,
                },
            ):
                if not chunk.startswith("data: "):
                    continue

                payload_text = chunk[len("data: ") :].strip()
                try:
                    event = json.loads(payload_text)
                except Exception:
                    event = None

                if not isinstance(event, dict):
                    continue

                task_index = event.get("task_index")
                if not isinstance(task_index, int):
                    continue

                snapshot = snapshots.setdefault(task_index, _event_snapshot())
                event_type = event.get("type")

                if event_type == "task_start":
                    snapshot["task_input"] = redact_text(
                        str(event.get("task_input") or "")
                    )
                    if event.get("routing") is not None:
                        snapshot["routing_json"] = redact_payload(event.get("routing"))
                elif event_type == "routing_decision":
                    snapshot["selected_agent_id"] = event.get("selected_agent_id")
                    snapshot["selected_agent"] = event.get("selected_agent")
                    snapshot["routing_reason"] = redact_text(
                        str(event.get("reason") or "")
                    )
                    selected_llm = event.get("selected_llm") or {}
                    if isinstance(selected_llm, dict):
                        snapshot["selected_provider"] = selected_llm.get("provider")
                        snapshot["selected_model"] = selected_llm.get("model")
                    snapshot["decision_json"] = redact_payload(
                        {
                            "scores": event.get("scores"),
                            "fallback_used": bool(event.get("fallback_used", False)),
                        }
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
        finally:
            for idx in sorted(snapshots.keys()):
                snapshot = snapshots[idx]
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
                        source="webhook",
                        trigger_id=webhook_id,
                        trigger_timestamp=trigger_timestamp,
                        correlation_id=correlation_id,
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


@router.post("/{webhook_id}", status_code=status.HTTP_202_ACCEPTED)
async def trigger_webhook(
    webhook_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(core_database.get_db),
):
    trigger_result = await db.execute(
        select(WebhookTrigger).where(WebhookTrigger.webhook_id == webhook_id)
    )
    trigger = trigger_result.scalar_one_or_none()
    if not trigger:
        raise HTTPException(
            status_code=404,
            detail="Webhook trigger not found. Save or update the team graph after configuring the Webhook Node trigger id.",
        )

    team_result = await db.execute(select(Team).where(Team.id == trigger.team_id))
    team = team_result.scalar_one_or_none()
    if not team:
        raise HTTPException(
            status_code=404, detail="Team associated with webhook not found"
        )

    content_type = request.headers.get("content-type", "")
    if content_type and "application/json" not in content_type.lower():
        raise HTTPException(
            status_code=400,
            detail="Webhook payload must use Content-Type: application/json",
        )

    try:
        body = await request.json()
    except Exception:
        body = {}

    task_inputs = _canonical_task_inputs_from_payload(body, request)
    if not task_inputs:
        raise HTTPException(
            status_code=400, detail="No valid tasks found in webhook payload"
        )

    graph = json.loads(team.graph_json)
    node_exists = any(
        n.get("id") == trigger.node_id and n.get("type") == "webhookNode"
        for n in graph.get("nodes", [])
    )
    if not node_exists:
        raise HTTPException(
            status_code=400,
            detail="Webhook trigger is stale: mapped webhook node no longer exists",
        )

    compiled = compile_graph(graph)
    await hydrate_compiled_agent_secrets(db, compiled)
    if not compiled.get("agents"):
        raise HTTPException(
            status_code=400, detail="No agents found in this team graph."
        )

    execution_id = uuid4().hex
    correlation_id = (
        request.headers.get("x-correlation-id")
        or request.headers.get("x-request-id")
        or uuid4().hex
    )
    test_origin = (request.headers.get("x-test-origin") or "").strip() or None
    trigger_timestamp = datetime.now(timezone.utc)

    background_tasks.add_task(
        _run_webhook_execution,
        team_id=team.id,
        webhook_id=webhook_id,
        execution_id=execution_id,
        correlation_id=correlation_id,
        test_origin=test_origin,
        trigger_timestamp=trigger_timestamp,
        compiled=compiled,
        task_inputs=task_inputs,
    )

    return {
        "ok": True,
        "execution_id": execution_id,
        "correlation_id": correlation_id,
        "trigger_id": webhook_id,
        "accepted_at": trigger_timestamp.isoformat(),
        "test_origin": test_origin,
        "message": "Webhook execution accepted",
    }
