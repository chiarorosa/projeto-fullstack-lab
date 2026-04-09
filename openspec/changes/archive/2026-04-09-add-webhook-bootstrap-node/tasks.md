## 1. Backend Webhook Bootstrap Foundation

- [x] 1.1 Add/extend backend data model and persistence to store Webhook Node bootstrap identifiers linked to flow and node ids.
- [x] 1.2 Implement webhook trigger endpoint that resolves webhook identifier to flow bootstrap context and rejects unknown paths.
- [x] 1.3 Implement webhook request validation and canonical payload normalization into execution task input format.

## 2. Execution Bootstrap and Routing Integration

- [x] 2.1 Update bootstrap validation logic to accept at least one supported source (Task Node or Webhook Node) and emit explicit errors when absent.
- [x] 2.2 Integrate webhook bootstrap context into existing execution pipeline so downstream agent routing reuses current task-routing behavior.
- [x] 2.3 Persist webhook-origin metadata (source, trigger id, timestamp, correlation id) into run artifacts and stream metadata.

## 3. Frontend Node and UX Support

- [x] 3.1 Add Webhook Node type to frontend node catalog with configuration fields required for trigger lifecycle.
- [x] 3.2 Implement Webhook Node configuration UI to display/copy trigger endpoint and support identifier regeneration flow.
- [x] 3.3 Update frontend run/execution affordances and validation messaging to reflect dual bootstrap modes.

## 4. Verification and Compatibility

- [x] 4.1 Add backend tests for valid webhook trigger, unknown trigger, malformed payload, and accepted asynchronous execution response.
- [x] 4.2 Add integration tests for Task Node-only, Webhook-only, and mixed-node graphs to ensure bootstrap compatibility.
- [x] 4.3 Add artifact/metadata assertions to verify webhook-triggered runs are distinguishable from Task Node-triggered runs.
