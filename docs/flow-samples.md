# Flow samples

Flow samples are contract examples for reusable production flows.

They are validated by:

```bash
flowctl validate-samples
```

## Purpose

A sample shows:

- realistic input values for a flow
- expected output shapes
- the source flow id and version the sample belongs to

Samples do not execute the flow. They make the flow contract understandable and testable.

## Location

Use:

```text
examples/samples/<domain>/<flow-name>.sample.json
```

Every production flow under `flows/` must have one sample when `flowctl validate-samples` is run with default paths.

## Required structure

Every sample must include:

- `sample_version`
- `flow.id`
- `flow.version`
- `flow.source`
- `inputs`
- `expected_outputs`

## Validation rules

`flowctl validate-samples` checks:

- source flow exists
- source flow validates
- sample flow id and version match the source flow
- all required inputs are present
- all required expected outputs are present
- unknown input or output ids are rejected
- sample values match declared contract types
- every production flow has a sample

## Content rules

- Keep samples synthetic or already-public.
- Do not include secrets, tokens, private contacts, or private repo data.
- Prefer concrete examples over placeholders.
- Keep expected outputs short enough to scan.
- Use `notes` for sample intent and constraints.

