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
| `docs.decision-record` | contract-smoke | not-targeted | not-targeted | run-smoke |
| `docs.migration-guide` | not-targeted | contract-smoke | not-targeted | run-smoke |
| `docs.operating-handbook` | not-targeted | contract-smoke | not-targeted | run-smoke |
| `docs.postmortem` | contract-smoke | not-targeted | not-targeted | run-smoke |
| `engineering.api-contract-change` | not-targeted | target | contract-smoke | run-smoke |
| `engineering.bug-reproduction-lab` | not-targeted | contract-smoke | not-targeted | run-smoke |
| `engineering.ci-failure-diagnosis` | not-targeted | contract-smoke | target | run-smoke |
| `engineering.dead-code-retirement` | not-targeted | contract-smoke | not-targeted | run-smoke |
| `engineering.dependency-upgrade` | not-targeted | target | contract-smoke | run-smoke |
| `engineering.docs-from-diff` | not-targeted | contract-smoke | not-targeted | run-smoke |
| `engineering.flaky-test-stabilization` | not-targeted | contract-smoke | not-targeted | run-smoke |
| `engineering.issue-to-verified-pr` | target | contract-smoke | target | run-smoke |
| `engineering.large-refactor-safe-plan` | not-targeted | contract-smoke | target | run-smoke |
| `engineering.pr-review-and-risk-notes` | not-targeted | target | contract-smoke | run-smoke |
| `engineering.schema-evolution` | not-targeted | contract-smoke | target | run-smoke |
| `general.human-in-the-loop-review` | contract-smoke | target | target | run-smoke |
| `ops.adapter-certification` | target | target | contract-smoke | run-smoke |
| `ops.flow-intake-and-routing` | contract-smoke | target | not-targeted | run-smoke |
| `ops.capability-negotiation` | target | target | contract-smoke | run-smoke |
| `ops.event-and-evidence-bridge` | target | contract-smoke | target | run-smoke |
| `ops.flow-version-upgrade` | contract-smoke | target | target | run-smoke |
| `orchestration.agent-quality-review` | not-targeted | not-targeted | contract-smoke | run-smoke |
| `orchestration.handoff-and-resume` | target | contract-smoke | not-targeted | run-smoke |
| `orchestration.parallel-work-claiming` | contract-smoke | target | not-targeted | run-smoke |
| `orchestration.swarm-execution` | not-targeted | contract-smoke | target | run-smoke |
| `orchestration.tool-creation` | not-targeted | target | contract-smoke | run-smoke |
| `proof.evidence-bundle-export` | not-targeted | not-targeted | contract-smoke | run-smoke |
| `proof.patch-risk-classification` | not-targeted | target | contract-smoke | run-smoke |
| `proof.verified-patch-acceptance` | not-targeted | not-targeted | contract-smoke | run-smoke |
| `research.codebase-orientation` | not-targeted | contract-smoke | not-targeted | run-smoke |
| `research.deep-research-report` | target | target | not-targeted | target |
| `research.library-evaluation` | contract-smoke | target | not-targeted | run-smoke |
| `research.source-backed-brief` | contract-smoke | target | not-targeted | run-smoke |
| `security.connector-grant-review` | contract-smoke | not-targeted | target | run-smoke |
| `security.policy-exception` | contract-smoke | not-targeted | target | run-smoke |
| `security.supply-chain-audit` | not-targeted | contract-smoke | target | run-smoke |
| `security.threat-modeling` | target | target | contract-smoke | run-smoke |
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
- `ops.adapter-certification` has a standalone valid run bundle at `examples/runs/adapter-certification.run.json`.
- `engineering.issue-to-verified-pr` has a standalone valid run bundle at `examples/runs/issue-to-verified-pr.run.json`.
- `proof.verified-patch-acceptance` has a standalone valid run bundle at `examples/runs/verified-patch-acceptance.run.json`.
- `engineering.ci-failure-diagnosis` has a standalone valid run bundle at `examples/runs/ci-failure-diagnosis.run.json`.
- `engineering.pr-review-and-risk-notes` has a standalone valid run bundle at `examples/runs/pr-review-and-risk-notes.run.json`.
- `orchestration.parallel-work-claiming` has a standalone valid run bundle at `examples/runs/parallel-work-claiming.run.json`.
- `security.supply-chain-audit` has a standalone valid run bundle at `examples/runs/supply-chain-audit.run.json`.
- `research.source-backed-brief` has a standalone valid run bundle at `examples/runs/source-backed-brief.run.json`.
- `engineering.bug-reproduction-lab` has a standalone valid run bundle at `examples/runs/bug-reproduction-lab.run.json`.
- `engineering.dependency-upgrade` has a standalone valid run bundle at `examples/runs/dependency-upgrade.run.json`.
- `docs.decision-record` has a standalone valid run bundle at `examples/runs/decision-record.run.json`.
- `docs.postmortem` has a standalone valid run bundle at `examples/runs/postmortem.run.json`.
- `orchestration.handoff-and-resume` has a standalone valid run bundle at `examples/runs/handoff-and-resume.run.json`.
- `security.threat-modeling` has a standalone valid run bundle at `examples/runs/threat-modeling.run.json`.
- `proof.evidence-bundle-export` has a standalone valid run bundle at `examples/runs/evidence-bundle-export.run.json`.
- `orchestration.agent-quality-review` has a standalone valid run bundle at `examples/runs/agent-quality-review.run.json`.
- `research.codebase-orientation` has a standalone valid run bundle at `examples/runs/codebase-orientation.run.json`.
- `engineering.schema-evolution` has a standalone valid run bundle at `examples/runs/schema-evolution.run.json`.
- `engineering.dead-code-retirement` has a standalone valid run bundle at `examples/runs/dead-code-retirement.run.json`.
- `security.connector-grant-review` has a standalone valid run bundle at `examples/runs/connector-grant-review.run.json`.
- `engineering.docs-from-diff` has a standalone valid run bundle at `examples/runs/docs-from-diff.run.json`.
- `engineering.flaky-test-stabilization` has a standalone valid run bundle at `examples/runs/flaky-test-stabilization.run.json`.
- `research.library-evaluation` has a standalone valid run bundle at `examples/runs/library-evaluation.run.json`.
- `orchestration.swarm-execution` has a standalone valid run bundle at `examples/runs/swarm-execution.run.json`.
- `proof.patch-risk-classification` has a standalone valid run bundle at `examples/runs/patch-risk-classification.run.json`.
- `docs.migration-guide` has a standalone valid run bundle at `examples/runs/migration-guide.run.json`.
- `ops.flow-version-upgrade` has a standalone valid run bundle at `examples/runs/flow-version-upgrade.run.json`.
- `engineering.api-contract-change` has a standalone valid run bundle at `examples/runs/api-contract-change.run.json`.
- `engineering.large-refactor-safe-plan` has a standalone valid run bundle at `examples/runs/large-refactor-safe-plan.run.json`.
- `orchestration.tool-creation` has a standalone valid run bundle at `examples/runs/tool-creation.run.json`.
- `security.policy-exception` has a standalone valid run bundle at `examples/runs/policy-exception.run.json`.
- `docs.operating-handbook` has a standalone valid run bundle at `examples/runs/operating-handbook.run.json`.
- Repo-local adapter smoke manifests live under `examples/adapters/`.
