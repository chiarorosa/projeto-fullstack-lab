## MODIFIED Requirements

### Requirement: LLM Provider Validation Action
The system SHALL provide a direct provider validation action in LLM Properties so users can verify provider credentials/connectivity without running team execution.

#### Scenario: User validates configured provider from LLM Properties
- **WHEN** user clicks `Test Provider` in LLM Properties for a selected LLM node
- **THEN** the client sends provider settings for that node to a backend validation endpoint
- **AND** the UI shows loading state while validation is in progress

#### Scenario: Empty API key input uses provider environment fallback
- **WHEN** provider is `openai`, `openrouter`, `opencode`, `anthropic`, or `google`
- **AND** the validation request does not include a non-empty `apiKey`
- **THEN** backend resolves provider-specific API key from runtime environment variables
- **AND** backend uses that resolved key to execute validation

#### Scenario: Explicit API key input overrides fallback sources
- **WHEN** validation request includes a non-empty `apiKey`
- **THEN** backend MUST validate using that explicit key for the request
- **AND** backend MUST NOT replace that value with environment fallback during validation

#### Scenario: Validation succeeds
- **WHEN** backend confirms provider credentials/connectivity
- **THEN** the UI shows a success status/message in LLM Properties
- **AND** response may include updated `credentialRef` for the tested node when persistence context is provided

#### Scenario: Validation fails
- **WHEN** backend cannot validate provider credentials/connectivity
- **THEN** the UI shows an error status/message with actionable guidance

### Requirement: Provider-Specific Validation Endpoint
The backend SHALL validate provider settings based on provider type and return a normalized validation result.

#### Scenario: Backend validates cloud provider key
- **WHEN** provider is `openai`, `anthropic`, `google`, `openrouter`, or `opencode`
- **THEN** backend performs a lightweight provider API check using the effective key and optional base URL
- **AND** backend returns a normalized JSON response with `ok` boolean and `message`

#### Scenario: Backend validates local provider endpoint
- **WHEN** provider is `local`
- **THEN** backend performs a lightweight reachability check on supplied or default local base URL
- **AND** backend returns a normalized JSON response with `ok` boolean and `message`

#### Scenario: Validation key resolution follows deterministic precedence
- **WHEN** provider requires key-based validation
- **THEN** backend resolves effective key with precedence: explicit `apiKey` > node `credentialRef` > provider environment variable
- **AND** backend returns actionable error when no effective key is available

#### Scenario: Successful validation persists credential for node context
- **WHEN** keyed provider validation succeeds and request contains node persistence context
- **THEN** backend stores the effective key in secure credential storage
- **AND** backend updates the tested node to reference the resulting `credentialRef`

#### Scenario: Re-running validation rotates stored node credential
- **WHEN** the same node executes `Test Provider` again and validation succeeds with a different effective key
- **THEN** backend updates the node-linked credential material to the latest successfully validated key
- **AND** subsequent validation/execution for that node uses the updated credential

#### Scenario: Validation response redacts secret data
- **WHEN** validation result is returned to client
- **THEN** response contains normalized status and guidance only
- **AND** response does not expose raw secret values or decrypted credential contents
