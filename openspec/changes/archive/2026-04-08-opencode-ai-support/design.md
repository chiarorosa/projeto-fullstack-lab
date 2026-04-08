## Context

The Visual Multi-Agent Team Builder currently supports multiple tool types and has a recent change scoped to OpenCode.ai. That scope was incorrect; the intended provider is OpenRouter.ai, which offers a unified interface for many LLMs through an OpenAI-compatible API.

System context:
- **Frontend**: ReactFlow editor with agentNode/llmNode/toolNode and a Properties Panel
- **Backend**: Compiler + execution flow in `backend/core/compiler.py`
- **Execution**: Tool results are emitted in SSE events and fed back into agent context

## Goals / Non-Goals

**Goals:**
- Correct the integration target from OpenCode.ai to OpenRouter.ai
- Keep tool execution architecture unchanged while renaming handler semantics
- Use OpenRouter's OpenAI-compatible endpoint (`/chat/completions`)
- Preserve robust error handling for missing keys, failures, and timeouts

**Non-Goals:**
- Implement full OpenRouter feature surface (routing policies, prompt caching, etc.)
- Add provider-specific advanced parameters in this change
- Redesign tool execution orchestration

## Decisions

1. **Endpoint correction to OpenRouter**
   - Use `OPENROUTER_API_KEY` and default base URL `https://openrouter.ai/api/v1`
   - Rationale: aligns with intended product and avoids semantic mismatch in docs/code
   - Alternative: keep OpenCode and add OpenRouter later; rejected due to immediate correctness need

2. **Keep OpenAI-compatible payload shape**
   - Continue using `model`, `messages`, and `max_tokens` with `/chat/completions`
   - Rationale: minimal change and reuses tested code path
   - Alternative: custom adapter layer now; rejected as unnecessary complexity

3. **Tool path continuity**
   - Retain tool node flow and SSE event behavior (`tool_executed`, `tool_error`)
   - Rationale: minimal blast radius and easy verification
   - Alternative: shift to LLM provider path immediately; rejected for this correction-only scope

## Risks / Trade-offs

- [Risk] Existing env vars still use old names (`OPENCODE_*`) → Mitigation: migrate to `OPENROUTER_*`, optionally keep temporary fallback during implementation
- [Risk] Model naming varies by OpenRouter routes → Mitigation: accept model as configurable input and validate errors clearly
- [Risk] Existing docs/examples become stale → Mitigation: update labels/spec/tasks in same change
