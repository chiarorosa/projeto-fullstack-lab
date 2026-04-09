## Why

Execution currently starts only from Task Node input, which requires manual bootstrapping inside the editor and limits real-world integrations. Adding a Webhook bootstrap path enables external systems to trigger user-defined flows directly, improving adoption for event-driven use cases.

## What Changes

- Add a Webhook bootstrap node that can start flow execution from inbound HTTP webhook calls.
- Add backend webhook execution entry handling that resolves the target flow and maps request payload into execution input.
- Keep Task Node bootstrap support, but update bootstrap validation/routing rules to support both Task Node and Webhook Node entry strategies.
- Expose run-time metadata so webhook-triggered runs remain traceable with source and request context.

## Capabilities

### New Capabilities
- `webhook-bootstrap`: Define webhook-based flow bootstrapping, request validation, payload mapping, and execution trigger behavior.

### Modified Capabilities
- `agent-task-routing`: Update bootstrap requirements so execution can be started by a valid Webhook Node in addition to Task Node.
- `intelligent-task-routing`: Broaden routing assumptions so task selection and routing logic work for tasks originating from supported bootstrap sources, including webhooks.

## Impact

- Frontend node graph editor (new Webhook node type and configuration UI).
- Backend execution bootstrap and API routing layer (new webhook trigger endpoint and flow dispatch path).
- Execution validation and routing metadata contracts used by stream events and run artifacts.
- Test coverage for webhook-triggered execution and backward compatibility with Task Node flows.
