## Why

Webhook-driven flows currently require users to leave the platform and use external tools (for example Bruno or Postman) to test payload delivery and response behavior. This breaks workflow continuity and slows down iteration when configuring webhook-triggered automations.

## What Changes

- Add an in-app webhook test console that allows users to compose request method, headers, and JSON body, then send requests directly to configured webhook endpoints.
- Display structured request/response details (status, latency, headers, response body, and transport errors) inside the app so users can validate webhook behavior without external clients.
- Provide reusable request presets tied to Webhook Node configuration to accelerate repeated testing during flow setup.
- Integrate test execution visibility with existing run/log UX so users can quickly correlate webhook test calls with downstream flow execution.

## Capabilities

### New Capabilities
- `webhook-test-console`: In-app UI and backend interaction model for composing, sending, and inspecting webhook test requests.

### Modified Capabilities
- `run-artifacts-workspace`: Extend run/artifact views to surface webhook test context linkage and improve end-to-end observability for webhook-triggered runs.

## Impact

- Frontend execution/testing UX: new console panel/component, request editor, response inspector, and Webhook Node-level quick actions.
- Frontend API layer: webhook test request client methods and typed response contracts.
- Backend request path usage: leverage existing webhook trigger endpoints; may add optional diagnostics metadata returned for test-origin calls.
- Run/log observability surfaces: execution logs and persisted artifact views may include webhook test context references.
