## ADDED Requirements

### Requirement: GitHub Typography Baseline
The frontend SHALL use the GitHub-style sans-serif font stack as the default font family across the application and SHALL reduce base text sizing to a compact, readable scale.

#### Scenario: Global typography is applied
- **WHEN** a user opens any primary application screen
- **THEN** the rendered text uses the configured GitHub-style font stack as first-choice family
- **AND** body and supporting text are displayed in reduced size compared to the previous baseline

#### Scenario: Typography hierarchy remains readable
- **WHEN** headings, labels, body text, and helper text are displayed together
- **THEN** the interface preserves clear typographic hierarchy through size, weight, and spacing

### Requirement: GitHub Theme Color Palette
The frontend SHALL define and use a centralized token palette based on GitHub theme reference colors for surfaces, text, borders, and interaction states.

#### Scenario: Color tokens are used in core surfaces
- **WHEN** the main layout, sidebar, panels, and cards are rendered
- **THEN** component colors come from centralized GitHub-reference theme tokens
- **AND** hardcoded ad-hoc colors are not required for standard UI states

#### Scenario: Interactive states follow theme tokens
- **WHEN** users hover, focus, select, or disable interactive controls
- **THEN** state colors use the same centralized GitHub-reference token system

### Requirement: Wider Sidebar Layout
The application SHALL increase sidebar width relative to the previous layout to improve scanability while maintaining responsive behavior on smaller screens.

#### Scenario: Desktop sidebar uses increased width
- **WHEN** the app is viewed on desktop breakpoint
- **THEN** the sidebar is visibly wider than the previous baseline
- **AND** navigation labels and grouped actions fit with improved readability

#### Scenario: Mobile layout remains usable
- **WHEN** the app is viewed on small screens
- **THEN** sidebar behavior adapts responsively without blocking primary content interaction

### Requirement: Improved Global Contrast
The interface SHALL provide improved contrast across text, surfaces, and borders using GitHub-reference palette values to increase readability across the full application.

#### Scenario: Text contrast is improved in major UI regions
- **WHEN** users view pages containing primary content, forms, side panels, and status information
- **THEN** text-to-background contrast is stronger than the previous baseline in those regions

#### Scenario: Component boundaries are visually distinct
- **WHEN** adjacent UI blocks such as cards, panels, and toolbars are displayed
- **THEN** border and surface contrast makes block boundaries clearly distinguishable
