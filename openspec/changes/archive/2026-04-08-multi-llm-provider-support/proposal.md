# Proposal: Multi-LLM Provider Support

## Objective
Extend the Visual Multi-Agent Team Builder to support a diverse range of Large Language Model (LLM) providers, including OpenAI, Google Gemini, Anthropic Claude, and local models via Ollama or LMStudio.

## Motivation
Currently, the system has basic support tied primarily to a generic provider structure. To make the platform more robust and accessible, users should be able to:
1.  **Reduce costs** by using cheaper models for specific tasks.
2.  **Increase privacy** by using local models (Ollama/LMStudio) for sensitive data.
3.  **Leverage specific strengths** of different providers (e.g., Gemini's large context window, Claude's reasoning capabilities).

## Capabilities
- **Provider Selection**: A dropdown in the LLM Node to select from OpenAI, Gemini, Claude, Ollama, and LMStudio.
- **Model Configuration**: Dynamic model selection strings for each provider.
- **Local Model Integration**: Support for custom base URLs for local providers (Ollama/LMStudio) to allow connecting to standard OpenAI-compatible endpoints.
- **Standardized Configuration**: A unified LLM configuration object that flows from frontend to backend.

## Impact
- **Frontend**: Update `LLMNode` component in the visual editor to include provider selection and base URL fields.
- **Backend**: 
    - Update `backend/core/compiler.py` to handle the new LLM configuration fields.
    - Prepare the integration layer for different Agno model classes (OpenAI, Gemini, Claude, etc.).
- **Data Model**: Update the stored graph nodes to include `provider` and `baseUrl` in `llmNode` data.
