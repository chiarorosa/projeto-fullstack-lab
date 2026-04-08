## Context

O sistema atual tem uma lista mista de modelos e providers no menu lateral, o que causa confusão. O menu mostra modelos como "GPT-4o", "Claude 3.5 Sonnet", "Gemini 1.5 Pro" sem uma organização clara por provider.

O objetivo é simplificar para 5 providers pre-definidos: OpenAI, Anthropic, Google, Local (Ollama), OpenCode. A configuração detalhada (modelo, API key, base URL) será feita no LLM Properties Panel.

## Goals / Non-Goals

**Goals:**
- Simplificar seleção de provider no menu do LLM Node para 5 opções claras
- Redesenhar o LLM Properties Panel com campos contextuais por provider
- Garantir integração funcional com o backend (compiler.py)
- Exibir provider de forma clara no LLMNode visual

**Non-Goals:**
- Modelos específicos default por provider (usuário pode digitar qualquer um)
- Validação de modelos (aceita qualquer string de modelo)
- Cache de modelos populares

## Decisions

1. **Provider Labels Simplificados**: Usar nomes simples (OpenAI, Anthropic, Google, Local, OpenCode) em vez de nomes completos de produtos
   - Rationale: Mais conciso e fácil de identificar rapidamente
   - Alternative: Nomes completos (Anthropic Claude) - rejeitado por ser mais longo

2. **Modelo como Input Livre**: Campo de texto livre para modelo em vez de dropdown fixo
   - Rationale: Permite flexibilidade para novos modelos sem atualizar código
   - Alternative: Dropdown com modelos populares - rejeitado, voltaria ao problema original

3. **Campos Contextuais por Provider**: Mostrar/ocultar campos baseado no provider selecionado
   - Rationale: UI mais limpa, só mostra o que é relevante
   - Alternative: Mostrar todos os campos sempre - rejeitado polui a interface

4. **Local 含 Ollama e LMStudio**: Provider "Local" cobre tanto Ollama quanto LMStudio (ambos usam protocolo OpenAI compatível)
   - Rationale: Simplifica, ambos usam mesmo padrão técnico
   - Alternative: Providers separados - rejeitado, manutenção redundante

## Risks / Trade-offs

- [Risk] Usuário não sabe qual modelo usar → Mitigation: Adicionar placeholder contextual por provider (e.g., "gpt-4o" for OpenAI, "claude-3-5-sonnet" for Anthropic)
- [Risk] Quebra de compatibilidade com graphs antigos → Mitigation: Manter campo provider como string, fallback para "openai" se vazio
- [Risk] API key errada para provider → Mitigation: Tooltip indicando variável de ambiente esperada por provider