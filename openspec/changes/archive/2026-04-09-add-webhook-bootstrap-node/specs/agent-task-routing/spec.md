## MODIFIED Requirements

### Requirement: Task Node Bootstrap
The system SHALL require at least one valid supported bootstrap source for execution input and task dispatch.

#### Scenario: Execution starts with valid Task Node
- **WHEN** the graph contains a Task Node with at least one task item
- **THEN** the backend uses Task Node payload as the source for execution input
- **AND** execution can dispatch tasks to downstream agent flow

#### Scenario: Execution starts with valid Webhook Node
- **WHEN** the graph contains a Webhook Node registered as a valid bootstrap source
- **THEN** the backend can start execution from webhook payload mapped into task input context
- **AND** execution can dispatch tasks to downstream agent flow

#### Scenario: Execution requested without valid bootstrap source
- **WHEN** the graph does not contain a valid Task Node or valid Webhook Node bootstrap source
- **THEN** the system returns an explicit validation error indicating at least one supported bootstrap source is required
