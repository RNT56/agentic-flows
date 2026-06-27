# Adapter smoke manifests

Adapter smoke manifests are repo-local contract evidence for optional consumers.

They are validated by:

```bash
flowctl validate-adapter-smoke examples/adapters/
```

## Purpose

ThinClaw, NilCore, and CrustCore are independent projects. This repository proves portable contract coverage through smoke manifests; compiled adapter behavior is tested in each independent project repo.

The smoke manifests here prove the portable parts:

- the selected flow declares the consumer in `runtime.supported_cores`
- the manifest supports every required flow capability
- every node type in the flow has a consumer mapping
- the consumer-specific run bundle validates
- negative evidence fixtures fail when expected

## File naming

Use:

```text
examples/adapters/<consumer>-<scenario>.adapter-smoke.json
```

Store supporting run bundles under:

```text
examples/adapters/runs/*.run.json
```

## Required structure

Every adapter smoke manifest must include:

- `adapter_smoke_version`
- `consumer`
- `flow.id`
- `flow.version`
- `flow.source`
- `capability_support`
- `node_type_mappings`
- `run_bundle`

## Validation rules

`flowctl validate-adapter-smoke` checks:

- adapter smoke schema validity
- source flow existence and validity
- flow id and version match the source flow
- consumer is listed in `runtime.supported_cores`
- every source flow required capability is listed in `capability_support`
- every source flow node type has a mapping
- referenced run bundle validates
- run bundle `run.core` matches the adapter consumer
- optional event stream evidence validates
- optional negative run bundle fails with the expected validation error

## Current examples

- `thinclaw-human-review.adapter-smoke.json`
- `nilcore-multi-agent-supervisor.adapter-smoke.json`
- `crustcore-feature-implementation.adapter-smoke.json`

## External validation

The first external adapter seams are validated by focused tests in their owning repos:

- ThinClaw: `cargo test -p thinclaw-agent agentic_flows`
- NilCore: `go test ./internal/agenticflows`
- CrustCore: `cargo test -p crustcore-flow agentic_flows`
