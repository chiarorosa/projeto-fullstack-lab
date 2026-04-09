## MODIFIED Requirements

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

#### Scenario: Backend validates provider using credential reference
- **WHEN** validation request includes `credentialRef` for a selected provider
- **THEN** backend resolves secret from secure credential storage
- **AND** backend performs provider validation without requiring raw secret in persisted graph payload

#### Scenario: Ephemeral validation key is not persisted
- **WHEN** validation request includes one-time `apiKey` input for immediate validation
- **THEN** backend validates connectivity for that request
- **AND** backend does not persist the ephemeral key into team graph data

#### Scenario: Validation response redacts secret data
- **WHEN** validation result is returned to client
- **THEN** response contains normalized status and guidance only
- **AND** response does not expose raw secret values or decrypted credential contents
