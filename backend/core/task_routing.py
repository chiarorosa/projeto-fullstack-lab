from __future__ import annotations

import json
from typing import Any

from core.llm_runtime import generate_llm_response


def _build_router_user_prompt(task_text: str, agents: list[dict[str, Any]]) -> str:
    agent_lines: list[str] = []
    for idx, agent in enumerate(agents):
        agent_lines.append(
            (
                f"[{idx}] id={agent['id']}\n"
                f"role={agent.get('role', '')}\n"
                f"goal={agent.get('goal', '')}\n"
                f"backstory={agent.get('backstory', '')}\n"
            )
        )

    return (
        "Task:\n"
        f"{task_text}\n\n"
        "Candidate agents:\n"
        + "\n".join(agent_lines)
        + "\nReturn strict JSON only: "
        + '{"selected_index": <int>, "reason": "<short>", "scores": [{"index": <int>, "score": <0-100>, "reason": "<short>"}]}'
    )


def _fallback_route(task_text: str, agents: list[dict[str, Any]]) -> dict[str, Any]:
    task_words = {w for w in task_text.lower().split() if w}
    scored: list[tuple[int, int, str]] = []

    for idx, agent in enumerate(agents):
        profile = f"{agent.get('goal', '')} {agent.get('backstory', '')}".lower()
        profile_words = {w for w in profile.split() if w}
        overlap = len(task_words.intersection(profile_words))
        score = 35 + min(60, overlap * 8)
        reason = (
            "Keyword overlap fallback"
            if overlap > 0
            else "Default fallback to first viable agent"
        )
        scored.append((idx, score, reason))

    scored.sort(key=lambda item: item[1], reverse=True)
    best_idx, _, best_reason = scored[0] if scored else (0, 50, "No candidates")

    return {
        "selected_index": best_idx,
        "reason": best_reason,
        "scores": [
            {"index": idx, "score": score, "reason": reason}
            for idx, score, reason in scored
        ],
        "fallback_used": True,
    }


def _parse_router_json(text: str) -> dict[str, Any] | None:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    snippet = text[start : end + 1]
    try:
        value = json.loads(snippet)
    except Exception:
        return None
    if not isinstance(value, dict):
        return None
    return value


async def route_task_to_agent(
    task_text: str,
    eligible_agents: list[dict[str, Any]],
) -> dict[str, Any]:
    if not eligible_agents:
        return {
            "selected_agent": None,
            "selected_agent_id": None,
            "reason": "No eligible agents",
            "scores": [],
            "fallback_used": True,
        }

    if len(eligible_agents) == 1:
        only = eligible_agents[0]
        return {
            "selected_agent": only.get("role"),
            "selected_agent_id": only.get("id"),
            "selected_agent_llm": only.get("llm"),
            "reason": "Single eligible agent available",
            "scores": [
                {
                    "agent_id": only.get("id"),
                    "agent": only.get("role"),
                    "score": 100,
                    "reason": "Only eligible candidate",
                }
            ],
            "fallback_used": False,
        }

    router_llm = eligible_agents[0].get("llm")
    if not router_llm:
        fallback = _fallback_route(task_text, eligible_agents)
    else:
        system_prompt = "You are a strict JSON task router. Pick one best agent for the task by goal/backstory relevance."
        user_prompt = _build_router_user_prompt(task_text, eligible_agents)
        try:
            router_text = await generate_llm_response(
                router_llm, system_prompt, user_prompt
            )
            parsed = _parse_router_json(router_text)
            if (
                parsed is None
                or not isinstance(parsed.get("selected_index"), int)
                or parsed.get("selected_index") < 0
                or parsed.get("selected_index") >= len(eligible_agents)
            ):
                fallback = _fallback_route(task_text, eligible_agents)
            else:
                fallback = {
                    "selected_index": parsed["selected_index"],
                    "reason": str(parsed.get("reason") or "Router selected this agent"),
                    "scores": parsed.get("scores")
                    if isinstance(parsed.get("scores"), list)
                    else [],
                    "fallback_used": False,
                }
        except Exception:
            fallback = _fallback_route(task_text, eligible_agents)

    selected_index = int(fallback.get("selected_index", 0))
    if selected_index < 0 or selected_index >= len(eligible_agents):
        selected_index = 0

    selected_agent = eligible_agents[selected_index]

    score_items: list[dict[str, Any]] = []
    for item in fallback.get("scores", []):
        if not isinstance(item, dict):
            continue
        idx = item.get("index")
        if not isinstance(idx, int) or idx < 0 or idx >= len(eligible_agents):
            continue
        score_items.append(
            {
                "agent_id": eligible_agents[idx].get("id"),
                "agent": eligible_agents[idx].get("role"),
                "score": int(item.get("score", 0)),
                "reason": str(item.get("reason") or ""),
            }
        )

    return {
        "selected_agent": selected_agent.get("role"),
        "selected_agent_id": selected_agent.get("id"),
        "selected_agent_llm": selected_agent.get("llm"),
        "reason": str(fallback.get("reason") or ""),
        "scores": score_items,
        "fallback_used": bool(fallback.get("fallback_used", False)),
    }
