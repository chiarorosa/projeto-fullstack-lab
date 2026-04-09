# Visual Multi-Agent Team Builder

Este é um repositório contendo uma aplicação Fullstack (Frontend e Backend) dedicada à construção visual de equipes de agentes de Inteligência Artificial. A aplicação permite a definição de fluxos de trabalho, orquestração de agentes e configuração de diferentes provedores de LLMs através de uma interface gráfica baseada em nós estruturada para facilitar o desenvolvimento e execução de casos de uso multi-agentes.

## Sobre o Projeto

Este projeto tem como objetivo principal demonstrar um caso de estudo de desenvolvimento orientado a especificações (Spec-Driven Development - SDD). Todo o ciclo de vida deste projeto está sendo guiado pela abordagem de SDD em conjunto com tecnologias avançadas de agentes autônomos.

As ferramentas em destaque utilizadas para o desenvolvimento deste laboratório incluem:
- Antigravity: Agente de IA avançado para automação e paridade de programação.
- Opencode: Ferramentas auxiliares de integração local do IDE.
- Openspec: Especificações em formato estruturado que servem de "Single Source of Truth" para o agente autônomo.

Recomendamos o uso do **opencode**. Para habilitar as automações completas do agente (skills e fluxos de trabalho), instale as ferramentas necessárias executando o comando (lembrando que a pasta `.agents` não é versionada no repositório por ser grande):

```ps1
npx antigravity-awesome-skills --path .agents/skills
```

Nota: Este arquivo README foi exigido estritamente sem o uso de caracteres gráficos ("emojis") como parte das diretrizes de configuração deste repositório.

## Arquitetura

O repositório está estruturado em módulos distintos:
- `/frontend`: Interface gráfica desenvolvida com uma stack web moderna, focada no fluxo de trabalho baseado na arquitetura visual de nós.
- `/backend`: Servidor REST construído em Python, responsável por inicializar os agentes, orquestrar fluxos e gerenciar os provedores de serviços de LLM e lógica de roteamento de tarefas.
- `/openspec`: Documentos textuais delineando especificações operacionais e especificações arquiteturais consumidas pelas ferramentas SDD.

## Instruções de Uso (Getting Started)

### Pré-requisitos
- Node.js (versão 18 ou superior)
- Python (versão 3.10 ou superior)

### Configuração do Backend (FastAPI / Python)

1. Abra um terminal e navegue para o diretório de backend:
   ```ps1
   cd backend
   ```
2. Crie e ative um ambiente virtual (opcional, porém recomendado):
   ```ps1
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Instale as dependências necessárias:
   ```ps1
   pip install -r requirements.txt
   ```
4. Inicie o servidor localmente:
   ```ps1
   uvicorn main:app --reload --port 8000
   ```
O backend estará executando em `http://localhost:8000`.

### Configuração do Frontend (Vite + Node)

1. Abra um novo terminal na raiz do projeto e acesse o diretório frontend:
   ```ps1
   cd frontend
   ```
2. Instale as dependências listadas:
   ```ps1
   npm install
   ```
3. Execute o ambiente de desenvolvimento local:
   ```ps1
   npm run dev
   ```
Por fim, basta acessar o sistema pelo seu navegador através da URL indicada no terminal (frequentemente `http://localhost:5173`).

## Recomendações

Para quem tiver interesse em testar a aplicação de maneira acessível e flexível, recomendamos a utilização dos modelos gratuitos disponibilizados pela OpenRouter.

Você pode conferir a lista de modelos de inteligência artificial sem custo através do link:
- [OpenRouter - Free Models](https://openrouter.ai/models?q=free)

Para obter sua chave de acesso (API Key), basta gerá-la pelo painel:
- [OpenRouter Keys](https://openrouter.ai/workspaces/default/keys)

Com sua chave gerada, você poderá utilizá-la em quantos nós (nodes) de LLMs desejar nos fluxos de trabalho (workflows) da interface da aplicação.
