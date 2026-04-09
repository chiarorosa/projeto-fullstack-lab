"""
Agent Compilation Engine
Converts the visual graph JSON into Agno Team/workflow objects.
"""

import json
import asyncio
from typing import Any, AsyncIterator

from core.llm_runtime import generate_llm_response
from core.task_routing import route_task_to_agent


def _build_agent_system_prompt(agent_cfg: dict[str, Any]) -> str:
    role = str(agent_cfg.get("role") or "Agent")
    goal = str(agent_cfg.get("goal") or "Complete the assigned task")
    backstory = str(agent_cfg.get("backstory") or "")
    return (
        f"You are {role}.\n"
        f"Primary goal: {goal}.\n"
        f"Backstory/context: {backstory}.\n"
        "Answer clearly, focusing only on the assigned task."
    )


def _friendly_provider_error(raw_message: str, provider: str, model: str) -> str:
    text = raw_message.strip()
    lower = text.lower()

    if provider == "openrouter" and ("429" in lower or "rate/usage limit" in lower):
        detail = text
        marker = "upstream detail:"
        marker_idx = lower.find(marker)
        if marker_idx != -1:
            detail = text[marker_idx + len(marker) :].strip() or text
        return (
            "OpenRouter key is valid, but model execution failed (429): "
            f"{detail} "
            "Add credits or switch to another model and retry."
        )

    if (
        provider == "openrouter"
        and "model access failed even though api key is valid" in lower
    ):
        return (
            "OpenRouter key is valid, but this model is not currently accessible for your account. "
            "Check model permissions/availability or choose another model."
        )

    if "401" in lower:
        return (
            f"{provider}/{model} authentication failed (401). "
            "Check API Key in the connected LLM node and validate with 'Test Provider'."
        )

    if "network error" in lower or "connection" in lower:
        return (
            f"{provider}/{model} connection failed. "
            "Check network access and Base URL in LLM Properties."
        )

    if "api key" in lower and "required" in lower:
        return (
            f"{provider}/{model} API key missing. "
            "Configure API Key in the LLM node or server environment variable."
        )

    return text


def _build_execution_user_prompt(task_text: str) -> str:
    return (
        f"Task:\n{task_text}\n\nProduce the best possible final output for this task."
    )


def _build_agent_config(agent_node: dict, llm_nodes: dict) -> dict:
    """Parse a single agent node into agent configuration."""
    data = agent_node.get("data", {})
    agent_id = agent_node["id"]

    # Find connected LLM
    llm_config = None
    missing_llm_connection = False
    connected_llm_id = data.get("connectedLlm")
    if connected_llm_id and connected_llm_id in llm_nodes:
        llm_data = llm_nodes[connected_llm_id].get("data", {})
        provider = llm_data.get("provider", "openai")

        # Map legacy provider values to new unified providers
        # Backward compatibility: ollama/lmstudio -> local
        if provider in ["ollama", "lmstudio"]:
            provider = "local"

        llm_config = {
            "provider": provider,
            "model": llm_data.get("model", "gpt-4o-mini"),
            "api_key": llm_data.get("apiKey", ""),
            "credential_ref": llm_data.get("credentialRef"),
            "base_url": llm_data.get("baseUrl"),
        }
    else:
        missing_llm_connection = True

    return {
        "id": agent_id,
        "role": data.get("role", "Agent"),
        "goal": data.get("goal", "Complete the assigned task."),
        "backstory": data.get("backstory", "A capable AI agent."),
        "llm": llm_config,
        "eligible": llm_config is not None,
        "skip_reason": "missing_llm_connection" if missing_llm_connection else None,
    }


def compile_graph(graph_json: dict) -> dict:
    """
    Compile the ReactFlow graph JSON into an execution plan.
    Returns an ordered list of agent configs based on the edge connections.
    """
    nodes = graph_json.get("nodes", [])
    edges = graph_json.get("edges", [])

    task_nodes = {n["id"]: n for n in nodes if n.get("type") == "taskNode"}
    webhook_nodes = {n["id"]: n for n in nodes if n.get("type") == "webhookNode"}
    agent_nodes = {n["id"]: n for n in nodes if n.get("type") == "agentNode"}
    llm_nodes = {n["id"]: n for n in nodes if n.get("type") == "llmNode"}

    task_connected_agent_ids: list[str] = []
    webhook_connected_agent_ids: list[str] = []

    # Build adjacency for agent->agent edges
    agent_edges = [
        e for e in edges if e["source"] in agent_nodes and e["target"] in agent_nodes
    ]

    # Topological sort of agents
    in_degree = {aid: 0 for aid in agent_nodes}
    successors = {aid: [] for aid in agent_nodes}
    for e in agent_edges:
        in_degree[e["target"]] += 1
        successors[e["source"]].append(e["target"])

    queue = [aid for aid, deg in in_degree.items() if deg == 0]
    ordered_agents = []
    while queue:
        aid = queue.pop(0)
        ordered_agents.append(aid)
        for succ in successors[aid]:
            in_degree[succ] -= 1
            if in_degree[succ] == 0:
                queue.append(succ)

    # Attach LLM connections from edges
    for edge in edges:
        src = edge["source"]
        tgt = edge["target"]
        if src in llm_nodes and tgt in agent_nodes:
            agent_nodes[tgt]["data"]["connectedLlm"] = src
        if src in task_nodes and tgt in agent_nodes:
            task_connected_agent_ids.append(tgt)
        if src in webhook_nodes and tgt in agent_nodes:
            webhook_connected_agent_ids.append(tgt)

    compiled_agents = [
        _build_agent_config(agent_nodes[aid], llm_nodes) for aid in ordered_agents
    ]

    return {
        "agents": compiled_agents,
        "execution_order": ordered_agents,
        "task_connected_agent_ids": task_connected_agent_ids,
        "webhook_connected_agent_ids": webhook_connected_agent_ids,
        "has_task_node": bool(task_nodes),
        "has_webhook_node": bool(webhook_nodes),
    }


async def execute_team(compiled: dict, task_input: str) -> AsyncIterator[str]:
    """
    Execute agents sequentially. Yields Server-Sent Event strings.
    This is a simulation that can be wired to real Agno agents.
    """
    agents = compiled["agents"]
    context = task_input

    for i, agent_cfg in enumerate(agents):
        role = agent_cfg["role"]
        llm_info = agent_cfg.get("llm")
        llm_label = (
            f"{llm_info['provider']}/{llm_info['model']}" if llm_info else "default LLM"
        )

        yield f"data: {json.dumps({'type': 'agent_start', 'agent': role, 'llm': llm_label, 'index': i})}\n\n"
        await asyncio.sleep(0.1)

        # In a real implementation, instantiate Agno agent here:
        # agent = agno.Agent(role=role, goal=goal, model=Model(...))
        # response = await agent.arun(context)
        # For now, emit a simulated response
        simulated_output = (
            f"[{role}] Processed task using {llm_label}: '{context[:200]}'"
            + f" → Output from {role} is ready."
        )
        context = simulated_output  # Pass output as next agent's input

        yield f"data: {json.dumps({'type': 'agent_output', 'agent': role, 'output': simulated_output})}\n\n"
        await asyncio.sleep(0.2)

    yield f"data: {json.dumps({'type': 'done', 'final_output': context})}\n\n"


async def execute_team_tasks(
    compiled: dict,
    task_inputs: list[str],
    execution_context: dict[str, Any] | None = None,
) -> AsyncIterator[str]:
    """
    Execute one or many tasks. Emits routing metadata per task and
    only activates agents with valid LLM connection.
    """
    all_agents = compiled.get("agents", [])
    context = execution_context or {"source": "task"}
    source = str(context.get("source") or "task").lower()

    if source == "webhook":
        entry_connected_ids = set(compiled.get("webhook_connected_agent_ids", []))
        has_entry_node = bool(compiled.get("has_webhook_node"))
    else:
        entry_connected_ids = set(compiled.get("task_connected_agent_ids", []))
        has_entry_node = bool(compiled.get("has_task_node"))

    if has_entry_node and not entry_connected_ids:
        all_agents = []
    elif entry_connected_ids:
        all_agents = [
            agent for agent in all_agents if agent.get("id") in entry_connected_ids
        ]

    eligible_agents = [agent for agent in all_agents if agent.get("eligible")]
    skipped_agents = [
        {
            "id": agent.get("id"),
            "agent": agent.get("role"),
            "reason": agent.get("skip_reason") or "not_eligible",
        }
        for agent in all_agents
        if not agent.get("eligible")
    ]

    for task_index, task_text in enumerate(task_inputs):
        routing_event = {
            "type": "task_start",
            "task_index": task_index,
            "task_input": task_text,
            "routing": {
                "activated_agents": [
                    {"id": agent.get("id"), "agent": agent.get("role")}
                    for agent in eligible_agents
                ],
                "skipped_agents": skipped_agents,
            },
            "bootstrap": {
                "source": source,
                "trigger_id": context.get("trigger_id"),
                "timestamp": context.get("timestamp"),
                "correlation_id": context.get("correlation_id"),
                "test_origin": context.get("test_origin"),
            },
        }
        yield f"data: {json.dumps(routing_event)}\n\n"

        if not eligible_agents:
            error_event = {
                "type": "task_error",
                "task_index": task_index,
                "message": "No eligible agents available (all missing LLM connection).",
            }
            yield f"data: {json.dumps(error_event)}\n\n"
            continue

        routing_decision = await route_task_to_agent(task_text, eligible_agents)
        selected_agent_id = routing_decision.get("selected_agent_id")
        selected_agent = None
        for candidate in eligible_agents:
            if candidate.get("id") == selected_agent_id:
                selected_agent = candidate
                break
        if not selected_agent:
            selected_agent = eligible_agents[0]

        selected_llm = selected_agent.get("llm") or {}
        llm_label = f"{selected_llm.get('provider', 'unknown')}/{selected_llm.get('model', 'unknown')}"

        decision_event = {
            "type": "routing_decision",
            "task_index": task_index,
            "selected_agent_id": selected_agent.get("id"),
            "selected_agent": selected_agent.get("role"),
            "selected_llm": {
                "provider": selected_llm.get("provider"),
                "model": selected_llm.get("model"),
            },
            "reason": routing_decision.get("reason"),
            "scores": routing_decision.get("scores") or [],
            "fallback_used": bool(routing_decision.get("fallback_used", False)),
            "ineligible_agents": skipped_agents,
            "bootstrap_source": source,
            "correlation_id": context.get("correlation_id"),
        }
        yield f"data: {json.dumps(decision_event)}\n\n"

        role = selected_agent["role"]
        yield f"data: {json.dumps({'type': 'agent_start', 'agent': role, 'llm': llm_label, 'index': 0, 'task_index': task_index})}\n\n"
        await asyncio.sleep(0.05)

        system_prompt = _build_agent_system_prompt(selected_agent)
        user_prompt = _build_execution_user_prompt(task_text)

        try:
            final_output = await generate_llm_response(
                selected_llm,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
        except Exception as exc:
            provider = str(selected_llm.get("provider") or "provider")
            model = str(selected_llm.get("model") or "model")
            friendly = _friendly_provider_error(str(exc), provider, model)
            fail_event = {
                "type": "task_error",
                "task_index": task_index,
                "message": f"Execution failed for {role}: {friendly}",
            }
            yield f"data: {json.dumps(fail_event)}\n\n"
            continue

        yield f"data: {json.dumps({'type': 'agent_output', 'agent': role, 'output': final_output, 'task_index': task_index})}\n\n"
        await asyncio.sleep(0.08)

        yield f"data: {json.dumps({'type': 'task_done', 'task_index': task_index, 'final_output': final_output})}\n\n"

    yield f"data: {json.dumps({'type': 'done', 'final_output': 'All tasks processed.', 'total_tasks': len(task_inputs)})}\n\n"
