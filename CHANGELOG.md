# Changelog

All notable changes to this project will be documented in this file.

This project follows semantic versioning for releases and keeps flow compatibility notes in the relevant release section.

## Unreleased

### Added

- Added the `ops.flow-intake-and-routing` reusable flow with a standalone run bundle and a ThinClaw contract smoke.
- Added the `ops.capability-negotiation` reusable flow with a standalone run bundle and a CrustCore contract smoke.
- Added the `ops.event-and-evidence-bridge` reusable flow with a standalone run bundle, a multi-file event stream, and a NilCore contract smoke.
- Added the `ops.adapter-certification` reusable flow with a standalone run bundle and a CrustCore contract smoke.
- Added the `engineering.issue-to-verified-pr` reusable flow with a standalone run bundle and a NilCore contract smoke.
- Added the `proof.verified-patch-acceptance` reusable flow with a standalone run bundle and a CrustCore contract smoke.
- Added the `engineering.ci-failure-diagnosis` reusable flow with a standalone run bundle and a NilCore contract smoke.
- Added the `engineering.pr-review-and-risk-notes` reusable flow with a standalone run bundle and a CrustCore contract smoke.
- Added the `security.supply-chain-audit` reusable flow with a standalone run bundle and a NilCore contract smoke.
- Added the `orchestration.parallel-work-claiming` reusable flow with a standalone run bundle and a ThinClaw contract smoke.
- Added the `research.source-backed-brief` reusable flow with a standalone run bundle and a ThinClaw contract smoke.
- Added the `engineering.bug-reproduction-lab` reusable flow with a standalone run bundle and a NilCore contract smoke.
- Added the `engineering.dependency-upgrade` reusable flow with a standalone run bundle and a CrustCore contract smoke.
- Added the `docs.decision-record` reusable flow with a standalone run bundle and a ThinClaw contract smoke.
- Added the `docs.postmortem` reusable flow with a standalone run bundle and a ThinClaw contract smoke.
- Added the `orchestration.handoff-and-resume` reusable flow (exercising the `handoff` node type) with a standalone run bundle and a NilCore contract smoke.
- Added the `security.threat-modeling` reusable flow with a standalone run bundle and a CrustCore contract smoke.
- Added the `proof.evidence-bundle-export` reusable flow with a standalone run bundle and a CrustCore contract smoke.
- Added the `orchestration.agent-quality-review` reusable flow with a standalone run bundle and a CrustCore contract smoke.
- Added the `research.codebase-orientation` reusable flow with a standalone run bundle and a NilCore contract smoke.
- Added the `engineering.schema-evolution` reusable flow with a standalone run bundle and a NilCore contract smoke.
- Added the `engineering.dead-code-retirement` reusable flow with a standalone run bundle and a NilCore contract smoke.
- Added the `security.connector-grant-review` reusable flow (approval-gated destructive grants) with a standalone run bundle and a ThinClaw contract smoke.
- Added the `engineering.docs-from-diff` reusable flow with a standalone run bundle and a NilCore contract smoke.
- Added the `engineering.flaky-test-stabilization` reusable flow with a standalone run bundle and a NilCore contract smoke.
- Added the `research.library-evaluation` reusable flow with a standalone run bundle and a ThinClaw contract smoke.
- Added the `orchestration.swarm-execution` reusable flow with a standalone run bundle and a NilCore contract smoke.
- Added the `proof.patch-risk-classification` reusable flow (fail-closed risk routing) with a standalone run bundle and a CrustCore contract smoke.
- Added the `docs.migration-guide` reusable flow with a standalone run bundle and a NilCore contract smoke.
- Added `docs/buildable-now.md`, an evidence-backed assessment of which backlog workflows can be built end-to-end now.

### Changed

- Reworked the README into a full project landing page with vision, catalog status, workflow backlog links, runtime-boundary framing, and validation guidance.
- Expanded the catalog to thirty-five reusable workflows across the integration spine, engineering, proof, security, orchestration, research, and documentation, and recorded their compatibility states.

## 0.1.1 - 2026-06-27

### Added

- Documented first optional adapter seams in the independent ThinClaw, NilCore, and CrustCore repos.

## 0.1.0 - 2026-06-27

### Added

- Initialized the `agentic-flows` repository.
- Added schemas for flows, nodes, and events.
- Added the `flowctl` CLI with flow validation, listing, and graph export.
- Added initial reusable flows for coding, research, collaboration, and review workflows.
- Added starter templates for feature, refactor, and research report workflows.
- Added adapter contract sketches for ThinClaw, NilCore, and CrustCore.
- Added GitHub Actions validation.
- Added the project operating handbook under `docs/`.
- Added changelog and release management guidance.
- Added `flowctl validate-event` for event artifact validation.
- Added CI coverage for event validation.
- Added `schemas/run.schema.json` for completed run bundles.
- Added `flowctl validate-run` for source-flow, event, output, and gate-evidence validation.
- Added `flowctl report` for catalog maturity and optional-consumer summaries.
- Added `flowctl validate-samples` for flow input/output sample validation.
- Added sample input and expected-output files for every production flow.
- Added semantic validation for node requirements and required contract outputs.
- Added semantic validation for required quality gate `evidence_refs`.
- Added semantic regression fixtures for graph, gate, evidence, and deprecation validation rules.
- Added optional `deprecated_by` and `migration` metadata for future flow replacements.
- Added maturity rubrics to production flow READMEs.
- Added run evidence ids and validation that passed gate evidence matches declared gate `evidence_refs`.
- Added `flowctl replay` for validated run-bundle timelines.
- Added `flowctl changelog-check` and `flowctl check-links` with CI coverage.
- Added `flowctl normalize` for deterministic flow YAML ordering with CI coverage.
- Added `schemas/event-stream.schema.json` and `flowctl validate-stream` for multi-file event streams.
- Added `schemas/adapter-smoke.schema.json`, `flowctl validate-adapter-smoke`, and repo-local adapter smoke examples.
- Added `flowctl package-release` for deterministic release package builds.
- Added `flowctl release-check` for deprecation and stable-promotion release gates.
- Added a completed feature implementation run example.
- Added completed standalone run examples for human review and multi-agent supervisor flows.
- Added a compatibility matrix and run-bundle guidance.
- Added a release notes template.
- Added a pull request checklist for validation and independent-consumer framing.
- Clarified that ThinClaw, NilCore, and CrustCore are independent optional consumers, not an already-integrated stack.
