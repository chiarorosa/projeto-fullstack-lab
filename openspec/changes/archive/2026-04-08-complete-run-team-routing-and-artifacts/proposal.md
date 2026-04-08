## Why

O `Run Team` atual ainda usa execução simulada e roteamento simplificado, sem decisão real de qual agente deve assumir cada tarefa com base em `goal` e `backstory`. Também falta transparência visual de conexões entre nós e uma aba dedicada para artefatos gerados por execução.

## What Changes

- Implementar roteamento real de tarefas a partir do `Task Node` para os agentes conectados, com seleção dinâmica do agente mais adequado por tarefa usando análise de `goal`/`backstory` via LLM.
- Usar a LLM conectada ao agente selecionado como cérebro de execução para produção de saída final por tarefa.
- Exibir visualmente conexões e estado de ativação por nó (Task, Agent, LLM), incluindo indicação clara de agentes sem LLM conectado.
- Adicionar validações de execução para impedir agentes inválidos (sem LLM) de participar do `Run Team`.
- Criar aba dedicada de artefatos da execução (inputs, roteamento, outputs, status e metadados) no frontend.

## Capabilities

### New Capabilities
- `intelligent-task-routing`: roteamento inteligente por tarefa com seleção de agente via avaliação semântica de perfil (`goal`/`backstory`) e uso da LLM conectada.
- `run-artifacts-workspace`: área/aba de artefatos da execução para inspeção completa pós-run.

### Modified Capabilities
- `agent-task-routing`: evoluir de ativação uniforme para ativação seletiva por tarefa e validação visual/funcional de conectividade entre nós.

## Impact

- **Backend**: execução passa de simulação para orquestração orientada por roteamento inteligente e execução real por LLM conectada.
- **Frontend**: canvas/properties/logs ganham estado visual de conectividade e status de elegibilidade de agentes.
- **UX**: `Run Team` passa a refletir comportamento end-to-end completo, com rastreabilidade em artefatos.
