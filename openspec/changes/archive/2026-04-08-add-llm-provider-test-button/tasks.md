## 1. Backend Provider Validation API

- [x] 1.1 Add request/response schemas for provider validation payload and normalized result.
- [x] 1.2 Implement provider-specific validation helpers (openai, anthropic, google, openrouter, local) using lightweight checks.
- [x] 1.3 Add `POST /api/llm/test-provider` endpoint that returns `{ ok, message }` and handles validation errors safely.

## 2. Frontend LLM Properties Integration

- [x] 2.1 Add frontend API client method for provider validation endpoint.
- [x] 2.2 Add `Test Provider` button in `LLM Properties` that sends current provider config and manages loading state.
- [x] 2.3 Render inline validation feedback (success/error) in LLM Properties and clear stale results on provider/config edits.

## 3. Verification

- [x] 3.1 Run backend checks (at least import/runtime smoke via FastAPI app startup).
- [x] 3.2 Run frontend build to verify TypeScript compile and UI integration.
