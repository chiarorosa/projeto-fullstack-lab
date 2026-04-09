## REMOVED Requirements

### Requirement: OpenRouter AI Tool Configuration
**Reason**: Tool Node-based extensibility is being removed from active product behavior and replaced by the SKILLS/MCP direction.
**Migration**: Remove dependencies on Tool Node configuration in flows and use agent + connected LLM execution until SKILLS/MCP capabilities are implemented.

#### Scenario: Existing flow references Tool Node configuration
- **WHEN** a saved or in-progress flow includes Tool Node configuration for OpenRouter execution
- **THEN** maintainers remove Tool Node dependencies from that flow
- **AND** execution is moved to agent + connected LLM routing behavior

### Requirement: OpenRouter AI Tool Execution
**Reason**: Backend tool execution branches are removed to keep a single supported execution model while SKILLS/MCP is introduced in future changes.
**Migration**: Route task execution through agent selection and connected LLM nodes; do not invoke `openrouter_ai` tool branches.

#### Scenario: Runtime receives execution request
- **WHEN** the backend processes team execution after this change
- **THEN** runtime uses task-routing and agent/LLM execution only
- **AND** runtime does not call any `openrouter_ai` tool branch

### Requirement: OpenRouter AI Tool Error Handling
**Reason**: Error handling tied to Tool Node execution is no longer applicable after Tool Node path removal.
**Migration**: Handle provider and execution failures through existing agent/LLM execution error paths and future SKILLS/MCP-specific error contracts.

#### Scenario: Provider error occurs during execution
- **WHEN** execution fails due to provider or connectivity issues
- **THEN** the system reports errors through existing agent/LLM execution error events
- **AND** no Tool Node-specific error event contract is required
