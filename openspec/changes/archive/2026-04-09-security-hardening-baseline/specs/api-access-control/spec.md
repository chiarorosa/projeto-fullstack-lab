## ADDED Requirements

### Requirement: Sensitive API Endpoints Require Authentication
The system SHALL require bearer-token authentication for sensitive endpoints that expose team data mutations, execution, or provider validation.

#### Scenario: Authenticated request to execution endpoint
- **WHEN** a client calls `/execute` with a valid bearer token
- **THEN** the backend authorizes the request and continues normal execution flow

#### Scenario: Unauthenticated request to sensitive endpoint
- **WHEN** a client calls `/execute`, `/api/llm/test-provider`, or protected `/api/teams` routes without a valid bearer token
- **THEN** the backend returns an authentication error response
- **AND** no downstream execution or mutation action is performed

### Requirement: Cost-Sensitive Endpoints Are Rate Limited
The system SHALL apply configurable rate limits to cost-sensitive endpoints to reduce abuse and accidental overuse.

#### Scenario: Request within configured limit
- **WHEN** a client sends requests to `/execute` or `/api/llm/test-provider` within configured rate thresholds
- **THEN** the backend processes requests normally

#### Scenario: Request exceeds configured limit
- **WHEN** a client exceeds configured request limits for `/execute` or `/api/llm/test-provider`
- **THEN** the backend returns `429 Too Many Requests`
- **AND** the response includes retry guidance metadata

### Requirement: Security Controls Are Environment Configurable
The system SHALL load access-control settings from environment configuration instead of hardcoded values.

#### Scenario: Server starts with security environment configured
- **WHEN** the backend initializes in an environment with auth, CORS, and rate-limit configuration
- **THEN** those values are applied at runtime for request validation and origin policy

#### Scenario: Required security configuration is missing
- **WHEN** backend startup detects missing required security configuration in a non-development mode
- **THEN** startup fails with an explicit configuration error
