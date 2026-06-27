# Compatibility matrix

This matrix records intended and proven compatibility with independent optional consumers.

States:

- `target`: designed with this consumer in mind, but no adapter evidence exists.
- `adapter-smoke`: consumer can load and validate the flow.
- `run-smoke`: consumer can produce a valid run bundle.
- `stable`: consumer has repeatable adapter and run evidence.

Current status:

| Flow | ThinClaw | NilCore | CrustCore | Standalone |
| --- | --- | --- | --- | --- |
| `coding.feature-implementation` | target | target | target | run-smoke |
| `coding.refactor-and-verify` | target | target | target | target |
| `coding.security-audit` | target | target | target | target |
| `collaboration.multi-agent-supervisor` | target | target | not-targeted | target |
| `general.human-in-the-loop-review` | target | target | target | target |
| `research.deep-research-report` | target | target | not-targeted | target |
| `template.coding-feature` | not-targeted | not-targeted | not-targeted | target |
| `template.coding-refactor` | not-targeted | not-targeted | not-targeted | target |
| `template.research-report` | not-targeted | not-targeted | not-targeted | target |

## Update rules

- Move from `target` to `adapter-smoke` only when the independent project can load the source flow.
- Move from `adapter-smoke` to `run-smoke` only when that project can emit a valid run bundle.
- Move to `stable` only after repeatable evidence exists and the flow stability is updated.
- Use `not-targeted` when the flow intentionally does not list the consumer in `runtime.supported_cores`.

## Current evidence

- `coding.feature-implementation` has a standalone valid run bundle at `examples/runs/feature-implementation.run.json`.

