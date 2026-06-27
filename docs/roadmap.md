# Roadmap

This roadmap tracks the full project from current bootstrap to stable optional consumption by independent projects.

## Phase 0: Repository foundation

Status: complete.

Goals:

- Create the repository structure.
- Add schema-backed flow definitions.
- Add `flowctl validate`, `flowctl list`, and `flowctl graph`.
- Add initial flows, templates, docs, tests, and CI.

Acceptance gates:

- `flowctl validate` passes.
- `pytest` passes.
- GitHub Actions pass on `main`.
- GitHub metadata is correct.

## Phase 1: Operating handbook and evidence validation

Status: complete.

Goals:

- Document complete goals, roadmap, workflows, task backlog, best practices, and release process.
- Add changelog management.
- Add event validation support to `flowctl`.
- Add CI coverage for event validation.
- Add run bundle validation and a first completed run example.
- Add flow catalog reporting.

Acceptance gates:

- Docs index links every process document.
- `CHANGELOG.md` has an unreleased section.
- `flowctl validate-event` validates sample events.
- `flowctl validate-run` validates sample run bundles.
- `flowctl report` summarizes catalog maturity.
- CI runs flow validation, event validation, run validation, report generation, graph export, and tests.

## Phase 2: Flow quality and catalog maturity

Status: complete.

Goals:

- Expand flow metadata reports.
- Add stronger semantic validation for contracts, artifacts, and required gate evidence names.
- Add examples for every production flow.
- Add at least one invalid fixture for every semantic validation class.

Acceptance gates:

- `flowctl report` can summarize flow maturity and optional consumers.
- Every production flow has a sample input and expected output contract.
- Every production flow has a maturity rubric with a documented path to promotion.
- Required gate evidence references are machine-checkable.
- Semantic validation classes have invalid regression fixtures.

## Phase 3: Optional adapter smoke tests

Status: complete.

Goals:

- Implement a minimal optional loader in ThinClaw.
- Implement a minimal optional worker and sandbox mapping in NilCore.
- Implement a minimal optional verifier mapping in CrustCore.
- Add adapter smoke-test evidence under `examples/`.

Acceptance gates:

- Repo-local adapter smoke manifests validate for ThinClaw, NilCore, and CrustCore.
- ThinClaw can create routine state from a selected flow and persist approval metadata with the source flow version.
- NilCore can dispatch `agent_task` nodes as subtasks and run `tool` plans through its sandbox boundary.
- CrustCore can map required gates to verifier-owned criteria and reject incomplete completion evidence.
- Full product deployment and long-lived event emission remain Phase 7 work.

## Phase 4: Run evidence and replay

Status: complete.

Goals:

- Expand run bundle layout for richer artifacts.
- Validate multi-file event streams against source flow metadata.
- Add example completed runs for human review and multi-agent supervisor flows.

Acceptance gates:

- A run can be replayed from event JSON.
- Missing required gate evidence fails validation.
- Flow version mismatches fail validation.
- Passed gate evidence matches declared gate evidence refs.
- Multi-file event streams validate against source flow metadata.

## Phase 5: Release packaging

Status: complete.

Goals:

- Add release tags.
- Publish schema bundles as release assets if needed.
- Add compatibility matrix.
- Decide whether to publish `flowctl` to PyPI or keep it repo-local.

Acceptance gates:

- Release package build passes.
- `flowctl release-check` passes.
- Release checklist passes.
- Changelog has dated release notes.
- Consuming projects can pin by tag.

## Phase 6: Stable flow promotion

Status: planned.

Goals:

- Promote proven flows from `experimental` or `preview` to `stable`.
- Require adapter smoke evidence for every listed optional consumer.
- Enforce deprecation policy for replaced flows.

Acceptance gates:

- Stability promotion PR links adapter evidence.
- All stable flows have compatibility notes.
- Deprecated flows include migration guidance.

## Phase 7: Project-specific deployment

Status: planned.

Goals:

- Optionally use `agentic-flows` in ThinClaw, NilCore, and CrustCore project workflows.
- Create project-specific flow packs only when a reusable flow is insufficient.
- Keep custom project logic in consuming repos unless it generalizes.

Acceptance gates:

- Each participating project has at least one real workflow loaded from this repo.
- The workflow produces validated run events.
- Integration lessons are fed back into docs or schema changes.
