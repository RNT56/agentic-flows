# Task backlog

Use this file as the project-level task board. Keep tasks small enough to finish in a focused PR.

## Current implementation lane

- [x] Document full operating handbook.
- [x] Add changelog management guidance.
- [x] Add event validation command to `flowctl`.
- [x] Add CI event validation coverage.
- [x] Add `flowctl report` for maturity and compatibility summaries.
- [x] Add completed run bundle examples.
- [x] Add `flowctl validate-run` for required gate evidence.
- [x] Add human review completed run example.
- [x] Add multi-agent supervisor completed run example.

## Flow catalog tasks

- [x] Add sample inputs for every production flow.
- [x] Add expected outputs for every production flow.
- [ ] Add a flow maturity rubric to each production flow README.
- [ ] Add flow ownership metadata once real owners exist.
- [ ] Split any project-specific behavior out of reusable flows.

## Schema tasks

- [ ] Add optional `deprecated_by` and `migration` fields.
- [x] Add schema coverage for run bundles.
- [x] Add semantic validation that node `requires` reference declared artifacts or prior `produces`.
- [x] Add semantic validation that outputs are produced by reachable nodes.
- [ ] Add semantic validation that quality gate evidence names are declared artifacts or events.

## Tooling tasks

- [x] Add `flowctl report`.
- [x] Add `flowctl validate-run`.
- [ ] Add `flowctl normalize` for deterministic YAML ordering.
- [ ] Add `flowctl changelog-check` before first tagged release.
- [ ] Add markdown link checking once docs stabilize.

## Optional adapter tasks

- [ ] ThinClaw: optionally load a flow into routine state.
- [ ] ThinClaw: persist approval decisions with source flow version.
- [ ] NilCore: optionally dispatch `agent_task` nodes as worker jobs.
- [ ] NilCore: run `tool` nodes in sandboxed execution.
- [ ] CrustCore: optionally map required gates to verifier-owned completion criteria.
- [ ] CrustCore: reject patch completion when evidence is incomplete.

## Release tasks

- [ ] Create first release candidate tag after Phase 1.
- [x] Add compatibility matrix.
- [x] Add release notes template.
- [ ] Decide whether `flowctl` should be published outside this repo.
- [ ] Add deprecation policy checks before any stable release.
