## MODIFIED Requirements

### Requirement: Provider Default Configuration Hints
The system SHALL display provider-specific configuration hints in LLM Properties, including default base URL and expected environment variable key.

#### Scenario: User selects OpenRouter provider
- **WHEN** user selects `OpenRouter AI` in LLM Properties
- **THEN** the panel shows default base URL `https://openrouter.ai/api/v1`
- **AND** the panel shows environment variable hint `OPENROUTER_API_KEY`

#### Scenario: User selects Local provider
- **WHEN** user selects `Local` in LLM Properties
- **THEN** the panel shows local endpoint examples
- **AND** the base URL field remains editable for custom local runtimes

### Requirement: Provider Model Reference Links
The system SHALL provide a provider-specific link to official model reference documentation in LLM Properties.

#### Scenario: User needs OpenAI model IDs
- **WHEN** provider is `OpenAI`
- **THEN** the panel shows a link to `https://platform.openai.com/docs/models`

#### Scenario: User needs Anthropic or Gemini model IDs
- **WHEN** provider is `Anthropic` or `Google`
- **THEN** the panel shows the corresponding official model documentation link for that provider

### Requirement: Legacy Provider Compatibility
The system SHALL normalize legacy provider value `opencode` to `openrouter` in LLM Properties.

#### Scenario: Existing graph uses legacy provider value
- **WHEN** user selects an LLM node with provider `opencode`
- **THEN** the Provider field displays `OpenRouter AI`
- **AND** OpenRouter guidance and links are shown

## ADDED Requirements

### Requirement: LLM Provider Validation Action
The system SHALL provide a direct provider validation action in LLM Properties so users can verify provider credentials/connectivity without running team execution.

#### Scenario: User validates configured provider from LLM Properties
- **WHEN** user clicks `Test Provider` in LLM Properties for a selected LLM node
- **THEN** the client sends provider settings for that node to a backend validation endpoint
- **AND** the UI shows loading state while validation is in progress

#### Scenario: Validation succeeds
- **WHEN** backend confirms provider credentials/connectivity
- **THEN** the UI shows a success status/message in LLM Properties

#### Scenario: Validation fails
- **WHEN** backend cannot validate provider credentials/connectivity
- **THEN** the UI shows an error status/message with actionable guidance

### Requirement: Provider-Specific Validation Endpoint
The backend SHALL validate provider settings based on provider type and return a normalized validation result.

#### Scenario: Backend validates cloud provider key
- **WHEN** provider is `openai`, `anthropic`, `google`, or `openrouter`
- **THEN** backend performs a lightweight provider API check using supplied API key and optional base URL
- **AND** backend returns a normalized JSON response with `ok` boolean and `message`

#### Scenario: Backend validates local provider endpoint
- **WHEN** provider is `local`
- **THEN** backend performs a lightweight reachability check on supplied or default local base URL
- **AND** backend returns a normalized JSON response with `ok` boolean and `message`
