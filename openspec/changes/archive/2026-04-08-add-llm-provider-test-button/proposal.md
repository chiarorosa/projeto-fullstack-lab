## Why

Today users only discover whether a provider API key works when they run the full team execution flow. This slows down setup and makes provider configuration in LLM Properties harder to verify.

## What Changes

- Add a provider test action in `LLM Properties` to validate the currently selected provider configuration without running the team.
- Add a backend endpoint that performs a lightweight provider connectivity/credential check per provider.
- Show clear success/error feedback in the properties panel for fast troubleshooting.

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `llm-provider-guidance`: extend LLM Properties guidance with an explicit provider validation action and result feedback.

## Impact

- **Frontend**: `PropertiesPanel` gains a `Test Provider` button and validation status messaging.
- **Backend**: new LLM validation endpoint and provider-specific validation logic.
- **UX**: users can confirm provider readiness before executing any workflow.
