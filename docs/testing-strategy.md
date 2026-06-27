# Testing strategy

## Local test layers

Run before pushing:

```bash
flowctl validate
flowctl validate-event examples/standalone/event.sample.json
flowctl validate-run examples/runs/
flowctl report
flowctl graph flows/coding/feature-implementation/flow.yaml --format json --output /tmp/feature-flow.graph.json
pytest
git diff --check
```

## Unit tests

Unit tests should cover:

- valid repository flows
- invalid schema fixtures
- invalid semantic fixtures
- event schema validation
- CLI command behavior

## CI tests

The GitHub Actions workflow should run:

- package installation
- flow validation
- event validation
- run bundle validation
- flow catalog report
- graph export
- test suite

## Optional adapter smoke tests

Adapter smoke tests should prove that an independent optional consumer can:

- load a valid flow
- reject unsupported capabilities
- map nodes to runtime concepts
- emit valid events
- attach evidence to required gates

## Release gates

No release should be tagged unless:

- CI passes on `main`
- `CHANGELOG.md` has a dated entry
- docs match the current command surface
- stable flows have adapter evidence for each declared optional consumer
