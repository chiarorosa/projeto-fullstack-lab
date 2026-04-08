## ADDED Requirements

### Requirement: SKILLS and MCP as Extensibility Direction
The system SHALL define SKILLS and MCP as the intended extensibility model and SHALL not depend on Tool Node concepts for current extensibility behavior.

#### Scenario: Product artifacts describe extensibility model
- **WHEN** maintainers update OpenSpec artifacts for extensibility behavior
- **THEN** artifacts describe SKILLS and MCP as the extension direction
- **AND** artifacts do not describe Tool Nodes as an active extensibility mechanism

#### Scenario: Scope remains transitional before SKILLS/MCP runtime
- **WHEN** this change is applied without a full SKILLS or MCP runtime implementation
- **THEN** requirements only define direction and compatibility expectations
- **AND** no specific SKILLS/MCP runtime API contract is required yet

### Requirement: Execution Flow Is Independent from Tool Node Extensibility
The system SHALL execute task routing and agent-LLM flows without requiring Tool Node presence or Tool Node metadata.

#### Scenario: Team execution runs with task and agent graph only
- **WHEN** execution is started from a valid Task Node with eligible agents connected to LLM nodes
- **THEN** the run completes using task-routing and agent-LLM execution paths
- **AND** no Tool Node-specific execution branch is required for successful completion
