## Context

Atualmente o backend compila o grafo e executa todos os agentes em ordem topológica para uma única entrada. Isso não diferencia execução por tarefa em lote, nem aplica regra forte de ativação baseada em conexão LLM. Também não existe um nó dedicado de tarefa como origem explícita da execução no canvas.

O requisito introduz roteamento de tarefas (single/batch) para ativar somente agentes elegíveis por tarefa, e adiciona um `Task Node` como bootstrap da aplicação, exigindo mudanças em API de execução, compilação e feedback de execução para frontend.

## Goals / Non-Goals

**Goals:**
- Permitir execução com tarefa única e lote de tarefas
- Introduzir `Task Node` como ponto inicial (bootstrap) do fluxo de execução
- Selecionar automaticamente agentes ativáveis por tarefa
- Exigir nó LLM conectado para que um agente seja considerado ativo
- Expor metadados de roteamento (ativados/ignorados + razão)

**Non-Goals:**
- Construir classificador semântico avançado de roteamento
- Alterar persistência de equipes no banco
- Redesenhar o editor visual de nós além do necessário para introdução do `Task Node` e visualização de resultado

## Decisions

1. **Contrato de execução com suporte a single/batch**
   - Expandir payload de execução para aceitar `task_input` (compatível) e `task_inputs` (lote).
   - Backend normaliza para lista interna de tarefas.
   - Rationale: mantém compatibilidade com fluxo atual e adiciona execução em lote sem endpoint novo.

2. **Elegibilidade de agente baseada em LLM conectado**
   - Durante compilação, marcar agente como elegível somente se `connectedLlm` existir e resolver para um nó LLM válido.
   - Agentes sem LLM entram em lista de ignorados com motivo explícito.
   - Rationale: evita ativação inválida e torna comportamento previsível.

3. **Roteamento determinístico por tarefa com regras simples**
   - Para primeira versão, ativar todos os agentes elegíveis para cada tarefa (com opção de extensão para filtros por metadata futura).
   - Ainda assim retornar estrutura de roteamento por tarefa (`activated_agents`, `skipped_agents`).
   - Rationale: entrega infraestrutura de roteamento e transparência sem bloquear em heurística complexa.

4. **Evento SSE enriquecido**
   - Incluir evento de início por tarefa com contexto de roteamento e manter eventos existentes de agente/output.
   - Rationale: frontend pode exibir claramente quais agentes participaram em cada item de lote.

5. **Task Node como origem obrigatória de execução**
   - Definir um novo tipo de nó (`taskNode`) para representar entradas de tarefa e lote.
   - Execução do time passa a iniciar a partir do `Task Node`; sem ele, execução deve falhar com mensagem orientativa.
   - Rationale: estabelece bootstrap explícito e prepara evolução para múltiplas estratégias de entrada.

## Risks / Trade-offs

- [Risk] Execução em lote aumenta duração total → Mitigation: processar tarefas sequencialmente com eventos por tarefa para observabilidade.
- [Risk] Usuário pode esperar roteamento inteligente desde já → Mitigation: documentar comportamento inicial (todos elegíveis) e preservar contrato para evoluir heurística depois.
- [Risk] Times com agentes sem LLM podem aparentar “quebrados” → Mitigation: retornar motivos explícitos em `skipped_agents` e orientar configuração no UI.
- [Risk] Grafos existentes sem Task Node podem não executar no novo fluxo → Mitigation: migração de compatibilidade (fallback temporário para `task_input` clássico) e aviso no frontend para adicionar Task Node.
