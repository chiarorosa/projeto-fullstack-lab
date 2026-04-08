## Context

The current `LLM Properties` panel helps users choose provider/model and view guidance, but it does not let them validate whether credentials and endpoint settings are actually usable. Users only detect invalid API keys later during full team execution.

This change adds a focused validation path that checks the selected provider configuration immediately from the properties panel.

## Goals / Non-Goals

**Goals:**
- Provide a `Test Provider` action in `LLM Properties` for quick credential/connectivity validation
- Validate providers with lightweight backend checks that avoid running the full orchestration flow
- Return clear, actionable success/error messages to the UI

**Non-Goals:**
- Running full prompt completions as part of validation
- Persisting validation history in the database
- Reworking the existing team execution architecture

## Decisions

1. **Expose a dedicated backend validation endpoint**
   - Add `POST /api/llm/test-provider` that receives provider settings and returns `{ ok, message }`.
   - Rationale: keeps validation responsibility server-side, reuses server networking/security context, and avoids exposing additional provider mechanics in the client.

2. **Use provider-specific lightweight HTTP checks**
   - OpenAI / OpenRouter: call model listing endpoints with provided key/base URL.
   - Anthropic: call models endpoint with required headers.
   - Google: call Gemini models endpoint using `key` query parameter.
   - Local: call local models/tags endpoint on configured base URL without API key.
   - Rationale: checks credentials/connectivity with minimal token cost and fast response.

3. **Add inline feedback in LLM Properties**
   - Button triggers async call and shows loading, success, or error message in-panel.
   - Rationale: immediate UX feedback at the point of configuration.

## Risks / Trade-offs

- [Risk] Provider APIs may change endpoint behavior or auth requirements -> Mitigation: centralize validation logic in one backend helper and keep messages generic but actionable.
- [Risk] Local provider URL variations (with/without `/v1`) may fail -> Mitigation: normalize URL and try a tolerant local tags endpoint path.
- [Risk] Verbose raw upstream errors may leak unnecessary details -> Mitigation: sanitize error text before returning user-facing message.
