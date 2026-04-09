## Why

The frontend currently mixes visual styles, spacing patterns, and ad-hoc colors across components, which reduces clarity and makes the UI feel inconsistent. We need a single, enforceable design system so the product feels predictable, dense, and professional while staying maintainable as new UI is added.

## What Changes

- Introduce a centralized GitHub-inspired dark token system for colors, typography, spacing, borders, radii, and interaction states.
- Replace hardcoded visual values in core frontend surfaces with semantic tokens.
- Standardize the main shell into a clear topbar + fixed sidebar + content + responsive side-panel structure.
- Define and apply reusable component patterns for card, button variants, sidebar item states, progress bar, and feature/list rows.
- Enforce UX consistency rules (hierarchy, spacing rhythm, feedback visibility, subtle transitions) across primary screens.

## Capabilities

### New Capabilities
- `github-dark-saas-design-system`: Defines a dark-first, token-driven visual system and reusable UI patterns aligned with GitHub-inspired developer-tool UX standards.

### Modified Capabilities
- None.

## Impact

- **Frontend styling**: Global CSS/theme tokens and interaction states will be refactored to semantic design tokens.
- **Frontend layout**: Sidebar, topbar, content region, and side panel responsiveness will be standardized.
- **Frontend components**: Shared component styling patterns for cards, buttons, sidebar items, progress bars, and list rows will be introduced and applied.
- **Engineering workflow**: Future UI changes must consume the centralized token and component system instead of introducing ad-hoc visual styles.
