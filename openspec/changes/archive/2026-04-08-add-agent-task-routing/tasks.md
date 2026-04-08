## 1. Execution Contract and Validation

- [x] 1.1 Extend execution request schema to accept `task_input` and `task_inputs`, with normalization rules and validation errors for empty payloads.
- [x] 1.2 Add Task Node bootstrap validation in execution flow (require Task Node as input source, with compatibility fallback strategy if enabled).
- [x] 1.3 Update execute route to process normalized task lists and preserve backward compatibility for existing single-task clients.

## 2. Agent Eligibility and Routing

- [x] 2.1 Update graph compilation to mark eligible agents only when a valid connected LLM node exists.
- [x] 2.2 Implement per-task routing metadata (`activated_agents`, `skipped_agents`, reasons) before agent execution.
- [x] 2.3 Handle no-eligible-agent tasks by emitting clear status/error events and skipping agent output generation for that task.

## 3. Task Node and Frontend Integration

- [x] 3.1 Add `taskNode` type in frontend palette/canvas/store as the bootstrap node for task input.
- [x] 3.2 Implement Task Node properties UI for single and batch task entry/editing.
- [x] 3.3 Enrich SSE payloads with task-level context (index/id) and routing summary for each task item.
- [x] 3.4 Update frontend execution flow to read tasks from Task Node and render activated/skipped agent information.

## 4. Verification

- [x] 4.1 Run backend smoke checks for schema import and execution route behavior with single and batch payloads.
- [x] 4.2 Run frontend build and validate logs/UI rendering for task-level routing events and Task Node bootstrap behavior.
