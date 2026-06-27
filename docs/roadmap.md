# Roadmap

This roadmap tracks the full project from current bootstrap to stable cross-core use.

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

Status: in progress.

Goals:

- Document complete goals, roadmap, workflows, task backlog, best practices, and release process.
- Add changelog management.
- Add event validation support to `flowctl`.
- Add CI coverage for event validation.

Acceptance gates:

- Docs index links every process document.
- `CHANGELOG.md` has an unreleased section.
- `flowctl validate-event` validates sample events.
- CI runs flow validation, event validation, graph export, and tests.

## Phase 2: Flow quality and catalog maturity

Status: planned.

Goals:

- Add flow metadata reports.
- Add stronger semantic validation for contracts, artifacts, and required gate evidence names.
- Add examples for every production flow.
- Add at least one invalid fixture for every semantic validation class.

Acceptance gates:

- `flowctl report` can summarize flow maturity.
- Every production flow has a sample input and expected output contract.
- Every preview flow has a documented path to stability.

## Phase 3: Runtime adapter smoke tests

Status: planned.

Goals:

- Implement or document a minimal loader in ThinClaw.
- Implement or document a minimal loader in NilCore.
- Implement or document a minimal verifier mapping in CrustCore.
- Add adapter smoke-test evidence under `examples/`.

Acceptance gates:

- Each core can load at least one supported flow without per-flow custom parsing.
- Each core can reject unsupported capabilities.
- Each core can emit or consume events compatible with `schemas/event.schema.json`.

## Phase 4: Run evidence and replay

Status: planned.

Goals:

- Define run bundle layout.
- Validate event streams against source flow metadata.
- Add `flowctl validate-run` for event streams and required gate evidence.
- Add example completed runs for feature implementation and human review.

Acceptance gates:

- A run can be replayed from event JSON.
- Missing required gate evidence fails validation.
- Flow version mismatches fail validation.

## Phase 5: Release packaging

Status: planned.

Goals:

- Add release tags.
- Publish schema bundles as release assets if needed.
- Add compatibility matrix.
- Decide whether to publish `flowctl` to PyPI or keep it repo-local.

Acceptance gates:

- Release checklist passes.
- Changelog has dated release notes.
- Consuming repos can pin by tag.

## Phase 6: Stable flow promotion

Status: planned.

Goals:

- Promote proven flows from `experimental` or `preview` to `stable`.
- Require adapter smoke evidence for every listed core.
- Add deprecation policy for replaced flows.

Acceptance gates:

- Stability promotion PR links adapter evidence.
- All stable flows have compatibility notes.
- Deprecated flows include migration guidance.

## Phase 7: Project-specific deployment

Status: planned.

Goals:

- Use `agentic-flows` in ThinClaw, NilCore, and CrustCore project workflows.
- Create project-specific flow packs only when a reusable flow is insufficient.
- Keep custom project logic in consuming repos unless it generalizes.

Acceptance gates:

- Each core has at least one real workflow loaded from this repo.
- The workflow produces validated run events.
- Integration lessons are fed back into docs or schema changes.

