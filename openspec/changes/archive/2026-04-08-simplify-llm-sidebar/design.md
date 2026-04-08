## Context

O SidebarPalette atual mostra múltiplos modelos de LLM como itens separados:
- GPT-4o
- GPT-4o Mini
- Claude Sonnet
- Gemini Pro
- LLaMA 3.1

Cada um é um item clicável separado que cria um llmNode pré-configurado. Porém, o Properties Panel do LLM Node já permite alterar o provider e modelo livremente, tornando essa pré-configuração redundante.

## Goals / Non-Goals

**Goals:**
- Simplificar o menu lateral para uma única opção "LLM Node"
- Manter toda a funcionalidade do Properties Panel (provider selection, model input, API key, etc.)
- Melhorar a experiência do usuário evitando confusão

**Non-Goals:**
- Alterar o comportamento do LLM Properties Panel
- Alterar a forma como o LLM Node é renderizado no canvas
- Modificar o backend (compiler)

## Decisions

1. **Uma única opção no sidebar**: Em vez de múltiplos modelos, criar apenas "LLM Node"
   - Rationale: Usuário escolhe provider/model no Properties Panel, não precisa de pré-configurações no menu
   - Alternative: Manter lista de modelos - rejeitado, causa confusão e é redundante

2. **Label simples**: Usar "LLM" como label da categoria e do nó
   - Rationale: Mais limpo e consistente com "Agent" e "Tool"
   - Alternative: "Language Models" - rejeitado, longo demais

3. **Dados default**: O nó criado terá provider "openai" como default (mantém backward compatibility)
   - Rationale: Sem quebra para users que já usam o sistema

## Risks / Trade-offs

- [Risk] Usuário não sabe que pode mudar o provider → Mitigation: O Properties Panel já mostra isso claramente
- [Risk] Graphs existentes com modelo específico → Mitigation: O nó lê dados do graph, não precisa de mudança