# Changelog

All notable changes to this project will be documented in this file.

This project follows semantic versioning for releases and keeps flow compatibility notes in the relevant release section.

## Unreleased

### Added

- Added the substance layer to the node schema: optional `instructions`, `command`, `parameters`, `inputs_schema`, `outputs_schema`, and `on_failure` fields so a flow can carry what a consumer or the reference runner needs to execute it. All fields are additive and the existing catalog still validates.
- Added `flowctl run`, a reference runner that executes a flow with built-in local handlers (command subprocesses for `tool`/`command` nodes, structured records for `intake`/`plan`/`decision`/`verifier`/`finalizer`, needs-handler reporting for `agent_task`/`approval`/`handoff`), passes gates only from real produced evidence, and writes a run bundle validated against `schemas/run.schema.json`.
- Added `docs/runnable-flows.md` describing the substance layer, the consumer boundary, and the `flowctl run` execution model, with cross-links from `docs/flow-spec.md`.
- Made `research.codebase-orientation` runnable end-to-end and committed a real produced run bundle under `examples/runs/real/codebase-orientation/` with actual command output as evidence.
- Fleshed `coding.feature-implementation` as the consumable-contract reference (per-node instructions, intake `inputs_schema`, a `test_command` parameter, a command on the checks node, and `on_failure` handling); its `implement` node stays a consumer-supplied `agent_task`.
- Added `flowctl run` regression tests covering command execution, gate evidence, bundle validity, command-failure handling, and needs-handler reporting.
- Rolled the substance layer across the remaining 62 flows: every node now carries operational `instructions`, each intake node declares an `inputs_schema` mirroring its contract inputs, tool nodes that map to a concrete portable command carry a `command`, `parameters`, and `on_failure`, and critical verifier nodes carry failure policies. The change is additive (no contract, edge, gate, observability, runtime, or metadata changes), so all existing sample, run-bundle, and adapter-smoke fixtures still validate.
- Made three more flows runnable end-to-end under `flowctl run` and committed their real run bundles under `examples/runs/real/`: `ops.adapter-certification` (runs `flowctl validate-adapter-smoke`), `proof.verified-patch-acceptance` (runs the verifier-owned test command), and `ops.capability-negotiation` (no-command fail-closed comparison). Added a "Runnable flows today" table to `docs/runnable-flows.md` and a "Runnable" section to each flow's README.
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
- Added the `ops.flow-version-upgrade` reusable flow with a standalone run bundle and a ThinClaw contract smoke.
- Added the `engineering.api-contract-change` reusable flow with a standalone run bundle and a CrustCore contract smoke.
- Added the `engineering.large-refactor-safe-plan` reusable flow with a standalone run bundle and a NilCore contract smoke.
- Added the `orchestration.tool-creation` reusable flow with a standalone run bundle and a CrustCore contract smoke.
- Added the `security.policy-exception` reusable flow (approval-gated bypass) with a standalone run bundle and a ThinClaw contract smoke.
- Added the `docs.operating-handbook` reusable flow with a standalone run bundle and a NilCore contract smoke.
- Added the `security.audit-trail-reconstruction` reusable flow with a standalone run bundle and a CrustCore contract smoke.
- Added the `product.feedback-to-roadmap` reusable flow with a standalone run bundle and a ThinClaw contract smoke.
- Added the `docs.api-reference-refresh` reusable flow with a standalone run bundle and a NilCore contract smoke.
- Added the `research.paper-to-implementation-plan` reusable flow with a standalone run bundle and a NilCore contract smoke.
- Added the `research.market-and-user-value` reusable flow with a standalone run bundle and a ThinClaw contract smoke.
- Added the `orchestration.skill-authoring` reusable flow with a standalone run bundle and a ThinClaw contract smoke.
- Added the `program.research-to-roadmap` reusable flow with a standalone run bundle and a ThinClaw contract smoke.
- Added the `program.knowledge-base-maintenance` reusable flow with a standalone run bundle and a NilCore contract smoke.
- Added the `personal.commitment-ledger` reusable flow with a standalone run bundle and a ThinClaw contract smoke.
- Added the `personal.memory-curation` reusable flow (approval-gated sensitive memory) with a standalone run bundle and a ThinClaw contract smoke.
- Added the `personal.routine-authoring` reusable flow (approval-gated enablement) with a standalone run bundle and a ThinClaw contract smoke.
- Added the `engineering.security-hotfix` reusable flow (approval-gated release) with a standalone run bundle and a CrustCore contract smoke.
- Added the `engineering.repository-bootstrap` reusable flow with a standalone run bundle and a NilCore contract smoke.
- Added the `engineering.monorepo-slice-execution` reusable flow with a standalone run bundle and a NilCore contract smoke.
- Added the `engineering.performance-regression` reusable flow with a standalone run bundle and a CrustCore contract smoke.
- Added the `engineering.issue-backlog-grooming` reusable flow with a standalone run bundle and a ThinClaw contract smoke.
- Added the `proof.release-candidate-audit` reusable flow with a standalone run bundle and a CrustCore contract smoke.
- Added the `security.untrusted-output-routing` reusable flow with a standalone run bundle and a CrustCore contract smoke.
- Added the `security.access-review` reusable flow with a standalone run bundle and a ThinClaw contract smoke.
- Added the `research.technology-radar` reusable flow with a standalone run bundle and a ThinClaw contract smoke.
- Added the `ops.incident-response` reusable flow with a standalone run bundle and a ThinClaw contract smoke.
- Added the `orchestration.self-improvement-loop` reusable flow with a standalone run bundle and a CrustCore contract smoke.
- Added the `program.connector-productionization` reusable flow with a standalone run bundle and a CrustCore contract smoke.
- Added `docs/buildable-now.md`, an evidence-backed assessment of which backlog workflows can be built end-to-end now.

### Changed

- Redefined the project goal: `agentic-flows` is now a library of **runnable, consumable** workflows that carry a substance layer (per-node instructions, structured I/O, parameters, concrete commands, failure handling), executed by a consuming runtime or the bundled reference runner. Updated `docs/goals.md` and the README accordingly and added [docs/runnable-flows.md](docs/runnable-flows.md).
- Reworked the README into a full project landing page with vision, catalog status, workflow backlog links, runtime-boundary framing, and validation guidance.
- Expanded the catalog to sixty-four reusable workflows, completing all 46 build-now candidates plus the 12 strongest contract-first backlog flows (security hotfix, repo bootstrap, monorepo slice, performance regression, backlog grooming, release-candidate audit, untrusted-output routing, access review, technology radar, incident response, self-improvement loop, connector productionization), and recorded their compatibility states.

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
