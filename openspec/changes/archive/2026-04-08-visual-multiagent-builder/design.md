# Design: Visual Multi-Agent Team Builder

## Architecture Overview
The application will follow a client-server architecture.
- **Frontend (Client)**: A graphical web interface allowing users to build agent teams via a node-based or drag-and-drop workflow editor. Built with Vite setup (React/TypeScript probably for the visual node graphs using something like React Flow).
- **Backend (Server)**: A Python API (using FastAPI/Agno) that manages the actual multi-agent orchestration, validates the connection of specific LLMs to specific agents, and triggers team executions.

## Components & Data Flow
1. **Visual Editor (UI)**
   - Components: Node Palette (Agents, LLMs, Tools), Canvas (Graph Editor), Properties Panel.
   - Flow: User drags an "Agent" node onto the canvas, connects an "LLM" node (e.g., GPT-4 or Gemini) to it, and assigns "Tool" nodes (e.g., Web Search, Calculator).
2. **Team Configuration Compiler**
   - The UI serializes the node graph into a structured JSON representing the team (roles, skills, command chain, LLM mapping).
   - JSON is sent to the backend via REST API.
3. **Agent Orchestrator (Backend)**
   - Receives the JSON configuration.
   - Bootstraps the Agno framework (or similar) to dynamically instantiate the agents, assigning the requested LLMs and tools to each.
   - Establishes the command chain (who calls who or sequential workflow).

## Technical Choices
- **Frontend**: Vite + Vanilla/React (React Flow is highly recommended for node editors).
- **Backend**: Python + FastAPI (or just Agno's native API serving capabilities).
- **Styling**: Premium modern design (dark mode, glassmorphism, vibrant accents, smooth transitions).
- **Data storage**: SQLite for saving team templates.
