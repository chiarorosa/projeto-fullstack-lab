## 1. Access Control and Abuse Protection

- [x] 1.1 Add bearer-token authentication dependency/middleware and apply it to `/execute`, `/api/llm/test-provider`, and protected `/api/teams` routes
- [x] 1.2 Add configurable rate limiting for `/execute` and `/api/llm/test-provider` with deterministic `429` behavior
- [x] 1.3 Externalize CORS/auth/rate-limit settings to environment configuration and add startup validation for non-dev modes

## 2. Credential Security Lifecycle

- [x] 2.1 Add secure credential storage model and migration for encrypted provider secrets
- [x] 2.2 Implement encryption/decryption utility using application key from environment
- [x] 2.3 Update team save/update flows to convert raw `apiKey` into `credentialRef` and avoid persisting plaintext secrets
- [x] 2.4 Add migration for legacy team graphs containing raw provider keys to move them into credential storage

## 3. Validation and Runtime Secret Resolution

- [x] 3.1 Update provider validation endpoint to accept `credentialRef` and optional ephemeral `apiKey` mode
- [x] 3.2 Resolve provider secrets at runtime boundary for validation and execution without exposing plaintext in persisted graph payloads
- [x] 3.3 Enforce non-persistence rule for ephemeral validation keys

## 4. Redaction and Frontend Integration

- [x] 4.1 Add centralized redaction utility and apply it to logs, errors, API responses, and SSE execution events
- [x] 4.2 Update frontend LLM properties/client flows to use masked secret UX and `credentialRef`-based interactions
- [x] 4.3 Replace hardcoded frontend API base URL with environment-driven configuration

## 5. Verification and Rollout Readiness

- [x] 5.1 Add tests for auth enforcement and rate limiting on sensitive endpoints
- [x] 5.2 Add tests for secret persistence rules, legacy migration behavior, and validation redaction
- [x] 5.3 Document security environment variables, key provisioning, and rollback/feature-flag procedure
