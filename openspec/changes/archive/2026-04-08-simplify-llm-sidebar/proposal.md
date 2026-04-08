## Why

O painel lateral (Sidebar Palette) currently mostra uma lista extensa de modelos individuais sob a categoria "Language Models" (GPT-4o, GPT-4o Mini, Claude Sonnet, etc.). Isso é redundante porque quando o usuário clica no nó, o Properties Panel permite selecionar qualquer provider e modelo. O objetivo é simplificar para apenas uma opção "LLM Node" no menu lateral.

## What Changes

- Substituir a lista de modelos individuais (GPT-4o, Claude Sonnet, etc.) por uma única opção "LLM Node" no Sidebar Palette
- Remover a categoria "Language Models" ou renomear para "LLM"
- Manter o comportamento do LLM Node unchanged (Properties Panel com provider selection)

## Capabilities

### New Capabilities
- `llm-node-simplified`: Nova opção única de LLM no sidebar

### Modified Capabilities
- `llm-provider-unified`: Atualização para usar o nó simplificado

## Impact

- **Frontend**: Update em `frontend/src/components/SidebarPalette.tsx` para usar apenas uma opção de LLM Node