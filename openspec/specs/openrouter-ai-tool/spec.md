# openrouter-ai-tool Specification

## Purpose
Document the de-scoped OpenRouter Tool Node capability and migration expectations while the product transitions to SKILLS/MCP-based extensibility.

## Requirements
No active requirements.

## Migration Notes
- Remove Tool Node configuration dependencies from saved or in-progress flows and route execution through Task, Agent, and connected LLM nodes.
- Do not invoke `openrouter_ai` tool execution branches in runtime paths.
- Report provider and connectivity failures through existing agent/LLM execution error paths.
