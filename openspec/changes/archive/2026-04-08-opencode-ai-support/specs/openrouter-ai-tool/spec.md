## ADDED Requirements

### Requirement: OpenRouter AI Tool Configuration
The system SHALL allow users to configure an OpenRouter AI tool in the visual editor with a descriptive name and task type.

#### Scenario: User adds OpenRouter AI tool to graph
- **WHEN** user selects "OpenRouter AI" from the tool type dropdown
- **THEN** a new tool node is created with type "openrouter_ai"

#### Scenario: User configures OpenRouter AI tool properties
- **WHEN** user sets the tool name and task type in the properties panel
- **THEN** the tool node data is updated with the provided values

### Requirement: OpenRouter AI Tool Execution
The system SHALL execute OpenRouter API calls when an agent uses the OpenRouter AI tool during workflow execution.

#### Scenario: Agent calls OpenRouter AI tool with prompt
- **WHEN** an agent's connected tool includes an OpenRouter AI tool with a task prompt
- **THEN** the backend sends a request to the OpenRouter API and returns the response

#### Scenario: OpenRouter AI tool returns results to agent
- **WHEN** the OpenRouter API returns a successful response
- **THEN** the tool result is passed back to the agent for use in its workflow

### Requirement: OpenRouter AI Tool Error Handling
The system SHALL provide clear error messages when OpenRouter AI tool execution fails.

#### Scenario: API key is missing
- **WHEN** the OpenRouter API key is not configured in the server environment
- **THEN** the tool returns an error indicating the API key is not configured

#### Scenario: API request fails
- **WHEN** the OpenRouter API returns an error or times out
- **THEN** the tool returns a descriptive error message to the agent
