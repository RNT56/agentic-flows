# agentic-flows

Reusable workflow definitions for the RNT56 agentic stack.

`agentic-flows` is the contract layer between high-level agentic process design and the runtimes that execute or verify those processes:

- **ThinClaw** is the home: durable identity, memory, routines, channels, and operator-facing control.
- **NilCore** is the worker: sandboxed task execution, supervisor loops, browser checks, and scale-out delegation.
- **CrustCore** is the proof: verifier-owned completion, audit boundaries, approvals, and trusted patch evidence.

This repository does not replace those cores. It gives them a shared, versioned workflow format, examples, validation, and integration contracts.

## What is in this repo

```text
flows/          Versioned reusable workflow definitions.
templates/      Copyable starter flows for new projects.
schemas/        JSON Schema contracts for flows, nodes, and events.
tools/flowctl/  CLI for validation, listing, and graph export.
integrations/   ThinClaw, NilCore, CrustCore, and shared adapter contracts.
examples/       Minimal consumption examples and runbooks.
docs/           Architecture, spec, roadmap, and integration guidance.
tests/          CLI and schema regression tests.
```

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e . pytest

flowctl validate
flowctl validate-event examples/standalone/event.sample.json
flowctl list
flowctl graph flows/coding/feature-implementation/flow.yaml --format dot
pytest
```

The default validation command checks every `flow.yaml` under `flows/` and `templates/`.

## Current stack

- Flow definitions: YAML with a JSON Schema contract.
- Validation and export: Python CLI (`flowctl`).
- CI: GitHub Actions validates schemas, flows, graph export, and tests.
- Runtime adapters: contract-first documentation until ThinClaw, NilCore, and CrustCore expose stable importable APIs for this layer.

## First-class flows

- `coding/feature-implementation`
- `coding/refactor-and-verify`
- `coding/security-audit`
- `research/deep-research-report`
- `collaboration/multi-agent-supervisor`
- `general/human-in-the-loop-review`

## Definition of ready

A workflow is ready to use when:

1. `flowctl validate` passes.
2. The flow declares its supported cores and required capabilities.
3. Every edge references an existing node.
4. Every node is reachable from the entrypoint.
5. At least one required quality gate is present.
6. The consuming runtime records events compatible with `schemas/event.schema.json`.

See [docs/project-plan.md](docs/project-plan.md) for the upgraded plan and [docs/core-integration.md](docs/core-integration.md) for runtime expectations.

## Documentation

Start with [docs/README.md](docs/README.md). The docs folder contains the full roadmap, goals, task backlog, workflow authoring guidance, testing strategy, release process, changelog management, governance, and adapter implementation plan.

## Changelog

Release and compatibility notes live in [CHANGELOG.md](CHANGELOG.md). Keep `Unreleased` current for schema, flow, command, adapter-contract, and process changes.
