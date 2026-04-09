## Why

Before adding new features, the platform needs a minimum security baseline to reduce unauthorized usage, prevent credential leakage, and control costly execution abuse. Addressing this now avoids compounding risk as the product surface grows.

## What Changes

- Add baseline API access control for sensitive endpoints (execution, provider validation, and team mutation routes)
- Add rate limiting for high-cost endpoints to reduce abuse and accidental overuse
- Remove plaintext provider API keys from persisted graph payloads and replace with credential references
- Introduce secure credential storage and runtime-only secret resolution for provider calls
- Redact secrets from API responses, SSE events, logs, and error payloads
- Move CORS and client API base URL behavior to environment-driven configuration with safe defaults

## Capabilities

### New Capabilities
- `api-access-control`: Enforce authenticated access and request throttling for sensitive backend routes
- `secret-protection`: Ensure provider credentials are stored, retrieved, and exposed using a secure lifecycle

### Modified Capabilities
- `llm-provider-guidance`: Update provider validation behavior to work with secret references and enforce secure validation semantics

## Impact

- **Backend**: `backend/main.py`, `backend/routes/teams.py`, `backend/core/compiler.py`, `backend/core/llm_runtime.py`, and database models/migrations for credential storage
- **Frontend**: `frontend/src/api/client.ts` and `frontend/src/components/PropertiesPanel.tsx` for auth header propagation, masked secret UX, and validation flow updates
- **Persistence**: Team graph payload format changes from raw provider secrets to secret references
- **Operations**: New required/optional security environment variables (token auth, encryption key, CORS allowlist, rate limit settings)
