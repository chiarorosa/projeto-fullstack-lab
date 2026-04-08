# Proposal: Visual Multi-Agent Team Builder

## Motivation
O objetivo é criar uma aplicação fullstack que simplifique e democratize a criação de times multiagentes. O processo atual de configuração de agentes autônomos e suas interações costuma ser técnico e complexo. Ao oferecer uma interface visual (drag-and-drop ou baseada em nós), permitimos que os usuários definam funções, habilidades e a cadeia de comando (hierarquia ou fluxo de trabalho) de maneira intuitiva. Além disso, a flexibilidade de ligar cada agente a um modelo de linguagem (LLM) distinto ou usar um modelo único para toda a equipe atende tanto a casos de uso simples quanto a arquiteturas avançadas especializadas.

## Goals
- Interface visual intuitiva para montagem e configuração de times de agentes.
- Atribuição simplificada de papéis (system prompts), habilidades (ferramentas/tools) e LLM específico por agente.
- Definição estruturada da cadeia de comando (quem passa a tarefa para quem, líder e subordinados).
- Flexibilidade no uso de LLMs (configuração global para o time ou per-agent).

## Non-Goals
- Execução complexa de infraestrutura de nuvem auto-gerida (foco inicial será na lógica e interface da aplicação).
- Treinamento local de LLMs na interface.

## Scope & Impact
A aplicação será composta por um backend capaz de orquestrar os agentes interagindo com as APIs variadas de LLMs, e um frontend focado em uma experiência interativa rica na representação de grafos, fluxos ou hierarquias. Isso pode abrir o uso de IA multiagente para um grupo de usuários menos técnicos e acelerar prototipagem para os técnicos.
