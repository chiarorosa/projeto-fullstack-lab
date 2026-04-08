# Specification: Visual Multi-Agent Team Builder

## Feature: Canvas-based Agent Orchestration

### Context
Users need a way to combine multiple autonomous agents without writing Python code, enabling rapid prototyping of multi-agent tasks.

### Requirements
1. **Node Editor Interface**
   - The user must be able to drag and drop nodes representing Agents, LLMs, and Tasks.
   - The user must be able to wire them together to define dependencies (e.g., Task A -> Task B).
2. **Agent Configuration**
   - Each Agent node must have properties for: Role, Backstory, Goal (System Prompts).
   - Each Agent must allow attaching an LLM node (to override the team's default LLM).
   - Each Agent must allow attaching Tools (nodes for specific skills).
3. **Execution & Feedback**
   - The user should be able to trigger the exacted graph execution.
   - The user should see real-time streaming of which agent is working and what output is generated.

### Acceptance Criteria
- Given the user creates two agents connected sequentially, when they hit "Run", the backend executes Agent 1 first, passes the output to Agent 2, and returns the final result.
- Given the user connects a distinct LLM (e.g., Gemini) to Agent 1 and another UI (e.g., local model) to Agent 2, the backend correctly maps their language models during task execution.
