# Operating workflows

This document describes how work should move through the project.

## Documentation change workflow

1. Identify the affected docs.
2. Update links from `docs/README.md` when adding a new document.
3. Keep README short and point to durable docs.
4. Update `CHANGELOG.md` when the doc changes project operation.
5. Run `git diff --check`.

Acceptance gate:

- A new contributor can find the changed process from the docs index.

## Flow change workflow

1. Update or add `flow.yaml`.
2. Update the flow README.
3. Run `flowctl validate <flow-path>`.
4. Add fixtures if validation rules changed.
5. Update changelog if public flow behavior changed.

Acceptance gate:

- The flow validates and its supported cores, capabilities, gates, and outputs are clear.

## Tooling change workflow

1. Update `tools/flowctl`.
2. Add or update tests.
3. Update `docs/getting-started.md` and `docs/testing-strategy.md` when command behavior changes.
4. Update CI if the command becomes a release gate.
5. Update changelog.

Acceptance gate:

- The command has a documented use case, test coverage, and CI coverage when it protects repo correctness.

## Adapter contract workflow

1. Update shared contracts first.
2. Update core-specific integration docs.
3. Add adapter smoke-test expectations.
4. Update compatibility and roadmap docs.
5. Update changelog.

Acceptance gate:

- ThinClaw, NilCore, and CrustCore maintainers can see whether the change affects their adapter.

## Release workflow

1. Finish all target tasks.
2. Run local checks.
3. Confirm CI passes on `main`.
4. Move changelog entries from `Unreleased` to the release version.
5. Tag and push the release.
6. Publish release notes.

Acceptance gate:

- A consuming repo can pin the tag and understand compatibility impact from the changelog.

