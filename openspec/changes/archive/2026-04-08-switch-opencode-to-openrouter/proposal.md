## Why

Users currently need to remember provider-specific details (default API URL, expected model format, and model reference pages) when configuring LLM nodes. This creates friction and setup mistakes, especially when switching between OpenRouter, Local, OpenAI, Anthropic, and Gemini providers.

## What Changes

- Add provider-specific guidance in LLM Properties with preconfigured metadata (default base URL and environment variable hints)
- Expose quick links to official model reference pages for OpenAI, Anthropic, Gemini, OpenRouter, and local model catalogs
- Keep backward compatibility for legacy `opencode` provider values by treating them as `openrouter` in the UI

## Capabilities

### New Capabilities
- `llm-provider-guidance`: LLM Properties shows provider defaults and model reference links so users can configure nodes faster with fewer mistakes

### Modified Capabilities
- None

## Impact

- **Frontend**: `PropertiesPanel` adds provider metadata display and model documentation links
- **UX**: Better discoverability of provider defaults and accepted model sources
- **Compatibility**: Existing graphs using `opencode` continue to behave as `openrouter`
