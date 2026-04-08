# Tasks: LLM Provider Refactor

## 1. Frontend - Type Definitions

- [x] 1.1 Update `frontend/src/store/canvasStore.ts` LLMData interface with new provider types ('openai', 'anthropic', 'google', 'local', 'opencode')

## 2. Frontend - Properties Panel Updates

- [x] 2.1 Simplify PROVIDERS array to 5 options: OpenAI, Anthropic, Google, Local, OpenCode
- [x] 2.2 Add model placeholders per provider in LLMForm
- [x] 2.3 Add contextual field rendering based on provider type
- [x] 2.4 For Local provider: show Base URL field instead of API Key
- [x] 2.5 Add helpful tooltips per provider with default values

## 3. Frontend - LLMNode Visual Update

- [x] 3.1 Update PROVIDER_COLORS in LLMNode.tsx to include 'local' and 'opencode'
- [x] 3.2 Update LLMNode subtitle to show provider label (e.g., "Local" instead of "ollama")

## 4. Backend - Compiler Updates

- [x] 4.1 Update compiler.py to handle new provider values ('local', 'opencode')
- [x] 4.2 Ensure backward compatibility with existing 'openai', 'anthropic', 'google', 'ollama' values
- [x] 4.3 Map 'local' provider to appropriate execution handler

## 5. Testing and Verification

- [x] 5.1 Test provider selection UI in the Properties Panel
- [x] 5.2 Verify conditional fields work correctly per provider
- [x] 5.3 Test graph compilation with different providers
- [x] 5.4 Verify LLMNode displays correct provider name and color