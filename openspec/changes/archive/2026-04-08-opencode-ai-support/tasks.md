# Tasks: OpenRouter AI Support

## 1. Frontend Tool Type Addition

- [x] 1.1 Replace `opencode_ai` with `openrouter_ai` in `frontend/src/components/PropertiesPanel.tsx`
- [x] 1.2 Update tool display label from "OpenCode AI" to "OpenRouter AI"

## 2. Backend Tool Execution Handler

- [x] 2.1 Rename OpenCode execution handler to OpenRouter-oriented naming in `backend/core/compiler.py`
- [x] 2.2 Update default base URL to `https://openrouter.ai/api/v1`
- [x] 2.3 Replace environment keys from `OPENCODE_*` to `OPENROUTER_*`
- [x] 2.4 Keep robust error handling for missing API key, timeout, and HTTP failures

## 3. Tool Execution Integration

- [x] 3.1 Wire tool execution branch to `openrouter_ai` tool type in agent flow
- [x] 3.2 Ensure tool results continue to be emitted and injected into agent context

## 4. Testing and Verification

- [x] 4.1 Verify "OpenRouter AI" appears in tool type dropdown
- [x] 4.2 Verify a sample workflow calls OpenRouter and returns output to the agent
- [x] 4.3 Verify missing `OPENROUTER_API_KEY` path returns clear error
