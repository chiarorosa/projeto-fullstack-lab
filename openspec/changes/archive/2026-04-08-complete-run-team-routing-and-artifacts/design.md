## Context

Com o `Task Node` introduzido, o fluxo já suporta entrada de tarefa única/lote e persistência de runs, mas a execução ainda não realiza seleção inteligente do agente mais adequado nem usa o perfil do agente (`goal`/`backstory`) como critério decisório real. Também há lacunas de UX para indicar conectividade entre nós e status de elegibilidade de agentes sem LLM.

O objetivo desta mudança é fechar o ciclo do `Run Team` para comportamento end-to-end: roteamento inteligente por tarefa, execução via LLM conectada ao agente escolhido, feedback visual de conectividade/validação e aba de artefatos consolidada no frontend.

## Goals / Non-Goals

**Goals:**
- Selecionar agente mais adequado por tarefa com base em `goal`/`backstory`
- Executar tarefa com a LLM conectada ao agente selecionado
- Exibir claramente conexões e elegibilidade de nós no canvas/properties
- Bloquear/alertar agentes sem LLM ligado (não executáveis)
- Disponibilizar aba de artefatos da run com detalhes de roteamento e resultados

**Non-Goals:**
- Suportar colaboração multiusuário em tempo real
- Implementar política avançada de custo/latência por provedor nesta etapa
- Introduzir versionamento completo de prompts por agente

## Decisions

1. **Roteador semântico dedicado no backend**
   - Implementar módulo de roteamento que, para cada task, compara tarefa com perfil de cada agente elegível.
   - Estratégia inicial: prompt de ranking estruturado para um "router LLM" (ou fallback heurístico lexical quando indisponível).
   - Resultado deve retornar `selected_agent_id`, `score`, `reason` e candidatos avaliados.
   - Rationale: separa decisão de roteamento da execução e mantém extensibilidade.

2. **Execução por agente selecionado com LLM conectada**
   - Para cada tarefa, apenas um agente principal executa (com opcional de handoff futuro).
   - O executor usa explicitamente provider/model/base_url/api_key do LLM node ligado ao agente.
   - Rationale: cumpre requisito de "cérebro do agente = LLM conectada".

3. **Contrato de eventos de execução enriquecido**
   - Incluir eventos com `routing_decision`, `selected_agent`, `ineligible_agents` e estado da tarefa.
   - Persistência de run deve armazenar decisão e saída final por item.
   - Rationale: observabilidade e auditoria pós-execução.

4. **Validação e indicação visual de conectividade**
   - Canvas deve mostrar badges/estados por nó:
     - Agent sem LLM: `Not executable`
     - Agent com LLM: `Ready`
     - Task sem agentes downstream: aviso de rota incompleta
   - Rationale: reduzir erro de configuração antes de executar.

5. **Aba de artefatos dedicada**
   - Criar workspace/tab com lista de runs e detalhes por tarefa:
     - input, agente selecionado, justificativa de roteamento, output final, status/erro, timestamp.
   - Rationale: substituir inspeção apenas via logs efêmeros.

## Risks / Trade-offs

- [Risk] LLM de roteamento pode gerar decisão inconsistente → Mitigation: resposta estruturada, validação de schema e fallback determinístico.
- [Risk] Aumento de latência por tarefa (rotear + executar) → Mitigation: cache de perfil de agente e opção de lote sequencial otimizada.
- [Risk] Erros de provider podem interromper execução parcial → Mitigation: captura por tarefa, persistência de erro e continuidade do lote.
- [Risk] Complexidade de UX no canvas → Mitigation: estados visuais simples (`Ready`, `Not executable`, `Missing route`) e tooltips objetivos.
