## Context

The frontend currently has visual drift across global CSS, canvas widgets, panel controls, and interaction states. Colors, spacing, and typography are mixed between semantic variables and hardcoded values, which increases maintenance cost and weakens product consistency. This change introduces a strict, dark-first GitHub-inspired SaaS design system with centralized tokens and reusable component patterns so new and existing UI surfaces remain predictable.

## Goals / Non-Goals

**Goals:**
- Define a centralized token layer for dark theme colors, typography, spacing, and state styles.
- Map all core surfaces and controls to semantic tokens instead of raw values.
- Standardize shell layout with sidebar, topbar, content area, and responsive side panel behavior.
- Apply reusable component patterns for cards, button variants, sidebar items, progress bars, and feature/list rows.
- Enforce interaction and hierarchy rules (density, contrast, subtle motion, status visibility).

**Non-Goals:**
- Reworking business logic, APIs, graph execution flow, or data models.
- Introducing additional visual themes (light mode, brand theme variants) in this iteration.
- Rebuilding every component architecture from scratch beyond what is needed for standardized styling.

## Decisions

1. Use centralized design tokens as the single source of truth.
   - **Rationale:** Prevents style drift and makes refactors safe and scalable.
   - **Alternatives considered:**
     - Continue mixed raw values + variables: rejected due to ongoing inconsistency risk.
     - Component-local token definitions: rejected because it fragments theme governance.

2. Adopt a GitHub-inspired dark palette with semantic color mapping.
   - **Rationale:** Improves readability and supports developer-tool UX expectations while preserving clear semantic states.
   - **Alternatives considered:**
     - Keep existing purple-heavy accent palette: rejected because it conflicts with requested neutral dark system.
     - Introduce custom color families per feature: rejected due to weak consistency and higher cognitive load.

3. Apply compact typography and spacing scale globally.
   - **Rationale:** Maintains dense but readable information layout and consistent hierarchy across screens.
   - **Alternatives considered:**
     - Per-component font sizing: rejected because hierarchy becomes inconsistent.
     - Larger base font and looser spacing: rejected because it reduces information density.

4. Standardize shell layout and reusable UI primitives first, then migrate feature surfaces.
   - **Rationale:** Stabilizes foundation before broad component restyling and reduces regression risk.
   - **Alternatives considered:**
     - Screen-by-screen visual rewrite first: rejected because shared shells/components would still diverge.

5. Enforce interaction constraints via shared state tokens.
   - **Rationale:** Makes hover/focus/selected/disabled behavior predictable and accessible.
   - **Alternatives considered:**
     - Custom state styles per control: rejected because UX behavior becomes inconsistent.

## Risks / Trade-offs

- [Visual regressions in dense panels and node canvases] -> Mitigation: migrate layout primitives first, then run component-level visual QA at desktop and mobile breakpoints.
- [Legacy hardcoded values remain in low-traffic paths] -> Mitigation: run targeted code search for color/spacing literals and convert leftovers during implementation.
- [Strict token enforcement increases short-term implementation effort] -> Mitigation: prioritize shared components and shell regions to maximize immediate consistency impact.
- [Dark-first palette may expose weak contrast in existing labels] -> Mitigation: validate text/surface contrast during QA and tune semantic token pairs without breaking mapping rules.

## Migration Plan

1. Introduce or update the token layer (colors, typography, spacing, motion, state).
2. Migrate base app shell (topbar, sidebar, content, side panel) to tokenized layout primitives.
3. Refactor shared component styles (cards, buttons, sidebar items, progress bars, feature/list rows).
4. Remove/replace remaining inline styles and hardcoded visual values in major screens.
5. Run lint/build and responsive visual QA; fix contrast/spacing regressions.
6. Keep rollback simple by isolating changes in token and shared style files where possible.

## Open Questions

- Should strict token enforcement be codified with lint/style checks in a follow-up change?
- Do we preserve any existing non-semantic accent colors for node-type recognition, or fully remap all node accents to semantic token categories now?
