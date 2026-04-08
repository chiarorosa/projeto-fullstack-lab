## 1. Backend Routing Engine

- [x] 1.1 Create semantic routing service that ranks executable agents per task using `goal`/`backstory` and returns structured decision metadata.
- [x] 1.2 Add deterministic fallback routing strategy for invalid/unavailable router responses.
- [x] 1.3 Update execution pipeline to run selected agent with its connected LLM configuration (provider/model/base URL/key) and persist selected agent details.

## 2. Backend Execution and Artifacts Contract

- [x] 2.1 Enrich SSE events with routing decision payload (`selected_agent`, candidate scores/reasons, ineligible agents, fallback flag).
- [x] 2.2 Extend persisted run artifact schema to store routing reason, selected model/provider, and decision metadata per task.
- [x] 2.3 Expose backend API endpoints that return run artifacts grouped by execution with task-level detail.

## 3. Frontend Node Connectivity and Validation UX

- [x] 3.1 Show node connectivity summaries in properties/canvas for Task, Agent, and LLM nodes.
- [x] 3.2 Add visual state badges for agent executability (`Ready` vs `Not executable`) based on LLM linkage.
- [x] 3.3 Block or warn on Run Team when graph has no executable agents and provide actionable fix guidance.

## 4. Frontend Run Artifacts Workspace

- [x] 4.1 Implement dedicated artifacts tab/workspace separate from transient execution logs.
- [x] 4.2 Render execution-level and task-level artifact cards (input, selected agent, routing reason, output/error, timestamp, model/provider).
- [x] 4.3 Add artifact filtering/navigation by execution id and task status.

## 5. Verification

- [x] 5.1 Run backend smoke/integration checks for routing selection, fallback path, and persisted artifacts.
- [x] 5.2 Run frontend build and validate UX for node connectivity states, run blocking/warnings, and artifacts workspace rendering.
