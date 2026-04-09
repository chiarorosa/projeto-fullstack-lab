## Context

The current Test Provider flow validates using either a credential reference already stored for the node or a one-time key typed in the LLM Properties panel. It does not fully implement the desired behavior where an empty API key field automatically falls back to backend `.env` provider keys, and it does not persist the key after a successful explicit test for that node in a deterministic rotation path.

This change is cross-cutting across frontend payload shaping, backend validation orchestration, secure credential persistence, and provider-specific env-key resolution. It must preserve existing guarantees from the security baseline: encrypted-at-rest credentials, no raw key persistence in team graph JSON, and redacted responses.

## Goals / Non-Goals

**Goals:**
- Add provider-key fallback from backend environment when API Key input is empty during Test Provider.
- Apply this behavior to all supported keyed providers (`openai`, `openrouter`/`opencode`, `anthropic`, `google`).
- Define precedence: explicit API key typed by user takes priority over env fallback.
- On successful provider test, persist the effective key into secure credential storage and update the node credential reference.
- On repeated tests for the same node, rotate/update the node credential to the latest successfully validated key.

**Non-Goals:**
- Changing execution-time credential resolution precedence for team execution endpoints.
- Adding support for storing credentials for `local` provider.
- Introducing a new secret manager/KMS integration.
- Creating user-level credential vault UX or key history/audit timelines.

## Decisions

### 1) Introduce provider env-key resolver in backend validation path
- **Decision**: Add a backend resolver that maps provider to env variable names and returns fallback key when request key is absent.
- **Rationale**: Backend has authoritative runtime env context and should own secret-source precedence for security-sensitive behavior.
- **Alternatives considered**:
  - Frontend env fallback: rejected because frontend should not access backend secret material.
  - Require only explicit key: rejected because requested UX requires empty-field fallback.

### 2) Define key source precedence for Test Provider
- **Decision**: Use this precedence for keyed providers: `payload.api_key` (if non-empty) > `credential_ref` (if present) > provider env fallback.
- **Rationale**: Explicit user intent wins, existing node secret remains valid fallback, env supports bootstrap when node has no key.
- **Alternatives considered**:
  - Env before credential_ref: rejected because would unexpectedly override node-scoped secret.
  - credential_ref before explicit input: rejected because violates explicit override requirement.

### 3) Persist successful test key through secure credential lifecycle
- **Decision**: Extend the test endpoint to accept node context (`team_id`, `node_id`), and when validation succeeds for a keyed provider, upsert credential for that node and return the resulting `credential_ref`.
- **Rationale**: This guarantees "test-and-save" behavior and enables idempotent updates every time Test Provider is run.
- **Alternatives considered**:
  - Persist only on team save: rejected because requirement asks persistence after successful Test Provider.
  - Create new credential every test without replacement: rejected due to credential sprawl and stale refs.

### 4) Implement node-scoped credential rotation strategy
- **Decision**: If node already has `credential_ref`, update that credential's encrypted secret in place on successful test; otherwise create a new credential and attach it to node.
- **Rationale**: Preserves stable references while ensuring latest tested key is active for that node.
- **Alternatives considered**:
  - Always create new credential IDs: higher storage churn and harder traceability.
  - Never update existing refs: would fail "atualizando toda vez" requirement.

### 5) Persist updated credential reference in team graph immediately
- **Decision**: When test succeeds with node context, update the stored `teams.graph_json` node `credentialRef` (and remove `apiKey` if present) within the same request transaction.
- **Rationale**: Keeps backend state authoritative and immediately consistent after validation.
- **Alternatives considered**:
  - Return new `credentialRef` and let frontend persist later: vulnerable to lost update if user does not save team.

### 6) Keep redaction and non-leak guarantees intact
- **Decision**: Do not return effective key source values in responses; return only normalized success/failure and optional `credential_ref` token.
- **Rationale**: Maintains security baseline and prevents accidental leaks.
- **Alternatives considered**:
  - Return masked key fragments: unnecessary risk and no functional need.

## Risks / Trade-offs

- [Risk] Ambiguity between `credential_ref` and env fallback when both are present -> Mitigation: enforce explicit precedence and document it in specs/docs.
- [Risk] Test endpoint now mutates persistence, increasing side effects -> Mitigation: require node context for persistence and keep mutation bounded to tested node.
- [Risk] Team graph update race conditions under concurrent edits -> Mitigation: update by team id + node id in a single DB transaction and rely on existing save semantics for latest state.
- [Risk] Missing provider env vars in staging/production can cause false-negative tests -> Mitigation: actionable error message indicating expected env variable name.
- [Risk] Credential rotation can break old runs relying on previous key -> Mitigation: rotation is node-scoped and intentional on successful test; document operational expectation.

## Migration Plan

1. Extend provider test request/response schemas with optional node persistence context.
2. Add provider env-key mapping/resolution utility for keyed providers.
3. Update test-provider route orchestration to resolve effective key with precedence rules.
4. Implement credential upsert helpers (update existing ref or create + attach).
5. Update team graph persistence during successful test for keyed providers.
6. Update frontend Test Provider call payload to include node/team context and apply returned `credentialRef` to local node state.
7. Add tests for env fallback, explicit override, persistence on success, and per-test rotation.
8. Update README/baseline docs with provider env fallback behavior and precedence.

Rollback strategy:
- Disable persistence mutation in test-provider route (feature switch or guarded code path) while keeping pure validation behavior.
- Preserve backward-compatible request fields so frontend can continue testing without persistence side effects if rollback is needed.

## Open Questions

- Should successful validation using only existing `credential_ref` rewrite credential data (no-op) or skip persistence updates entirely?
- Should failure messages disclose which source failed (credential_ref vs env) or keep source-agnostic for security?
- Should we support provider-specific alternate env key aliases (e.g., `OPENAI_API_KEY` + legacy names) from day one?
