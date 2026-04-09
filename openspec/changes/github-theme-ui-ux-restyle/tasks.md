## 1. Theme Foundation

- [x] 1.1 Inventory current frontend style entry points (global CSS, theme files, layout wrappers, sidebar styles) and map where typography/colors are currently defined
- [x] 1.2 Create centralized GitHub-reference design tokens for typography, surfaces, text, borders, and interaction states
- [x] 1.3 Apply GitHub-style font stack globally and reduce base text scale while preserving heading/body hierarchy

## 2. Layout and Sidebar Update

- [x] 2.1 Update main layout containers to consume the new theme tokens instead of ad-hoc color values
- [x] 2.2 Increase sidebar width on desktop and implement responsive behavior for smaller breakpoints
- [x] 2.3 Validate sidebar readability and spacing for labels, groups, and controls after width changes

## 3. Component Contrast and Consistency

- [x] 3.1 Update core UI components (cards, panels, forms, buttons, labels, toolbars) to use tokenized GitHub-reference colors
- [x] 3.2 Standardize interactive states (hover, focus, selected, disabled) using shared state tokens
- [x] 3.3 Improve text/surface/border contrast across major screens and remove conflicting hardcoded color remnants

## 4. Validation and Stabilization

- [x] 4.1 Perform desktop/mobile visual QA for typography scale, sidebar responsiveness, and global contrast consistency
- [x] 4.2 Run frontend lint/build checks and fix any style or type regressions introduced by the restyle
- [x] 4.3 Document final token decisions and any intentional deviations from GitHub reference palette in the change notes

## Change Notes

- Frontend style entry points inventoried and mapped in implementation notes (global CSS in `frontend/src/index.css`, flow colors in `frontend/src/components/Canvas.tsx`, node/palette accents in `frontend/src/components/SidebarPalette.tsx`, `frontend/src/components/nodes/LLMNode.tsx`, and edge stroke in `frontend/src/store/canvasStore.ts`).
- Centralized token module added in `frontend/src/theme/tokens.ts` for node/provider colors and shared flow theme values.
- GitHub-reference typography and compact type scale applied globally in `frontend/src/index.css` using GitHub-like system sans/mono stacks and reduced body/component text sizes.
- Sidebar width increased for desktop and adjusted responsively (`280px` base, `240px` at <=1180px, full-width stacked layout at <=980px) with spacing/readability refinements.
- Core components and states (hover/focus/selected/disabled/success/error) now use shared variables in `frontend/src/index.css` (`--state-*`, semantic color tokens) for stronger contrast consistency.
- Validation runs: `npm run build` passed; `npm run lint` still reports pre-existing `@typescript-eslint/no-explicit-any` issues in files with existing `any` usage (`frontend/src/api/client.ts`, `frontend/src/components/Canvas.tsx`, `frontend/src/components/PropertiesPanel.tsx`), not introduced by this restyle.
- Intentional deviations from strict GitHub palette: semantic accents for node categories (task/webhook/llm) were kept as GitHub-adjacent tones to preserve canvas node-type affordance while keeping base surfaces, borders, and text aligned to GitHub light theme references.
