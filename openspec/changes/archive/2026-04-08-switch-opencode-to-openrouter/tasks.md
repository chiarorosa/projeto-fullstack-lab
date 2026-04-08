# Tasks: Switch OpenCode to OpenRouter (LLM guidance)

## 1. OpenSpec Artifacts

- [x] 1.1 Create proposal.md with provider guidance scope and impact
- [x] 1.2 Create design.md describing UI metadata strategy and compatibility
- [x] 1.3 Create specs/llm-provider-guidance/spec.md with requirements and scenarios

## 2. Frontend Provider Guidance

- [x] 2.1 Add centralized provider metadata (default URL, env var, docs link, model placeholder) in `frontend/src/components/PropertiesPanel.tsx`
- [x] 2.2 Update LLM form to render provider-specific docs link and default URL hint block
- [x] 2.3 Keep/confirm `opencode` -> `openrouter` normalization in LLM form behavior

## 3. Styling and Verification

- [x] 3.1 Add compact styles for provider docs link and metadata hints in `frontend/src/index.css`
- [x] 3.2 Run frontend build to verify TypeScript and UI compile successfully
