# Design: Multi-LLM Provider Support

## Technical Overview
The implementation involves updating the `LLMNode` in the frontend to capture provider-specific information and updating the backend compiler to parse and transport this configuration to the execution engine.

## Frontend Architecture
### 1. LLMNode Component Update
- **Location**: `frontend/src/components/nodes/LLMNode.tsx`
- **Changes**:
    - Add a `provider` state/field to the node data.
    - Implement a selection interface for providers: `OpenAI`, `Google Gemini`, `Anthropic Claude`, `Ollama`, `LMStudio`.
    - Add a conditional input field for `baseUrl`, visible only when `Ollama` or `LMStudio` is selected.
    - Standardize the `data` object sent to the backend to include `provider` and `baseUrl`.

### 2. Node Data Interface
```typescript
interface LLMNodeData {
  provider: 'openai' | 'google' | 'anthropic' | 'ollama' | 'lmstudio';
  model: string;
  apiKey: string;
  baseUrl?: string;
}
```

## Backend Architecture
### 1. Compiler Update
- **Location**: `backend/core/compiler.py`
- **Changes**:
    - Update `_build_agent_config` to extract `provider` and `baseUrl` from the `llm_nodes` data.
    - Default the provider to `openai` for backward compatibility.
    - Ensure the compiled config object includes these new fields so the orchestrator can use them.

### 2. Execution Logic (Future Integration)
- The execution engine (Agno integration) will use the `provider` field to select the appropriate model class:
    - `openai` -> `OpenAIChat`
    - `google` -> `Gemini`
    - `anthropic` -> `Claude`
    - `ollama`/`lmstudio` -> `OpenAIChat` with custom `base_url` (OpenAI compatible).

## Data Flow
1.  **UI**: User selects provider and enters model details in `LLMNode`.
2.  **State**: ReactFlow state updates with the new node data.
3.  **Transmission**: The graph JSON is sent to the backend.
4.  **Compilation**: `compiler.py` converts the node data into an internal execution format.
5.  **Execution**: The orchestrator instantiates the vendor-specific client using the provided configuration.

## Risks / Trade-offs
- **API Consistency**: We will start with a standardized configuration object that covers the core needs (model, key, url) and can be extended later for provider-specific parameters like `temperature` or `max_tokens`.
- **Local Connectivity**: Backend requires access to local model endpoints (e.g., `http://localhost:11434/v1` for Ollama).
