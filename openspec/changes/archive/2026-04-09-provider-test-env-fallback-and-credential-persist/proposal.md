## Why

Provider testing still depends mostly on manually typed API keys and does not consistently use provider-specific environment fallbacks. This creates friction in staging/production and prevents a smooth credential lifecycle where successful validations become durable secure credentials for that node.

## What Changes

- Update Test Provider behavior so empty API Key input falls back to provider-specific key from backend environment variables
- Define precedence for provider tests: explicit API Key in LLM Properties overrides environment fallback
- Persist tested provider keys securely on successful validation, creating or updating credential references for the tested node
- Ensure repeated Test Provider executions on the same node update the stored credential to the latest successfully validated key
- Keep secure storage guarantees (encrypted at rest, no plaintext key in graph payload or API response)

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `llm-provider-guidance`: Extend provider validation contract with env-fallback and explicit precedence semantics for all supported keyed providers
- `secret-protection`: Change validation credential lifecycle so successful explicit/env-backed provider tests persist or rotate secure credentials per node

## Impact

- **Backend**: `backend/routes/teams.py`, `backend/core/provider_validation.py`, `backend/core/credentials.py`, `backend/core/security.py`, `backend/models/schemas.py`
- **Frontend**: `frontend/src/components/PropertiesPanel.tsx`, `frontend/src/api/client.ts`, and node state handling for `credentialRef` updates after test success
- **Operations**: provider-specific environment keys must be documented and available in non-dev runtimes
- **Tests**: add/adjust backend tests for fallback precedence and credential persistence/rotation on provider test success
