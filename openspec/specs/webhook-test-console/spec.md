# webhook-test-console Specification

## Purpose
TBD - created by archiving change add-in-app-webhook-test-console. Update Purpose after archive.
## Requirements
### Requirement: In-App Webhook Request Composer
The system SHALL provide an in-app webhook test console that allows users to compose and send webhook requests for a configured Webhook Node.

#### Scenario: User opens webhook test console from a configured Webhook Node
- **WHEN** a user selects a Webhook Node with a valid trigger identifier
- **THEN** the system displays a webhook test console prefilled with the node endpoint and POST method
- **AND** the user can edit headers and JSON body before sending

#### Scenario: User attempts to send invalid JSON body
- **WHEN** the user enters malformed JSON and triggers send
- **THEN** the system blocks request submission
- **AND** the system shows a validation message describing the JSON parsing error

### Requirement: Structured Request and Response Inspection
The system SHALL display structured request and response diagnostics for each webhook test call.

#### Scenario: Webhook test request is accepted
- **WHEN** the user sends a valid test request and backend accepts it
- **THEN** the system displays status code, response headers, response body, and measured latency
- **AND** the response view includes execution reference metadata returned by backend

#### Scenario: Webhook test request fails transport or server validation
- **WHEN** the request cannot be completed or backend returns an error
- **THEN** the system displays the failure status and error payload/message
- **AND** previously entered request inputs remain available for retry

### Requirement: Webhook Test Presets Per Node
The system SHALL allow users to reuse request presets associated with a Webhook Node.

#### Scenario: User saves and reuses a preset
- **WHEN** the user saves a request payload/headers preset for a Webhook Node
- **THEN** the preset is available for subsequent test sessions for that node
- **AND** loading the preset repopulates the console fields before send

#### Scenario: User regenerates webhook trigger identifier
- **WHEN** the user regenerates a Webhook Node trigger identifier
- **THEN** the console updates to the new endpoint automatically
- **AND** sending uses the latest endpoint bound to that node

