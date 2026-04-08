## Why

Hoje a execução usa todos os agentes em sequência, mesmo quando a tarefa poderia ser tratada por apenas parte do time. Além disso, agentes sem nó LLM conectado ainda podem entrar no fluxo, o que gera execução inconsistente.

## What Changes

- Adicionar roteamento de tarefas para execução única ou em lote, selecionando apenas os agentes relevantes para cada tarefa.
- Definir elegibilidade de agente ativo: somente agentes com nó LLM conectado podem ser ativados para execução.
- Expor no resultado de execução quais agentes foram ativados, quais foram ignorados e o motivo.
- Criar um `Task Node` como bootstrap da aplicação para centralizar entrada de tarefas (single/batch) e acionar a execução do time.

## Capabilities

### New Capabilities
- `agent-task-routing`: roteamento de tarefas (single/batch) para subconjunto de agentes elegíveis, com ativação baseada em conexão LLM.
- `task-node-bootstrap`: nó de tarefa como ponto inicial obrigatório da execução, com suporte a entrada única e em lote.

### Modified Capabilities
- None

## Impact

- **Backend**: compilação/execução passa a filtrar agentes sem LLM e a decidir ativação por tarefa.
- **API**: execução precisa aceitar entrada única ou lote e retornar metadados de roteamento.
- **Frontend**: fluxo de execução deve suportar envio em lote, visualização de agentes ativados/ignorados e novo `Task Node` como bootstrap.
