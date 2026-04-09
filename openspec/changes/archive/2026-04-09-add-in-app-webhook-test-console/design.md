## Context

The application already supports webhook-triggered execution through Webhook Nodes and provides run logs/artifacts after execution. However, users must switch to external API clients to manually send webhook payloads while building flows. This introduces context switching and friction, especially when iterating on payload shape, headers, and expected responses.

This change adds an in-app test console focused on webhook validation workflows: compose request, execute against the configured webhook endpoint, inspect response, and correlate the call with run artifacts. The existing webhook endpoint and run persistence pipeline should be reused to avoid creating a separate execution path.

## Goals / Non-Goals

**Goals:**
- Provide an in-app webhook test experience comparable to lightweight Postman/Bruno usage for this product scope.
- Allow users to send JSON requests to Webhook Node endpoints with configurable headers and payload.
- Show complete request/response diagnostics (status, duration, headers, body, network error) in the same workspace.
- Persist or expose correlation metadata so test calls can be traced in run artifacts.
- Keep existing webhook trigger behavior backward-compatible.

**Non-Goals:**
- Building a full generic API client for arbitrary methods/endpoints beyond webhook testing needs.
- Implementing advanced team-wide request collection management, sharing, environments, or scripting.
- Replacing existing run execution or artifact subsystems.

## Decisions

1. Add a dedicated Webhook Test Console panel in frontend execution workspace.
- Decision: implement a focused console UI (endpoint, headers, JSON body, send action, response viewer) integrated with the current app layout.
- Rationale: keeps testing near graph editing and run inspection, minimizing context switching.
- Alternative considered: embedding external tool iframe/integration. Rejected due to complexity, auth/cors constraints, and reduced UX cohesion.

2. Reuse existing webhook trigger endpoint as primary execution path.
- Decision: the console sends requests directly to `/api/webhooks/{webhook_id}` and consumes the same response contract.
- Rationale: avoids duplicating execution logic and guarantees parity between test calls and real webhook calls.
- Alternative considered: separate `/api/webhooks/test` endpoint. Rejected to prevent drift and extra maintenance.

3. Add optional test-origin metadata in request/response and artifact linking.
- Decision: include correlation-friendly fields (for example request id and test origin marker) in console requests and display them; extend artifact UI to highlight webhook source and correlation id.
- Rationale: users must quickly map a test request to resulting execution artifacts.
- Alternative considered: rely only on timestamps. Rejected because timestamp-only correlation is fragile under concurrent runs.

4. Keep payload authoring JSON-first with strict validation before send.
- Decision: body editor validates JSON client-side and blocks send with explicit errors when invalid.
- Rationale: most webhook flows in this app are JSON-centric; early validation improves usability and reduces noisy backend errors.
- Alternative considered: permissive raw text mode by default. Rejected for higher failure rate and less predictable behavior.

## Risks / Trade-offs

- [Console complexity increases UI density] -> Mitigation: collapsible panel, sensible defaults, and concise component hierarchy.
- [Users misinterpret test calls as production traffic] -> Mitigation: explicit “test request” labeling and visibly scoped endpoint context.
- [Correlation metadata inconsistency across entry modes] -> Mitigation: standardize display fields (`source`, `trigger_id`, `correlation_id`) in artifacts/logs.
- [Potential leakage of sensitive headers/body in UI history] -> Mitigation: avoid long-term storage by default and apply redaction/masking for known secret fields.

## Migration Plan

1. Introduce frontend Webhook Test Console components and API client methods behind existing webhook node workflows.
2. Extend backend response/metadata handling only as needed for robust request-to-run correlation.
3. Update artifacts/log views to expose correlation/source context for webhook test requests.
4. Add tests for console request handling, malformed payload UX, and metadata linkage.
5. Rollback strategy: disable/hide console UI while keeping webhook endpoint and existing execution path intact.

## Open Questions

- Should request presets be persisted per team only, or per webhook node with optional cloning?
- Do we need a small request history list in v1, or only “last request” replay?
- Should non-JSON content types be supported in initial release or deferred?
