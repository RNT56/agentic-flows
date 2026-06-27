# Release process

## Release types

- Patch release: docs, examples, tests, or non-breaking tool changes.
- Minor release: additive schema fields, new flows, new templates, or new commands.
- Major release: breaking schema, flow contract, or adapter contract changes.

## Release checklist

1. Confirm `main` is clean.
2. Run local checks from [testing strategy](testing-strategy.md).
3. Confirm GitHub Actions pass on `main`.
4. Move entries from `Unreleased` to a dated changelog section.
5. Confirm docs match command output.
6. Run `flowctl changelog-check --release <version>`.
7. Run `flowctl check-links`.
8. Build a release package with `flowctl package-release --output /tmp/agentic-flows-release.zip`.
9. Confirm schema and flow versions are correct.
10. Tag the release.
11. Push the tag.
12. Add release notes from `CHANGELOG.md`.
13. Attach the release package if consumers need a bundled asset.

## Tag format

Use semantic version tags:

```bash
git tag v0.1.0
git push origin v0.1.0
```

## Release notes

Release notes should include:

- added flows
- schema changes
- command changes
- adapter compatibility notes
- breaking changes
- migration notes

## Pre-release policy

Use `v0.x.y` releases while adapters are still maturing.

Do not release `v1.0.0` until:

- at least one stable flow exists
- event validation is implemented
- run validation is implemented
- each declared optional consumer has adapter evidence for at least one flow
