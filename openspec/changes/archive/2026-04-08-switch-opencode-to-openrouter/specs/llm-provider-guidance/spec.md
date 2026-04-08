## ADDED Requirements

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
