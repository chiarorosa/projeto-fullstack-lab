## Why

The previous change targeted OpenCode.ai, but the intended provider is OpenRouter.ai. We need to correct the integration target so the application uses the unified LLM interface from OpenRouter and keeps provider access consistent through a single API.

## What Changes

- Replace OpenCode.ai references with OpenRouter.ai in the integration scope and artifacts
- Add/update backend OpenAI-compatible endpoint integration for OpenRouter (`https://openrouter.ai/api/v1`)
- Keep the tool-based execution path but rename behavior, labels, and environment configuration to OpenRouter
- Ensure error handling and execution results continue to flow through the existing agent pipeline

## Capabilities

### New Capabilities
- `openrouter-ai-tool`: A tool type that allows agents to call OpenRouter.ai for code analysis, generation, and debugging tasks through a unified LLM interface

### Modified Capabilities
- `llm-provider-unified`: Include OpenRouter as a functional provider path where applicable in provider-driven flows

## Impact

- **Frontend**: Update tool labels and options from OpenCode to OpenRouter where exposed
- **Backend**: Update tool execution handler and environment variable contract to OpenRouter
- **Dependencies**: Reuse existing HTTP client (`httpx`) with OpenAI-compatible request format for OpenRouter
