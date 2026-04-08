## Context

The current product still carries Tool Node concepts in both UI and backend execution, including tool selection, tool node rendering, `connectedTools` wiring, and tool-specific execution branches. In practice, this capability is not part of the intended roadmap and creates maintenance overhead because future extensibility is expected to come from SKILLS and MCP.

This is a cross-cutting cleanup because it touches canvas composition, node data normalization, execution compiler logic, and OpenSpec capability definitions. Existing task-routing and agent/LLM execution flows must remain stable after Tool Node removal.

## Goals / Non-Goals

**Goals:**
- Remove Tool Node UX and data wiring from the frontend graph editor.
- Remove backend runtime paths that execute tools or emit tool-specific SSE events.
- Keep task-routing, agent eligibility, and LLM execution behavior unchanged.
- Update specs so they reflect removal of Tool Node behavior and future SKILLS/MCP direction.

**Non-Goals:**
- Implement SKILLS runtime execution in this change.
- Implement MCP protocol integration in this change.
- Redesign task routing or run artifacts architecture.

## Decisions

1. **Hard-remove Tool Node from active editor flows now**
   - Remove Tool Node entries from sidebar palette and tool-type editing controls from Properties Panel.
   - Rationale: avoids carrying partially supported behavior and eliminates user confusion.
   - Alternative considered: hide with feature flag; rejected because dead code would still increase complexity.

2. **Compile graphs without tool edges/metadata**
   - Remove `connectedTools` collection and propagation in graph normalization.
   - Rationale: agent execution should depend only on task input and connected LLM eligibility.
   - Alternative considered: keep fields but ignore at runtime; rejected because stale payload contracts tend to reappear as accidental dependencies.

3. **Delete backend tool execution branches entirely**
   - Remove `openrouter_ai` tool-specific handlers and `tool_executed`/`tool_error` event emission from compiler execution loops.
   - Rationale: enforces a single supported execution model until SKILLS/MCP is introduced.
   - Alternative considered: keep code path but unreachable; rejected to reduce risk and maintenance burden.

4. **Model future extensibility at spec level only for now**
   - Add a new capability spec describing SKILLS/MCP extensibility intent without runtime obligations yet.
   - Rationale: documents direction and avoids reintroducing Tool Nodes in future work.
   - Alternative considered: postpone spec updates until implementation starts; rejected because current requirements would remain misleading.

## Risks / Trade-offs

- [Risk] Existing saved graphs may still contain Tool Nodes or `connectedTools` metadata -> Mitigation: treat unknown or legacy tool node data as ignored during compile/load and avoid runtime failure.
- [Risk] Existing tests or docs that assert tool SSE events may fail -> Mitigation: update assertions and docs to reflect agent/LLM-only execution path.
- [Risk] Removing OpenRouter tool requirements may look like a regression -> Mitigation: document this as intentional de-scope in proposal/spec deltas and point to SKILLS/MCP follow-up.

## Migration Plan

1. Remove frontend Tool Node creation/editing surfaces.
2. Remove graph normalization fields related to tool connectivity.
3. Remove backend tool execution handlers and event branches.
4. Update OpenSpec capability deltas and task checklist.
5. Run regression checks for task execution with connected LLM agents.

Rollback strategy: restore Tool Node UI/backend branches from git history if critical user flow is unexpectedly blocked.

## Open Questions

- Should legacy tool nodes be visually marked as deprecated if loaded from old graphs, or fully hidden/ignored with no UI indication?
- Do we want to reserve any neutral extension node type now, or defer all extensibility UI until SKILLS/MCP implementation begins?
