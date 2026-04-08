# llm-node-simplified Specification

## Purpose
TBD - created by archiving change simplify-llm-sidebar. Update Purpose after archive.
## Requirements
### Requirement: Single LLM Node Option in Sidebar
The system SHALL show exactly one LLM Node option in the sidebar palette.

#### Scenario: User views LLM category in sidebar
- **WHEN** user opens the sidebar palette
- **THEN** there is exactly one LLM option labeled "LLM" or "LLM Node"

#### Scenario: User adds LLM node from sidebar
- **WHEN** user clicks the LLM option in the sidebar
- **THEN** a single llmNode is added to the canvas
- **AND** the node can be configured via Properties Panel

### Requirement: Sidebar Category Label
The system SHALL display a clear category label for LLM nodes.

#### Scenario: Sidebar categories are displayed
- **WHEN** the sidebar palette renders
- **THEN** LLM nodes appear under a category labeled "LLM" (not "Language Models")

