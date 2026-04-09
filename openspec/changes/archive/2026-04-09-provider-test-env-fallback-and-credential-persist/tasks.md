## 1. Backend Validation Source Resolution

- [x] 1.1 Add provider-to-env variable mapping for keyed providers (`openai`, `openrouter`/`opencode`, `anthropic`, `google`)
- [x] 1.2 Implement effective key resolver with precedence `apiKey` > `credentialRef` > provider env fallback
- [x] 1.3 Return actionable validation error when no key source is available for keyed providers

## 2. Test Provider Persistence Flow

- [x] 2.1 Extend provider test request schema with optional node persistence context (`team_id`, `node_id`)
- [x] 2.2 Extend provider test response schema to include updated `credential_ref` on successful persistence
- [x] 2.3 Update `/api/llm/test-provider` route to persist effective key on success for keyed providers when node context is present
- [x] 2.4 Implement node-scoped credential upsert behavior (update existing credential ref; create new when absent)
- [x] 2.5 Persist updated `credentialRef` in team graph JSON for the tested node and ensure `apiKey` is not stored

## 3. Frontend Test Provider Integration

- [x] 3.1 Send node persistence context in Test Provider requests from LLM Properties
- [x] 3.2 Apply returned `credentialRef` to local node state after successful provider test
- [x] 3.3 Preserve explicit-key override behavior and keep empty-key flow compatible with backend env fallback

## 4. Verification and Documentation

- [x] 4.1 Add backend tests for env fallback per provider, precedence ordering, and missing-key error paths
- [x] 4.2 Add backend tests for credential persistence/rotation after successful test and no-mutation on failure
- [x] 4.3 Update README/backend env docs with provider fallback behavior and precedence semantics for Test Provider
