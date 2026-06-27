# Best practices

## Flow design

- Keep each flow focused on one reusable job.
- Prefer explicit gates over vague final review.
- Put human decisions in `approval` nodes, not hidden prose.
- Keep command gates declarative; the runtime owns the execution environment.
- Use artifacts to name evidence that should survive the run.
- Keep flow ids stable after adoption.

## Runtime compatibility

- Only list a core in `runtime.supported_cores` when it can load or is intended to load the flow.
- Put core-specific hints under `runtime.adapter_hints`.
- Do not require a capability that only one core can provide unless the flow is intentionally limited to that core.
- Treat unsupported capabilities as hard failures in adapters.

## Evidence and auditability

- Every required gate needs evidence.
- Events should be timestamped and tied to a `run_id`.
- Completion should fail when required gate evidence is missing.
- Prefer durable artifact references over inline blobs for large evidence.

## Security and safety

- Do not store secrets in flows, examples, fixtures, or event samples.
- Do not make destructive commands the default gate command.
- Treat approval nodes as policy boundaries.
- Keep public examples synthetic unless source material is already safe to publish.

## Documentation

- Put durable process docs under `docs/`.
- Put flow-specific usage notes next to the flow.
- Keep README focused on orientation and quick start.
- Update `CHANGELOG.md` when user-facing behavior, schema, flow catalog, or tooling changes.

