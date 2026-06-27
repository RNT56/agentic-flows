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
- [x] Add quality gate evidence reference validation.
- [x] Add maturity rubrics for production flow READMEs.
- [x] Add optional deprecation and migration metadata.
- [x] Add semantic regression fixtures for flow quality rules.
- [x] Add run replay summaries for completed run bundles.
- [x] Match passed gate evidence to declared gate evidence refs.
- [x] Add changelog and local Markdown link checks.
- [x] Add deterministic flow normalization.
- [x] Add multi-file event stream validation.

## Flow catalog tasks

- [x] Add sample inputs for every production flow.
- [x] Add expected outputs for every production flow.
- [x] Add a flow maturity rubric to each production flow README.
- [ ] Add flow ownership metadata once real owners exist.
- [ ] Split any project-specific behavior out of reusable flows.

## Schema tasks

- [x] Add optional `deprecated_by` and `migration` fields.
- [x] Add schema coverage for run bundles.
- [x] Add semantic validation that node `requires` reference declared artifacts or prior `produces`.
- [x] Add semantic validation that outputs are produced by reachable nodes.
- [x] Add semantic validation that quality gate evidence names are declared artifacts or events.
- [x] Add invalid fixtures for semantic validation classes.

## Tooling tasks

- [x] Add `flowctl report`.
- [x] Add `flowctl validate-run`.
- [x] Add `flowctl replay`.
- [x] Add `flowctl normalize` for deterministic YAML ordering.
- [x] Add `flowctl changelog-check` before first tagged release.
- [x] Add markdown link checking once docs stabilize.

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

## Run evidence tasks

- [x] Validate passed gate evidence against source flow `evidence_refs`.
- [x] Add replay summaries for run bundles.
- [x] Validate external multi-file event streams.
