# Compatibility matrix

This matrix records intended and proven compatibility with independent optional consumers.

States:

- `target`: designed with this consumer in mind, but no adapter evidence exists.
- `contract-smoke`: repo-local manifest validates capabilities, node mappings, and target-core run evidence.
- `adapter-smoke`: consumer can load and validate the flow.
- `run-smoke`: consumer can produce a valid run bundle.
- `stable`: consumer has repeatable adapter and run evidence.

Current status:

| Flow | ThinClaw | NilCore | CrustCore | Standalone |
| --- | --- | --- | --- | --- |
| `coding.feature-implementation` | target | target | contract-smoke | run-smoke |
| `coding.refactor-and-verify` | target | target | target | target |
| `coding.security-audit` | target | target | target | target |
| `collaboration.multi-agent-supervisor` | target | contract-smoke | not-targeted | run-smoke |
| `general.human-in-the-loop-review` | contract-smoke | target | target | run-smoke |
| `ops.flow-intake-and-routing` | contract-smoke | target | not-targeted | run-smoke |
| `ops.capability-negotiation` | target | target | contract-smoke | run-smoke |
| `ops.event-and-evidence-bridge` | target | contract-smoke | target | run-smoke |
| `research.deep-research-report` | target | target | not-targeted | target |
| `template.coding-feature` | not-targeted | not-targeted | not-targeted | target |
| `template.coding-refactor` | not-targeted | not-targeted | not-targeted | target |
| `template.research-report` | not-targeted | not-targeted | not-targeted | target |

## Update rules

- Move from `target` to `contract-smoke` when this repo has a validated adapter smoke manifest.
- Move from `contract-smoke` to `adapter-smoke` only when the independent project can load the source flow.
- Move from `adapter-smoke` to `run-smoke` only when that project can emit a valid run bundle.
- Move to `stable` only after repeatable evidence exists and the flow stability is updated.
- Use `not-targeted` when the flow intentionally does not list the consumer in `runtime.supported_cores`.

## Current evidence

- `coding.feature-implementation` has a standalone valid run bundle at `examples/runs/feature-implementation.run.json`.
- `general.human-in-the-loop-review` has a standalone valid run bundle at `examples/runs/human-in-the-loop-review.run.json`.
- `collaboration.multi-agent-supervisor` has a standalone valid run bundle at `examples/runs/multi-agent-supervisor.run.json`.
- `ops.flow-intake-and-routing` has a standalone valid run bundle at `examples/runs/flow-intake-and-routing.run.json`.
- `ops.capability-negotiation` has a standalone valid run bundle at `examples/runs/capability-negotiation.run.json`.
- `ops.event-and-evidence-bridge` has a standalone valid run bundle at `examples/runs/event-and-evidence-bridge.run.json` and a multi-file event stream under `examples/streams/event-and-evidence-bridge/`.
- Repo-local adapter smoke manifests live under `examples/adapters/`.
