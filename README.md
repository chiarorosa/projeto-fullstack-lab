# Visual Multi-Agent Team Builder

Este é um repositório contendo uma aplicação Fullstack (Frontend e Backend) dedicada à construção visual de equipes de agentes de Inteligência Artificial. A aplicação permite a definição de fluxos de trabalho, orquestração de agentes e configuração de diferentes provedores de LLMs através de uma interface gráfica baseada em nós estruturada para facilitar o desenvolvimento e execução de casos de uso multi-agentes.

## Sobre o Projeto

Este projeto tem como objetivo principal demonstrar um caso de estudo de desenvolvimento orientado a especificações (Spec-Driven Development - SDD). Todo o ciclo de vida deste projeto está sendo guiado pela abordagem de SDD em conjunto com tecnologias avançadas de agentes autônomos.

As ferramentas em destaque utilizadas para o desenvolvimento deste laboratório incluem:
- Antigravity: Agente de IA avançado para automação e paridade de programação.
- Opencode: Ferramentas auxiliares de integração local do IDE.
- Openspec: Especificações em formato estruturado que servem de "Single Source of Truth" para o agente autônomo.

Nota: Este arquivo README foi exigido estritamente sem o uso de caracteres gráficos ("emojis") como parte das diretrizes de configuração deste repositório.

## Arquitetura

O repositório está estruturado em módulos distintos:
- `/frontend`: Interface gráfica desenvolvida com uma stack web moderna, focada no fluxo de trabalho baseado na arquitetura visual de nós.
- `/backend`: Servidor REST construído em Python, responsável por inicializar os agentes, orquestrar fluxos e gerenciar os provedores de serviços de LLM e lógica de roteamento de tarefas.
- `/openspec`: Documentos textuais delineando especificações operacionais e especificações arquiteturais consumidas pelas ferramentas SDD.

## Como Iniciar

1. Navegue até as pastas correspondentes (/frontend ou /backend).
2. Siga os requisitos de instalação e dependências de pacote locais em cada subprojeto.
3. Inicie os servidores de desenvolvimento a partir de seus conteúdos instalados.
