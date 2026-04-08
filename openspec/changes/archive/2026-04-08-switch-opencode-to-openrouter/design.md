## Context

The current LLM Properties panel lets users choose provider and model, but it does not consistently surface provider-specific defaults such as base URL and official model catalog references. As a result, users often need to leave the app to find supported model IDs and endpoint details.

This change is scoped to the frontend configuration experience in `frontend/src/components/PropertiesPanel.tsx` and related styles in `frontend/src/index.css`.

## Goals / Non-Goals

**Goals:**
- Provide preconfigured provider guidance inside LLM Properties
- Show provider-specific default base URL hints for OpenRouter, OpenAI, Anthropic, Google, and Local
- Add direct links to official model reference pages to speed up model selection
- Keep backward compatibility for legacy `opencode` provider values

**Non-Goals:**
- Changing backend runtime behavior for provider routing
- Persisting provider defaults server-side
- Implementing provider credential validation

## Decisions

1. **Centralize provider metadata in the UI**
   - A single metadata map contains default base URL, env var key, model placeholder, and model docs link per provider.
   - Rationale: keeps behavior consistent and easy to extend.

2. **Display guidance instead of auto-overwriting user fields**
   - Base URL remains editable and optional; default endpoint appears as hint/placeholder.
   - Rationale: users may use proxies/custom gateways and should not lose custom values.

3. **Use provider normalization for legacy values**
   - Treat `opencode` as `openrouter` in LLM Properties.
   - Rationale: avoids breaking existing saved graphs while presenting current naming.

## Risks / Trade-offs

- [Risk] Provider default URLs may evolve over time -> Mitigation: keep metadata isolated in one object for simple updates.
- [Risk] Too much guidance can clutter panel -> Mitigation: compact hint blocks with one doc link per provider.
- [Risk] Users may assume URL hint is enforced -> Mitigation: explicit text that field can be left blank to use defaults.
