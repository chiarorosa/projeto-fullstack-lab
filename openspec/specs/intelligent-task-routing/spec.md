# intelligent-task-routing Specification

## Purpose
Select the most suitable executable agent per task using semantic evaluation of agent profile (`goal`/`backstory`), execute with the selected agent LLM, and persist routing artifacts.
## Requirements
### Requirement: Semantic Agent Selection Per Task
The system SHALL select the most suitable executable agent for each task based on semantic evaluation of agent `goal` and `backstory` against task intent, regardless of supported bootstrap source.

#### Scenario: Multiple executable agents available from Task Node bootstrap
- **WHEN** a task is received from Task Node and two or more agents are executable
- **THEN** backend evaluates each candidate using agent profile (`goal`, `backstory`)
- **AND** backend selects exactly one primary agent with ranking score and reason

#### Scenario: Multiple executable agents available from Webhook bootstrap
- **WHEN** a task is derived from a valid Webhook bootstrap input and two or more agents are executable
- **THEN** backend evaluates each candidate using agent profile (`goal`, `backstory`)
- **AND** backend selects exactly one primary agent with ranking score and reason

#### Scenario: Router fallback mode
- **WHEN** semantic router LLM is unavailable or returns invalid structure
- **THEN** backend uses deterministic fallback strategy
- **AND** routing metadata indicates fallback was used

### Requirement: Agent Execution Uses Connected LLM
The system SHALL execute the selected agent using the specific LLM node connected to that agent.

#### Scenario: Selected agent has valid LLM node
- **WHEN** selected agent has connected provider/model configuration
- **THEN** task execution runs with that exact provider/model/base URL/API key context

#### Scenario: Selected agent loses LLM eligibility before execution
- **WHEN** selected agent is no longer executable due to missing/invalid LLM linkage
- **THEN** backend marks task as failed with explicit eligibility error
- **AND** task result is persisted with failure status

### Requirement: Task-Level Routing Artifact
The system SHALL produce and persist task-level routing artifacts for each executed task.

#### Scenario: Task routing decision emitted
- **WHEN** backend completes routing decision for a task
- **THEN** execution stream emits routing artifact including selected agent, candidates, score/reason, and ineligible agents

#### Scenario: Run artifacts queried later
- **WHEN** user opens run artifacts workspace
- **THEN** persisted task artifact includes task input, selected agent, routing reason, output/error, and timestamp

