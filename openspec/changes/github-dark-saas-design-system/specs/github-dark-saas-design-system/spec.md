## ADDED Requirements

### Requirement: Centralized Dark Theme Tokens
The frontend SHALL define a centralized token system for color, typography, spacing, borders, and interaction states, and UI components MUST consume these tokens instead of raw visual literals.

#### Scenario: Token set includes required semantic color roles
- **WHEN** theme tokens are defined for the design system
- **THEN** tokens include semantic roles for background, surface, surface-hover, border, text-primary, text-secondary, text-muted, brand, brand-hover, danger, warning, and info

#### Scenario: Components consume tokens instead of raw colors
- **WHEN** core UI components are rendered
- **THEN** styles reference semantic design tokens for color and spacing
- **AND** component styles do not require direct hex literals for standard states

### Requirement: Typography and Density Baseline
The frontend SHALL use a GitHub-style system font stack with a 14px base body size and a compact hierarchy driven primarily by controlled font sizes and two font weights.

#### Scenario: Base typography is applied globally
- **WHEN** a user opens primary screens
- **THEN** body text renders at 14px using the configured system font stack

#### Scenario: Typography hierarchy remains compact and clear
- **WHEN** headings, section labels, body text, and metadata are displayed together
- **THEN** hierarchy is distinguishable using tokenized size and weight rules
- **AND** the system uses regular and semibold as the primary hierarchy weights

### Requirement: Standardized Application Shell Layout
The frontend SHALL implement a standardized layout with topbar, fixed sidebar, primary content region, and responsive side panel behavior.

#### Scenario: Desktop layout follows the four-region shell
- **WHEN** the application is viewed at desktop breakpoints
- **THEN** topbar, sidebar, content, and side panel regions are visibly structured and readable

#### Scenario: Small-screen layout preserves usability
- **WHEN** the application is viewed on smaller breakpoints
- **THEN** sidebar and side panel behavior adapts responsively without blocking primary content interaction

### Requirement: Reusable Component Style Standards
The frontend SHALL provide reusable style standards for card, button variants, sidebar item states, progress bar, and feature/list item structures.

#### Scenario: Card and button primitives are standardized
- **WHEN** cards and buttons are rendered in major screens
- **THEN** card surfaces use tokenized background, border, radius, and spacing
- **AND** button variants are consistently presented as primary, secondary, and ghost

#### Scenario: Sidebar, progress, and list patterns are standardized
- **WHEN** navigation and status/feature rows are rendered
- **THEN** sidebar items expose default, hover, and active states using tokenized mapping
- **AND** progress bars and list items use the same spacing and semantic status presentation rules

### Requirement: Interaction and Consistency Rules
The frontend SHALL apply consistent interaction and UX rules for hierarchy, spacing rhythm, feedback visibility, and motion.

#### Scenario: Interaction states are subtle and consistent
- **WHEN** users hover, focus, select, or disable controls
- **THEN** controls use shared tokenized interaction states with subtle transitions in the 120-200ms range

#### Scenario: Feedback and system state remain visible
- **WHEN** screens present operational information
- **THEN** status and usage indicators remain visually clear through standardized patterns
- **AND** hierarchy is communicated with structure and typography rather than color alone

### Requirement: Design System Constraints Enforcement
The frontend SHALL enforce dark-system constraints that prohibit incompatible visual patterns in standard UI implementation.

#### Scenario: Forbidden visual patterns are avoided
- **WHEN** implementing or refactoring frontend styles
- **THEN** base UI surfaces do not rely on pure black or pure white as primary background layers
- **AND** random non-token spacing values and arbitrary component patterns are not required for standard interface construction
