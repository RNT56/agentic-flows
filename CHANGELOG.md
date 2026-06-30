# Changelog

All notable changes to this project will be documented in this file.

This project follows semantic versioning for releases and keeps flow compatibility notes in the relevant release section.

## Unreleased

### Added

- Added the `agentic-flows/v1.1` spec generation (a strict, additive superset of `v1`) introducing the `flow_ref` node type for sub-flow composition, plus optional `ref`/`with`/`expose`/`environment`/`iteration`/`fan_out` node fields, a top-level `parameters` block, `judgment`/`acceptance`/`probe` gate types, gate `evidence_class`, and a `sub_runs` array on run bundles with a `sub_run` link on events. Existing `v1` flows validate unchanged.
- Added sub-flow composition support to `flowctl`: a flow catalog and semver-range resolver, a new `flowctl check-composition` command (static `flow_ref` resolution, binding, capability, core, and cycle checks), and recursive child run-bundle validation folded into `flowctl validate-run` (a parent's `subflows-passed` gate now requires each `flow_ref` child to recursively validate and complete with its own required gates passed).
- Added `evidence_class` enforcement to `flowctl validate-run`: a gate that declares `evidence_class` (exact) or `evidence_class_min` (floor) is satisfied only by passed-gate evidence carrying a class that meets it, along the ordering `deterministic` < `fixture` < `sandbox-run` < `judgment` < `external-production`; and a `standalone` run that emits `sandbox-run` or `external-production` evidence is rejected. The new `engineering`, `design`, and `program` flows declare honest evidence classes on their gates.
- Added `parameters` enforcement to `flowctl validate`: every `{{param.x}}` reference in a gate `command` or a `flow_ref` node's `with` bindings must resolve to a declared parameter, and `enum` parameters must declare a non-empty `choices` list. `engineering.backend-service` now declares its stack build and test commands as parameters, demonstrating one parameterized flow per concern rather than a separate flow per stack.
- Added reviewer-identity enforcement for `judgment` and `acceptance` gates to `flowctl validate-run`: a passed `gate.completed` event must carry a `payload.reviewer_id` that is not one of the flow's producing agents (no self-review), mirroring `proof.verified-patch-acceptance`. The design, frontend, and program review gates are now `judgment` gates with enumerated `criteria` and reviewer evidence.
- Added bounds enforcement for the `iteration` and `fan_out` node primitives to `flowctl validate`: an `iteration` loop must declare an integer `max_iterations` and reference a real gate in its `until`, and a `fan_out` must declare a non-empty `over`, a `cardinality` with an integer `min`, and an `aggregate` rule. `engineering.frontend-build` now bounds its implement loop and `engineering.backend-service` fans out its endpoint tests.
- Added the v1.1 composition programs that `flow_ref` over the new build-track leaves: `program.service-from-spec` (Design -> Build -> Verify across `design.service-to-spec`, `engineering.backend-service`, and `ops.integration-test-lab`), `program.feature-to-release` (Build -> Ship -> Govern across `engineering.issue-to-verified-pr` and `ops.ephemeral-preview-deploy` with an independent release `acceptance` gate — the honest substitute for an end-to-end release autopilot, stopping at a preview deploy), and `program.security-hardening-campaign` (the first flow to combine `fan_out` + `iteration` + `flow_ref`, inventorying findings, hardening each under a bounded per-finding loop, and exporting an audit trail). Each ships a sample and a run bundle whose child sub-runs are recursively validated.
- Added the build-track leaf flows: `design.service-to-spec` (a Design-phase sibling whose spec output feeds `engineering.backend-service`, gated by a judgment sign-off with reviewer-identity), `engineering.cli-tool` (a stack-parameterized CLI build with a bounded `iteration` loop and golden-output gate), `engineering.library-package` (an ecosystem-parameterized package build that stops at publish-ready with a reviewed public-API/semver gate), and `infra.iac-module` (a new `infra` category — plan/policy gates plus a `sandbox-run` apply against an ephemeral environment with an approval node for destructive change). Each ships a sample and a run bundle.
- Added the first wave of v1.1-native operations flows that exercise the sandbox/provenance spine: `ops.ephemeral-preview-deploy` (the catalog's first `probe` gate; deploys to a throwaway preview and probes health as honest sandbox-run evidence, never production), `ops.integration-test-lab` (runs an integration suite against a runtime-provisioned ephemeral stack), and `engineering.browser-matrix-check` (the first `fan_out` + `environment` combination — one parameterized matrix flow over browser/viewport targets, superseding per-browser and per-OS regression forks). Each ships a sample and a NilCore run bundle with sandbox-run evidence backed by environment provenance.
- Added the `environment` node primitive and its provenance enforcement to `flowctl`: a declared `environment` must `provide` at least one capability, and `validate-run` requires `sandbox-run` evidence to be backed by a runtime-issued `env.provisioned` event whose `provisioner` is not a producing agent (provenance is non-self-issued), with a matching `env.torn_down` when teardown is required. Added the `evidence_class_min` gate floor and an `engineering.backend-service` NilCore run bundle demonstrating honest `sandbox-run` evidence with environment provenance, alongside the existing standalone (`deterministic`) run.
- Added the `engineering.backend-service` reusable flow (stack as a contract input) with a sample and a standalone run bundle.
- Added the `engineering.frontend-build` reusable flow (deterministic build/test/accessibility gates plus an operator visual-review gate) with a sample and a standalone run bundle.
- Added the `design.website-to-spec` reusable flow with a sample and a standalone run bundle.
- Added the `program.webapp-build` program flow composing the three flows above via `flow_ref`, with a sample and a standalone run bundle whose three child sub-runs are recursively validated.
- Added the `capability-registry.schema.json` and `runtime-profile.schema.json` schemas and `docs/proposals/` (the lifecycle/evidence reframe and sub-flow composition design records).
- Added the substance layer to the node schema: optional `instructions`, `command`, `parameters`, `inputs_schema`, `outputs_schema`, and `on_failure` fields so a flow can carry what a consumer or the reference runner needs to execute it. All fields are additive and the existing catalog still validates.
- Added `flowctl run`, a reference runner that executes a flow with built-in local handlers (command subprocesses for `tool`/`command` nodes, structured records for `intake`/`plan`/`decision`/`verifier`/`finalizer`, needs-handler reporting for `agent_task`/`approval`/`handoff`), passes gates only from real produced evidence, and writes a run bundle validated against `schemas/run.schema.json`.
- Added `docs/runnable-flows.md` describing the substance layer, the consumer boundary, and the `flowctl run` execution model, with cross-links from `docs/flow-spec.md`.
- Added consumer handler binding to `flowctl run` via `--handler node_id=command`: a consuming runtime can bind an `agent_task`/`approval`/`handoff` node to a command at run time (with the same substitution, `on_failure`, and evidence capture as a node command), so a contract flow runs end-to-end without baking agent commands into the flow. Bound steps are tagged `handler: consumer` in the bundle, and handlers targeting unknown nodes are rejected. Committed a worked example under `examples/runs/consumed/feature-implementation/` and documented the model in `docs/runnable-flows.md`.
- Added `flowctl run --plan`, a dry run that prints the execution order and classifies each node as `command`, `data`, `handler`, or `needs-handler`, then lists the consumer handler surface (which nodes a consumer must bind). Passing `--handler` flags with `--plan` confirms a binding set is complete before executing. A test asserts every catalog flow has a well-defined consumption surface.
- Added `flowctl run --simulate`, a wiring check that assumes every working/agent step succeeds and verifies each required quality gate is satisfiable and every required output is produced, without running commands. A catalog-wide test runs `--simulate` over all 64 flows and asserts each reaches `status: completed`, giving the library a structural completability guarantee.
- Made `research.codebase-orientation` runnable end-to-end and committed a real produced run bundle under `examples/runs/real/codebase-orientation/` with actual command output as evidence.
- Fleshed `coding.feature-implementation` as the consumable-contract reference (per-node instructions, intake `inputs_schema`, a `test_command` parameter, a command on the checks node, and `on_failure` handling); its `implement` node stays a consumer-supplied `agent_task`.
- Added `flowctl run` regression tests covering command execution, gate evidence, bundle validity, command-failure handling, and needs-handler reporting.
- Rolled the substance layer across the remaining 62 flows: every node now carries operational `instructions`, each intake node declares an `inputs_schema` mirroring its contract inputs, tool nodes that map to a concrete portable command carry a `command`, `parameters`, and `on_failure`, and critical verifier nodes carry failure policies. The change is additive (no contract, edge, gate, observability, runtime, or metadata changes), so all existing sample, run-bundle, and adapter-smoke fixtures still validate.
- Made three more flows runnable end-to-end under `flowctl run` and committed their real run bundles under `examples/runs/real/`: `ops.adapter-certification` (runs `flowctl validate-adapter-smoke`), `proof.verified-patch-acceptance` (runs the verifier-owned test command), and `ops.capability-negotiation` (no-command fail-closed comparison). Added a "Runnable flows today" table to `docs/runnable-flows.md` and a "Runnable" section to each flow's README.

### Fixed

- `flowctl validate-event` no longer treats run-bundle artifacts (intake records and command logs under an `artifacts/` directory) as standalone event documents, so produced run bundles can live under `examples/` without breaking event validation.
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
- Upgraded three existing flows to `agentic-flows/v1.1` in place (additive, no per-flow forks): `engineering.flaky-test-stabilization` now bounds its rerun node with an `iteration` loop and declares an ephemeral runner `environment`; `engineering.performance-regression` bounds its remeasure node with a tune-until-budget `iteration` loop and an ephemeral bench-host `environment`; and `orchestration.swarm-execution` replaces its single-dispatch model with a real `fan_out` over lanes. Their existing samples, run bundles, and adapter smoke evidence remain valid.
- Expanded the catalog to sixty-eight reusable workflows: the original sixty-four (all 46 build-now candidates plus the 12 strongest contract-first backlog flows — security hotfix, repo bootstrap, monorepo slice, performance regression, backlog grooming, release-candidate audit, untrusted-output routing, access review, technology radar, incident response, self-improvement loop, connector productionization), plus the four v1.1 generative/composition flows (design.website-to-spec, engineering.backend-service, engineering.frontend-build, program.webapp-build), and recorded their compatibility states.

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
