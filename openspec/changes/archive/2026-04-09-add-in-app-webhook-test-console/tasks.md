## 1. Webhook Test Console Foundation

- [x] 1.1 Add frontend state and types for webhook test requests (endpoint, headers, JSON body, latency, response payload, error state).
- [x] 1.2 Implement Webhook Test Console UI panel with request composer and response inspector integrated into the existing workspace layout.
- [x] 1.3 Add client-side JSON validation and send guards so malformed payloads are blocked with explicit feedback.

## 2. Request Execution and Traceability

- [x] 2.1 Extend frontend API client to send webhook test requests to `/api/webhooks/{webhook_id}` with configurable headers and correlation metadata.
- [x] 2.2 Update backend webhook trigger handling to accept/propagate test-origin correlation metadata without changing core execution semantics.
- [x] 2.3 Return and display structured response diagnostics (status, headers, body, duration, execution reference) in the console.

## 3. Presets and UX Integration

- [x] 3.1 Implement per-Webhook Node request presets (save/load) for headers and JSON payload templates.
- [x] 3.2 Add quick access from Webhook Node properties to open/use the test console with the currently configured endpoint.
- [x] 3.3 Ensure responsive behavior and clear visual states for idle/loading/success/error in desktop and mobile layouts.

## 4. Artifacts Workspace and Verification

- [x] 4.1 Extend run artifacts UI to surface webhook trace fields (`source`, `trigger_id`, `correlation_id`) for test-triggered runs.
- [x] 4.2 Add backend/frontend tests for accepted webhook test calls, unknown webhook ids, malformed JSON handling, and response diagnostics rendering.
- [x] 4.3 Add compatibility assertions confirming task-triggered and webhook-test-triggered runs remain distinguishable and backward-compatible.
