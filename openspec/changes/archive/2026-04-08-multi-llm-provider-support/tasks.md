# Tasks: Multi-LLM Provider Support

## 1. Type Definitions and Schema Updates

- [x] 1.1 Update frontend LLM node data interface to include `provider` and `baseUrl`.
- [x] 1.2 Update backend model types (if any) to accommodate additional LLM metadata.

## 2. Frontend Implementation

- [x] 2.1 Modify `frontend/src/components/nodes/LLMNode.tsx` to add a Provider Selection dropdown (OpenAI, Gemini, Claude, Ollama, LMStudio).
- [x] 2.2 Add conditional rendering logic for the `baseUrl` input field (visible only for local providers like Ollama or LMStudio).
- [x] 2.3 Ensure the `onChange` handlers correctly update the node data state for new fields.
- [x] 2.4 Add informative labels or tooltips to guide users on required fields (e.g., "Ollama Base URL").

## 3. Backend Implementation

- [x] 3.1 Update `backend/core/compiler.py` `_build_agent_config` function to extract `provider` and `baseUrl` from the input node data.
- [x] 3.2 Ensure compiled configuration objects sent to the execution engine contain the updated LLM metadata.

## 4. Testing and Verification

- [x] 4.1 Verify that the "Base URL" field toggles correctly based on provider selection in the UI.
- [x] 4.2 Create a sample graph with a Google Gemini node and verify the compiled execution plan reflects the provider change.
- [x] 4.3 Verify that OpenAI-compatible local endpoints (Ollama) work when a custom `baseUrl` is provided.
