## Why

O menu lateral de modelos de linguagem (LLM) atualmente mistura providers e modelos numa lista extensa e confusa. O objetivo é simplificar a seleção de providers para opções pre-definidas (OpenAI, Anthropic, Google, Local, OpenCode) e mover a configuração detalhada para o painel de propriedades, garantindo que a seleção seja funcional em toda a aplicação.

## What Changes

- Simplificar a seleção de provider no LLM Node para 5 opções pre-definidas: OpenAI, Anthropic, Google, Local (Ollama), OpenCode
- Remover a lista extensa de modelos do menu lateral
- Expandir o LLM Properties Panel com campos específicos por provider
- Garantir integração funcional com o backend (compiler.py)
- Atualizar o LLMNode visual para exibir o provider de forma clara

## Capabilities

### New Capabilities
- `llm-provider-unified`: Sistema unificado de providers com configuração contextual por tipo

### Modified Capabilities
- `multi-llm-provider-support`: Atualizar para usar o novo sistema de providers unificado

## Impact

- **Frontend**: Redesenho do LLMNode e PropertiesPanel para o novo modelo de providers
- **Backend**: Atualização no compiler.py para reconhecer novos tipos de provider
- **Store**: Atualização do canvasStore.ts para novos tipos de dados