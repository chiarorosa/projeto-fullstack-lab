## Context

The current backend exposes execution and provider-validation routes without authentication or rate limits, and provider API keys are currently carried in graph/node payloads that can be persisted in team JSON. This creates three immediate risks before feature expansion: unauthorized API usage, cost abuse on LLM endpoints, and credential disclosure through storage/transport/logging paths.

This change introduces a baseline security architecture that is intentionally small and implementable in the current stack (FastAPI + SQLite + React), while preserving the existing graph-driven product model.

## Goals / Non-Goals

**Goals:**
- Protect sensitive endpoints with enforced access control and rate limits.
- Remove plaintext provider secrets from persisted graph payloads.
- Introduce secure credential storage and runtime secret resolution.
- Ensure validation, logs, events, and API responses do not leak secrets.
- Move security-sensitive runtime behavior (CORS, auth, throttling) to environment-driven config.

**Non-Goals:**
- Full user/account system with RBAC, sessions, and multi-tenant org isolation.
- External secret-manager integration (AWS/GCP/Vault) in this iteration.
- Complete zero-trust network redesign.
- Changes to agent/task orchestration semantics unrelated to security baseline.

## Decisions

### 1) Add token-based API guard for sensitive routes
- **Decision**: Introduce a shared bearer-token guard for sensitive endpoints (`/execute`, `/api/llm/test-provider`, and `/api/teams*` write/read paths), controlled via environment configuration.
- **Rationale**: Fastest meaningful protection with minimal architectural churn.
- **Alternatives considered**:
  - OAuth/JWT user auth now: stronger identity model, but too large for baseline phase.
  - Keep endpoints open and rely on CORS/network perimeter: insufficient and bypassable.

### 2) Add per-endpoint rate limiting for high-cost paths
- **Decision**: Apply rate limits to execution and provider-validation endpoints (token/IP keyed), returning deterministic `429` responses with retry metadata.
- **Rationale**: Controls abuse and accidental runaway usage while preserving functionality.
- **Alternatives considered**:
  - Global app-level throttling only: too coarse, penalizes low-risk endpoints.
  - No limits until billing controls exist: leaves immediate cost-exposure gap.

### 3) Introduce credential references instead of persisted raw keys
- **Decision**: Persist provider credentials in a dedicated secure store and reference them from graph data with `credentialRef` identifiers.
- **Rationale**: Decouples secrets from graph JSON and standardizes secret lifecycle.
- **Alternatives considered**:
  - Keep keys in graph JSON: unacceptable risk and poor auditability.
  - Hash-only storage: unusable because runtime provider calls need plaintext.

### 4) Encrypt credentials at rest and resolve only at runtime
- **Decision**: Encrypt secret values before database write using an application encryption key from environment; decrypt only at execution/validation boundary.
- **Rationale**: Reduces impact of DB compromise and avoids plaintext-at-rest.
- **Alternatives considered**:
  - Obfuscation/base64: not security controls.
  - External KMS now: desirable long-term, too much integration for baseline.

### 5) Support secure validation with secret reference or ephemeral key
- **Decision**: Provider validation accepts either `credentialRef` (preferred) or one-time ephemeral `apiKey` input, with explicit guarantee that ephemeral values are not persisted.
- **Rationale**: Preserves UX for first-time testing while keeping storage safe.
- **Alternatives considered**:
  - Require pre-saved credentials only: safer but higher friction for quick tests.
  - Keep current direct key-in-node flow: persists insecure pattern.

### 6) Standardize redaction across logs, responses, and SSE events
- **Decision**: Add centralized secret-redaction utility and apply it to exception handling, validation responses, execution event payloads, and structured logs.
- **Rationale**: Prevents accidental leaks through non-storage channels.
- **Alternatives considered**:
  - Ad hoc redaction at call sites: inconsistent and brittle over time.

### 7) Make CORS and frontend API base URL environment-driven
- **Decision**: Replace hardcoded API URL/origins with env-based configuration and secure defaults.
- **Rationale**: Avoids insecure production drift and supports deployment environments cleanly.
- **Alternatives considered**:
  - Keep localhost constants: operationally fragile and unsafe in non-dev contexts.

## Risks / Trade-offs

- [Risk] Shared token model is coarse-grained and not user-aware -> Mitigation: document as baseline and keep auth layer boundary ready for future JWT/RBAC migration.
- [Risk] Encryption key misconfiguration can block secret access -> Mitigation: startup validation, clear operational error messages, and runbook for key provisioning.
- [Risk] Legacy stored plaintext keys require migration handling -> Mitigation: one-time migration to credential store with verification and fallback plan.
- [Risk] Rate limiting may block valid burst traffic -> Mitigation: configurable limits, scoped application to expensive endpoints, and observable 429 metrics.
- [Risk] Added security checks increase request latency slightly -> Mitigation: in-memory token check and lightweight limiter strategy.

## Migration Plan

1. Add credential storage schema/migration and encryption utility.
2. Add auth middleware/dependency and endpoint-level rate limiting.
3. Implement graph transformation path from raw `apiKey` to `credentialRef` on save/update.
4. Add startup migration for legacy teams containing persisted `apiKey` values.
5. Update provider validation API contract to accept `credentialRef` and ephemeral key mode.
6. Update frontend properties flow to store/use credential references and masked secret states.
7. Apply redaction utility to logs, API errors, and SSE payloads.
8. Roll out environment-based CORS/API URL configuration with deployment defaults.

Rollback strategy:
- Keep reversible DB migration for new tables/columns where possible.
- Feature-flag auth enforcement and rate-limit policy for emergency disable.
- Maintain backward-read compatibility for legacy graph payload during rollback window.

## Open Questions

- Should read-only team routes require authentication in all environments, or only non-dev environments?
- What default rate limits should be applied for `/execute` vs `/api/llm/test-provider` in production?
- Should ephemeral validation keys be accepted in production, or restricted to local/dev modes?
- What rotation policy should be required for the credential encryption key in ops documentation?
