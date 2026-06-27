# Versioning

## Schema versions

The schema version is carried by `spec_version`.

Current value:

```yaml
spec_version: agentic-flows/v1
```

Rules:

- Additive optional fields can stay in the same major version.
- Removing fields requires a new major version.
- Renaming fields requires a new major version.
- Tightening validation on existing required fields should be treated as breaking unless all existing flows already pass.

## Flow versions

Each flow has its own semantic version.

Increment:

- Patch for documentation-only or non-behavioral metadata changes.
- Minor for additive nodes, gates, outputs, or capabilities.
- Major when inputs, outputs, core support, or required gates change incompatibly.

## Deprecation metadata

Use `deprecated_by` when a flow has a replacement. Add `migration.summary` and `migration.steps` in the same change so optional consumers can move without guessing.

Deprecation rules:

- Do not delete a published flow until at least one tagged release has included the replacement and migration guidance.
- Keep deprecated flows valid under `flowctl validate`.
- Keep samples and run evidence available until the replacement has equivalent evidence.

## Stability levels

- `experimental`: Safe to iterate; optional consumers should pin exact commits.
- `preview`: Shape is useful but optional consumer adapters may still change.
- `stable`: Compatible with declared cores and protected by integration evidence.

No flow should become `stable` before real adapter checks exist for every optional consumer listed in `runtime.supported_cores`.
