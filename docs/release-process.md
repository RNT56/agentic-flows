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
9. Run `flowctl release-check`.
10. Confirm schema and flow versions are correct.
11. Tag the release.
12. Push the tag.
13. Add release notes from `CHANGELOG.md`.
14. Attach the release package if consumers need a bundled asset.

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

## Release readiness command

`flowctl release-check` validates the policy gates that are easy to miss during manual review:

- deprecated flows must point at a replacement flow in the release catalog
- production flows must be replaced by production flows
- stable flows cannot also be deprecated
- stable flows need a sibling README maturity rubric
- stable flows need a valid sample
- stable flows need completed standalone run evidence when they support `standalone`
- stable flows need adapter smoke evidence for every declared optional consumer
