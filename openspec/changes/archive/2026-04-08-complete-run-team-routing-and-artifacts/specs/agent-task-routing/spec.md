## MODIFIED Requirements

### Requirement: Batch and Single Task Execution Input
The execution API SHALL accept both single-task and batch-task input formats and normalize them for processing.

#### Scenario: User executes team with a single task
- **WHEN** request payload includes `task_input`
- **THEN** backend normalizes it to a single-item internal task list
- **AND** execution proceeds without requiring `task_inputs`

#### Scenario: User executes team with multiple tasks
- **WHEN** request payload includes `task_inputs` with one or more items
- **THEN** backend normalizes it to the internal task list in the same order
- **AND** execution processes tasks in deterministic sequence

### Requirement: Task Node Bootstrap
The system SHALL provide a Task Node as the bootstrap entry point for execution input and task dispatch.

#### Scenario: User adds Task Node in canvas
- **WHEN** user creates a `Task Node`
- **THEN** the node exposes input for single task and batch tasks
- **AND** it can connect to downstream agent flow as execution source

#### Scenario: Execution starts with Task Node configured
- **WHEN** graph contains a valid `Task Node` with at least one task item
- **THEN** backend uses Task Node payload as source of `task_input`/`task_inputs`

#### Scenario: Execution requested without Task Node
- **WHEN** graph does not contain a valid `Task Node`
- **THEN** system returns an explicit validation error indicating Task Node is required for bootstrap

### Requirement: Agent Activation Requires Connected LLM Node
The system SHALL only activate agents that have a valid connected LLM node in the compiled graph.

#### Scenario: Agent has connected LLM
- **WHEN** an agent has `connectedLlm` pointing to an existing LLM node
- **THEN** the agent is marked eligible for activation

#### Scenario: Agent has no connected LLM
- **WHEN** an agent does not have a valid connected LLM node
- **THEN** the agent is excluded from activation
- **AND** the routing metadata includes this agent in `skipped_agents` with reason `missing_llm_connection`
- **AND** the UI marks this agent as not executable before run

### Requirement: Task-Level Routing Metadata
The execution stream SHALL expose per-task routing metadata showing activated and skipped agents.

#### Scenario: Task execution starts
- **WHEN** backend starts processing a task item
- **THEN** stream emits task-level routing metadata containing `activated_agents` and `skipped_agents`

#### Scenario: Task has no eligible agents
- **WHEN** no agents are eligible for a task
- **THEN** stream emits an error/status event indicating no active agents available
- **AND** task execution for that item ends without agent output events

### Requirement: Batch Execution Result Traceability
The system SHALL keep batch outputs traceable per task item.

#### Scenario: Multiple task inputs are executed
- **WHEN** backend processes a batch request
- **THEN** each emitted event includes task index or task identifier context
- **AND** final output state identifies completion per task item
