# Deployment

This repo deploys in two senses:

1. Repository deployment: validated flow definitions are pushed to GitHub.
2. Consumer deployment: an independent project pins a commit or tag and loads selected flows.

## Repository deployment

Required gates before pushing:

```bash
flowctl validate
flowctl normalize
flowctl validate-adapter-smoke examples/adapters/
flowctl validate-event examples/standalone/event.sample.json
flowctl validate-stream examples/streams/
flowctl validate-run examples/runs/
flowctl replay examples/runs/feature-implementation.run.json --json
flowctl validate-samples
flowctl report
flowctl changelog-check
flowctl check-links
flowctl package-release --output /tmp/agentic-flows-release.zip
flowctl release-check
pytest
```

CI repeats those gates on every push to `main`.

## Runtime deployment

Recommended process:

1. Pin `agentic-flows` by commit SHA or tag.
2. Run `flowctl validate` in the consuming repo.
3. Load the selected `flow.yaml`.
4. Confirm runtime capabilities.
5. Execute a dry run or adapter smoke test.
6. Record event output compatible with `schemas/event.schema.json`.
7. Package completed evidence as a run bundle compatible with `schemas/run.schema.json`.

## Release tags

Use tags once a consuming runtime depends on the repo:

```bash
git tag v0.1.0
git push origin v0.1.0
```

Do not tag a flow as stable for a consumer until that independent project has adapter evidence.
