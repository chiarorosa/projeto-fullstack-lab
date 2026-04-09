## MODIFIED Requirements

### Requirement: Provider Credentials Shall Not Be Persisted in Graph Payloads
The system SHALL prevent raw provider API keys from being stored in persisted team graph JSON.

#### Scenario: Team graph save includes raw API key fields
- **WHEN** a save or update operation receives LLM node data containing raw `apiKey`
- **THEN** the backend stores the secret in secure credential storage
- **AND** persisted graph payload replaces raw secret fields with a `credentialRef`

#### Scenario: Existing persisted graph contains raw API key
- **WHEN** migration processes legacy team records with raw provider keys
- **THEN** each key is moved to secure credential storage
- **AND** the graph payload is rewritten to use `credentialRef`

### Requirement: Stored Credentials Shall Be Encrypted At Rest
The system SHALL encrypt provider credentials before database persistence and decrypt only at runtime boundary where needed.

#### Scenario: Credential is written to storage
- **WHEN** backend persists provider credential material
- **THEN** the stored value is encrypted using configured application encryption key

#### Scenario: Provider execution needs credential
- **WHEN** runtime resolves provider credentials for execution or validation
- **THEN** backend decrypts credential in memory for the active request scope only

### Requirement: Secret Data Shall Be Redacted From Responses and Telemetry
The system SHALL redact secret material from API responses, execution stream events, logs, and error payloads.

#### Scenario: Provider validation response is returned
- **WHEN** provider validation completes
- **THEN** response includes status and guidance without exposing raw API key or decrypted credential content

#### Scenario: Execution emits events or errors
- **WHEN** backend emits SSE events or logs errors during execution
- **THEN** secret fields are redacted before emission

### Requirement: Validation Supports Secure Credential References
The system SHALL allow provider validation using a secure credential reference and MAY allow ephemeral key validation without persistence.

#### Scenario: Validation with credential reference
- **WHEN** validation request contains `credentialRef`
- **THEN** backend resolves referenced secret securely and performs provider connectivity validation

#### Scenario: Validation with explicit key persists on success
- **WHEN** validation request contains one-time `apiKey` input and keyed-provider validation succeeds
- **THEN** backend persists that key as encrypted credential material for the tested node
- **AND** backend returns or updates node `credentialRef` accordingly

#### Scenario: Validation with env fallback persists on success
- **WHEN** validation request does not contain explicit `apiKey`
- **AND** backend resolves provider key from environment fallback
- **AND** keyed-provider validation succeeds for a tested node
- **THEN** backend persists the effective fallback key as encrypted credential material for the node

#### Scenario: Failed validation does not mutate stored credential
- **WHEN** provider validation fails for explicit, credential-ref, or env-fallback key sources
- **THEN** backend does not create or update credential material for that node
