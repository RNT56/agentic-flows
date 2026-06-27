# Task backlog

Use this file as the project-level task board. Keep tasks small enough to finish in a focused PR.

## Current implementation lane

- [x] Document full operating handbook.
- [x] Add changelog management guidance.
- [x] Add event validation command to `flowctl`.
- [x] Add CI event validation coverage.
- [ ] Add `flowctl report` for maturity and compatibility summaries.
- [ ] Add completed run bundle examples.
- [ ] Add `flowctl validate-run` for required gate evidence.

## Flow catalog tasks

- [ ] Add sample inputs for every production flow.
- [ ] Add expected outputs for every production flow.
- [ ] Add a flow maturity rubric to each production flow README.
- [ ] Add flow ownership metadata once real owners exist.
- [ ] Split any project-specific behavior out of reusable flows.

## Schema tasks

- [ ] Add optional `deprecated_by` and `migration` fields.
- [ ] Add schema coverage for run bundles.
- [ ] Add semantic validation that node `requires` reference declared artifacts or prior `produces`.
- [ ] Add semantic validation that outputs are produced by reachable nodes.
- [ ] Add semantic validation that quality gate evidence names are declared artifacts or events.

## Tooling tasks

- [ ] Add `flowctl report`.
- [ ] Add `flowctl validate-run`.
- [ ] Add `flowctl normalize` for deterministic YAML ordering.
- [ ] Add `flowctl changelog-check` before first tagged release.
- [ ] Add markdown link checking once docs stabilize.

## Adapter tasks

- [ ] ThinClaw: load a flow into routine state.
- [ ] ThinClaw: persist approval decisions with source flow version.
- [ ] NilCore: dispatch `agent_task` nodes as worker jobs.
- [ ] NilCore: run `tool` nodes in sandboxed execution.
- [ ] CrustCore: map required gates to verifier-owned completion criteria.
- [ ] CrustCore: reject patch completion when evidence is incomplete.

## Release tasks

- [ ] Create first release candidate tag after Phase 1.
- [ ] Add compatibility matrix.
- [ ] Add release notes template.
- [ ] Decide whether `flowctl` should be published outside this repo.
- [ ] Add deprecation policy checks before any stable release.

