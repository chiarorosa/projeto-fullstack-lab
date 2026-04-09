## Context

The current execution contract assumes Task Node as the only flow bootstrap source. This works for manual and editor-driven runs but limits integration with external systems that need to trigger flows via HTTP events. The change introduces a Webhook Node bootstrap path while preserving existing Task Node behavior and routing semantics.

The implementation spans frontend node modeling, backend trigger endpoint handling, bootstrap validation, and run artifact metadata. Existing routing capabilities already operate on task inputs after bootstrap, so this design keeps routing logic mostly unchanged and focuses on normalizing bootstrap inputs before routing.

## Goals / Non-Goals

**Goals:**
- Add a first-class Webhook Node bootstrap source that can trigger flows from inbound HTTP calls.
- Preserve backward compatibility for flows that still use Task Node bootstrap.
- Normalize bootstrap payload into the same task input shape consumed by agent routing.
- Persist webhook source metadata for run traceability and debugging.

**Non-Goals:**
- Replacing or removing Task Node bootstrap support.
- Building advanced webhook security features (for example IP allowlists, signed-secret verification, retries orchestration) in this change.
- Redesigning downstream agent execution or semantic routing algorithms.

## Decisions

1. Support multi-bootstrap validation with explicit source selection.
- Decision: execution validation accepts either Task Node or Webhook Node as valid bootstrap source and fails only when neither is valid.
- Rationale: maintains compatibility while enabling incremental migration for users.
- Alternative considered: hard switch to Webhook-only bootstrap. Rejected because it breaks existing flows and increases migration risk.

2. Introduce a dedicated webhook trigger endpoint mapped to Webhook Node identifiers.
- Decision: backend exposes a trigger path that resolves flow + node by a stable webhook identifier stored in node config.
- Rationale: simple integration model for external callers and clear ownership of each trigger.
- Alternative considered: flow-level single endpoint without node mapping. Rejected because it reduces flexibility for flows with multiple entry points.

3. Normalize webhook request into canonical execution input before routing.
- Decision: convert webhook payload and request metadata into the same internal task input contract used by existing routing.
- Rationale: minimizes changes in routing/agent execution layers and reuses existing logic.
- Alternative considered: separate webhook-specific routing branch. Rejected due to duplicated behavior and higher maintenance cost.

4. Persist webhook-origin metadata in run artifacts.
- Decision: store source type, trigger identifier, timestamp, and correlation/request id in run metadata.
- Rationale: enables observability and supports debugging across mixed bootstrap modes.
- Alternative considered: only log metadata in transient stream events. Rejected because historical traceability is required.

## Risks / Trade-offs

- [Webhook endpoint abuse / unsolicited traffic] -> Mitigation: strict path resolution, input validation, rate limiting and auth hardening in follow-up changes.
- [Ambiguous bootstrap selection when both Task and Webhook nodes exist] -> Mitigation: explicit source context in run request path and deterministic validation precedence.
- [Metadata schema drift between bootstrap modes] -> Mitigation: define a canonical run metadata contract with optional source-specific fields.
- [Operational debugging complexity for asynchronous webhook runs] -> Mitigation: include correlation id in accepted response and persisted artifacts.

## Migration Plan

1. Add backend schema and persistence support for Webhook Node bootstrap identifiers and run source metadata.
2. Introduce webhook trigger endpoint and bootstrap normalization pipeline.
3. Add frontend Webhook Node type and configuration UX for endpoint discovery/copy.
4. Update execution validation to accept supported bootstrap sources (Task or Webhook).
5. Roll out tests covering Task Node-only, Webhook-only, and invalid bootstrap graphs.
6. Rollback strategy: disable webhook trigger routing and keep Task Node path active (no migration required for existing flows).

## Open Questions

- Should webhook endpoints require secret-based verification in this first release or in a dedicated security hardening change?
- What payload-to-task mapping defaults should be applied when webhook body does not include an explicit task list?
- Should one flow support multiple webhook bootstrap nodes with independent endpoint lifecycle controls in UI?
