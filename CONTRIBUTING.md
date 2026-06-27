# Contributing

Keep this repository contract-first.

## Local checks

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e . pytest
flowctl validate
pytest
```

## Flow contribution checklist

- Put reusable flows under `flows/<domain>/<name>/flow.yaml`.
- Put starter-only flows under `templates/<name>/flow.yaml`.
- Keep `id` stable after a flow is consumed by a core.
- Add or update a README next to production flows.
- Declare all supported cores in `runtime.supported_cores`.
- Add required capabilities that the runtime must provide.
- Include at least one required quality gate.
- Avoid runtime-specific fields outside `runtime.adapter_hints`.

## Compatibility

The flow schema follows semantic versioning through `spec_version`.

- Additive fields can ship in the same major version.
- Removing or renaming fields requires a new major version.
- Existing stable flows should not be rewritten for style-only changes.

