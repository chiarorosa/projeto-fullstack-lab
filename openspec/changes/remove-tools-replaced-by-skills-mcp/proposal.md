## Why

The Tools concept was introduced but not adopted in real workflows, and it now adds UI and runtime complexity without delivering value. We should remove it now so the product can evolve toward a cleaner architecture focused on SKILLS and MCP integrations.

## What Changes

- Remove Tool Node creation and editing paths from the frontend canvas and properties UI
- Remove backend tool execution branches and metadata plumbing tied to agent-connected tools
- Remove OpenRouter tool-specific capability requirements that depend on Tool Nodes
- Keep agent and LLM execution paths intact so task routing continues to work without tools
- Mark this as a transitional cleanup that prepares the codebase for future SKILLS/MCP-based extensibility

## Capabilities

### New Capabilities
- `skills-mcp-extensibility`: Define the system direction to support future extensibility through SKILLS and MCP instead of Tool Nodes

### Modified Capabilities
- `openrouter-ai-tool`: Remove Tool Node-based OpenRouter tool configuration and execution requirements from the current product behavior

## Impact

- **Frontend**: `SidebarPalette`, `Canvas`, tool node rendering, and `PropertiesPanel` paths related to `toolType` and Tool Node editing
- **Backend**: `compiler.py` paths for `connectedTools`, tool execution branching, and tool SSE events
- **Specs**: Replace current Tool Node expectations with deprecation/removal requirements and add forward-looking SKILLS/MCP direction
- **Developer experience**: Reduced maintenance surface until SKILLS/MCP implementation is introduced
