## 1. Design System Foundation

- [x] 1.1 Inventory all frontend style entry points and identify hardcoded colors, spacing, typography, and interaction styles that must be tokenized
- [x] 1.2 Define centralized dark-theme tokens for semantic colors, typography, spacing, borders/radius, and interaction states in a shared theme location
- [x] 1.3 Replace global/base frontend styles to consume the new token set and enforce 14px body baseline with system font stack

## 2. Shell Layout Standardization

- [x] 2.1 Refactor the main shell into standardized topbar, fixed sidebar, content region, and side panel structure using shared spacing rhythm
- [x] 2.2 Update sidebar sizing, label density, and responsive behavior to preserve usability on desktop and small breakpoints
- [x] 2.3 Remove ad-hoc layout values in shell wrappers and replace with tokenized spacing and border rules

## 3. Component Pattern Refactor

- [x] 3.1 Standardize card styles (surface, border, padding, radius) across primary screens using shared tokens
- [x] 3.2 Standardize button variants (primary, secondary, ghost) and align hover/focus/disabled states to semantic state tokens
- [x] 3.3 Implement consistent sidebar item states (default/hover/active) with clear active indicator and tokenized contrast
- [x] 3.4 Standardize progress bar and feature/list item patterns with reusable spacing and status presentation rules

## 4. Consistency Enforcement and Validation

- [x] 4.1 Remove remaining inline styling and raw visual literals in major components, replacing them with token references
- [x] 4.2 Verify visual hierarchy and feedback visibility (status, usage, system state) across key screens in desktop and mobile layouts
- [x] 4.3 Run frontend lint/build checks, fix regressions introduced by the refactor, and document intentional visual deviations from strict token rules

## Change Notes

- Token system refactored to dark-first GitHub-style semantics in `frontend/src/index.css` (mandatory color/typography/spacing/state tokens added and mapped to existing app variables).
- Shared theme constants aligned in `frontend/src/theme/tokens.ts` for canvas/node/provider colors and flow surfaces.
- Main shell and sidebar behavior standardized in `frontend/src/index.css` (topbar/sidebar/content/side panel structure, desktop and responsive sizing rules).
- Reusable UI primitives added:
  - `frontend/src/components/ui/Button.tsx`
  - `frontend/src/components/ui/Card.tsx`
  - `frontend/src/components/ui/ProgressBar.tsx`
  - `frontend/src/components/ui/FeatureListItem.tsx`
- Core surfaces migrated to those primitives in `frontend/src/App.tsx` and `frontend/src/components/TeamManager.tsx`.
- Inline style remnants removed from major components (`SidebarPalette`, `LLMNode`, `AgentNode`, `TeamManager`) except dynamic width in `ProgressBar` which is data-driven.
- Validation:
  - `npm run build` passes.
  - `npm run lint` still fails on pre-existing `@typescript-eslint/no-explicit-any` findings in unchanged legacy areas (`frontend/src/api/client.ts`, `frontend/src/components/Canvas.tsx`, `frontend/src/components/PropertiesPanel.tsx`).
- Intentional deviation: provider-specific accent hues are retained for quick visual identification in node UIs, but remain constrained under centralized token variables.
