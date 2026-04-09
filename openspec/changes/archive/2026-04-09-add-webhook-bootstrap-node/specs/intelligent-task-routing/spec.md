## MODIFIED Requirements

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
