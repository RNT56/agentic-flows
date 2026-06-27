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
6. Confirm schema and flow versions are correct.
7. Tag the release.
8. Push the tag.
9. Add release notes from `CHANGELOG.md`.

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
- each supported core has adapter evidence for at least one flow

