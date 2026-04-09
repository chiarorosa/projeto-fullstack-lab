# agent-task-routing Specification

## Purpose
Define task-driven agent activation so execution starts from a Task Node, only eligible agents run, and task outcomes remain traceable in batch runs.
## Requirements
### Requirement: Task Node Bootstrap
The system SHALL require at least one valid supported bootstrap source for execution input and task dispatch.

#### Scenario: Execution starts with valid Task Node
- **WHEN** the graph contains a Task Node with at least one task item
- **THEN** the backend uses Task Node payload as the source for execution input
- **AND** execution can dispatch tasks to downstream agent flow

#### Scenario: Execution starts with valid Webhook Node
- **WHEN** the graph contains a Webhook Node registered as a valid bootstrap source
- **THEN** the backend can start execution from webhook payload mapped into task input context
- **AND** execution can dispatch tasks to downstream agent flow

#### Scenario: Execution requested without valid bootstrap source
- **WHEN** the graph does not contain a valid Task Node or valid Webhook Node bootstrap source
- **THEN** the system returns an explicit validation error indicating at least one supported bootstrap source is required

### Requirement: Agent Activation Requires Connected LLM Node
The system SHALL only activate agents that have a valid connected LLM node in the compiled graph.

#### Scenario: Agent has connected LLM
- **WHEN** an agent has `connectedLlm` pointing to an existing LLM node
- **THEN** the agent is marked eligible for activation

#### Scenario: Agent has no connected LLM
- **WHEN** an agent does not have a valid connected LLM node
- **THEN** the agent is excluded from activation
- **AND** routing metadata includes this agent in `skipped_agents` with reason `missing_llm_connection`
- **AND** the UI marks this agent as not executable before run

### Requirement: Task-Level Routing Metadata
The execution stream SHALL expose routing metadata per task item, including activated and skipped agents.

#### Scenario: Task execution starts
- **WHEN** backend starts processing a task item
- **THEN** stream emits task-level routing metadata containing `activated_agents` and `skipped_agents`

#### Scenario: Task has no eligible agents
- **WHEN** no agents are eligible for a task
- **THEN** stream emits a clear status or error event indicating no active agents are available
- **AND** task execution for that item ends without agent output events

### Requirement: Batch Execution Result Traceability
The system SHALL preserve traceability of outputs for each task item in batch execution.

#### Scenario: Multiple task inputs are executed
- **WHEN** backend processes a batch request
- **THEN** each emitted event includes task index or task identifier context
- **AND** final output state identifies completion per task item

