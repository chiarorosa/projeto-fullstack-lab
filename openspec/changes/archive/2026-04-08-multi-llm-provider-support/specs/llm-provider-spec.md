# Specification: LLM Provider Configuration

## Added Requirements

### Requirement: Provider Selection
The system must allow users to specify which LLM provider they want to use for a given agent configuration.

- **GIVEN** the user is viewing an `LLMNode` in the visual editor
- **WHEN** the user opens the provider dropdown
- **THEN** they should see options for `OpenAI`, `Google Gemini`, `Anthropic Claude`, `Ollama`, and `LMStudio`

### Requirement: Conditional Base URL for Local Models
To support local models like Ollama or LMStudio, the system must allow providing a custom API base URL.

- **GIVEN** the user has selected `Ollama` or `LMStudio` as the provider
- **WHEN** the node is rendered
- **THEN** an input field for "Base URL" should be visible
- **AND** it should be saved in the node data as `baseUrl`

### Requirement: Backend Propagation
The LLM configuration must be correctly propagated from the frontend graph to the backend execution plan.

- **GIVEN** a graph JSON contains an `llmNode` with `provider: "google"` and `model: "gemini-1.5-pro"`
- **WHEN** `compile_graph` is called
- **THEN** the resulting agent configuration for connected agents should include `llm: { provider: "google", model: "gemini-1.5-pro", ... }`

## User Experience
- The provider selection should be prominent within the `LLMNode`.
- Switching providers should not clear the API key or model name fields if they are still relevant.
- Tooltips should explain what "Base URL" is for (e.g., "Ollama default: http://localhost:11434/v1").
