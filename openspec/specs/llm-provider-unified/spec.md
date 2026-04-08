# llm-provider-unified Specification

## Purpose
TBD - created by archiving change llm-provider-refactor. Update Purpose after archive.
## Requirements
### Requirement: Unified LLM Provider Selection
The system SHALL allow users to select from 5 pre-defined LLM providers: OpenAI, Anthropic, Google, Local, and OpenCode.

#### Scenario: User selects a provider in the LLM Node
- **WHEN** user clicks on an LLM node and opens the properties panel
- **THEN** a provider dropdown shows options: OpenAI, Anthropic, Google, Local, OpenCode

#### Scenario: User changes provider
- **WHEN** user selects a different provider from the dropdown
- **THEN** the provider value updates in the node data
- **AND** the contextual fields adjust to the selected provider

### Requirement: Provider-Specific Configuration
The system SHALL display different configuration fields based on the selected provider.

#### Scenario: OpenAI provider selected
- **WHEN** user selects "OpenAI" as provider
- **THEN** the form shows: Model (text input), API Key (password input)
- **AND** placeholder shows "e.g., gpt-4o, gpt-4o-mini"

#### Scenario: Anthropic provider selected
- **WHEN** user selects "Anthropic" as provider
- **THEN** the form shows: Model (text input), API Key (password input)
- **AND** placeholder shows "e.g., claude-3-5-sonnet, claude-3-haiku"

#### Scenario: Google provider selected
- **WHEN** user selects "Google" as provider
- **THEN** the form shows: Model (text input), API Key (password input)
- **AND** placeholder shows "e.g., gemini-1.5-pro, gemini-1.5-flash"

#### Scenario: Local provider selected
- **WHEN** user selects "Local" as provider
- **THEN** the form shows: Model (text input), Base URL (text input)
- **AND** placeholder shows "e.g., llama-3.1-70b" for model
- **AND** placeholder shows "http://localhost:11434/v1" for Base URL
- **AND** tooltip indicates default port for Ollama (11434) or LMStudio (1234)

#### Scenario: OpenCode provider selected
- **WHEN** user selects "OpenCode" as provider
- **THEN** the form shows: Model (text input), API Key (password input)
- **AND** placeholder shows "e.g., opencode-model-name"

### Requirement: Backend Provider Mapping
The system SHALL correctly map provider values to the backend execution layer.

#### Scenario: Backend receives a graph with LLM configuration
- **WHEN** the compiler.py processes a graph with LLM node data
- **THEN** the provider value MUST be passed to the execution engine
- **AND** the provider mapping MUST support: openai, anthropic, google, local, opencode

### Requirement: Visual Provider Display
The LLM Node in the canvas SHALL display the selected provider clearly.

#### Scenario: LLM Node renders with provider
- **WHEN** an LLM node is rendered on the canvas
- **THEN** the node shows the provider name (e.g., "OpenAI", "Anthropic") in the subtitle
- **AND** the node uses the provider's brand color for visual distinction

