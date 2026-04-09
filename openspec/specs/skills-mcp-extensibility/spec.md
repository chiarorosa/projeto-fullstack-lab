# skills-mcp-extensibility Specification

## Purpose
Define SKILLS and MCP as the forward extensibility direction while execution remains focused on task routing through Task, Agent, and connected LLM nodes.

## Requirements
### Requirement: SKILLS and MCP as Extensibility Direction
The system SHALL define SKILLS and MCP as the intended extensibility model and SHALL not depend on Tool Node concepts for current extensibility behavior.

#### Scenario: Product artifacts describe extensibility model
- **WHEN** maintainers update OpenSpec artifacts for extensibility behavior
- **THEN** artifacts describe SKILLS and MCP as the extension direction
- **AND** artifacts do not describe Tool Nodes as an active extensibility mechanism

#### Scenario: Scope remains transitional before SKILLS/MCP runtime
- **WHEN** this capability is applied without a full SKILLS or MCP runtime implementation
- **THEN** requirements define direction and compatibility expectations only
- **AND** no specific SKILLS/MCP runtime API contract is required yet

### Requirement: Execution Flow Is Independent from Tool Node Extensibility
The system SHALL execute task routing and agent-LLM flows without requiring Tool Node presence or Tool Node metadata.

#### Scenario: Team execution runs with task and agent graph only
- **WHEN** execution is started from a valid Task Node with eligible agents connected to LLM nodes
- **THEN** the run completes using task-routing and agent-LLM execution paths
- **AND** no Tool Node-specific execution branch is required for successful completion
