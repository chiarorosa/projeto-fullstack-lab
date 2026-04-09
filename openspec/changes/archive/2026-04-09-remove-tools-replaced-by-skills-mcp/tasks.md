## 1. Frontend Tool Node Removal

- [x] 1.1 Remove Tool Node entries from `frontend/src/components/SidebarPalette.tsx` so users cannot create new Tool Nodes
- [x] 1.2 Remove Tool Node-specific property editing (tool type selector and related fields) from `frontend/src/components/PropertiesPanel.tsx`
- [x] 1.3 Update `frontend/src/components/Canvas.tsx` and related node data shaping so compile payload no longer depends on `connectedTools`

## 2. Backend Tool Execution Removal

- [x] 2.1 Remove OpenRouter tool execution helper and any `openrouter_ai` tool branch handling from `backend/core/compiler.py`
- [x] 2.2 Remove emission of tool-specific SSE events (`tool_executed`, `tool_error`) from agent execution loops
- [x] 2.3 Ensure compile/execution paths continue to run task-routing and agent/LLM flows without tool metadata

## 3. Spec and Contract Alignment

- [x] 3.1 Validate and refine `specs/openrouter-ai-tool/spec.md` removal deltas with explicit migration notes
- [x] 3.2 Validate and refine `specs/skills-mcp-extensibility/spec.md` so future direction is clear but non-committal on runtime details

## 4. Verification

- [x] 4.1 Verify canvas/editor flow works without Tool Nodes (create Task, Agent, LLM graph and execute)
- [x] 4.2 Verify backend execution succeeds for single-task and batch-task runs with no tool branches
- [x] 4.3 Verify no references to active Tool Node execution remain in user-facing OpenSpec artifacts for this change
