# Goals

## Mission

`agentic-flows` is the reusable workflow definition layer for RNT56 agentic projects.

The repo should make agentic work portable across:

- ThinClaw as the durable home and operator control surface.
- NilCore as the worker and supervisor execution layer.
- CrustCore as the proof and verifier boundary.
- Standalone development for validation, examples, and documentation.

## Primary goals

1. Define reusable workflows in a stable, human-readable format.
2. Validate flow structure, graph semantics, event evidence, and compatibility.
3. Provide clear adapter contracts for ThinClaw, NilCore, and CrustCore.
4. Keep workflow definitions runtime-neutral unless runtime-specific behavior is explicitly declared.
5. Provide starter templates for fast project-specific flow creation.
6. Maintain a release process that lets consuming projects pin compatible versions.
7. Keep documentation close to the code and protected by CI.

## Non-goals

- This repo is not a full workflow runtime.
- This repo does not own sandboxing, permissions, memory, or approval UX.
- This repo does not replace ThinClaw, NilCore, or CrustCore.
- This repo should not become a dumping ground for project-specific one-off prompts.
- This repo should not mark flows stable without adapter evidence from supported cores.

## Success metrics

- Every flow under `flows/` validates in CI.
- Every reusable flow has a README, supported core list, and required quality gates.
- Every stable flow has adapter smoke evidence for each supported core.
- Every release has a changelog entry and compatibility notes.
- Every schema change is either backward-compatible or explicitly versioned.
- Consuming repos can pin a tag and load selected flows without custom per-flow parsing.

## Operating principles

- Contract first: define the schema and validation before broadening flow content.
- Evidence over assertion: every completion path needs required gates and event evidence.
- Runtime-neutral by default: core-specific fields belong under `runtime.adapter_hints`.
- Small stable surface: keep the schema conservative until real adapters prove the need.
- Explicit compatibility: never imply support for a core that has not loaded the flow.

