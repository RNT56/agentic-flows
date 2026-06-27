# Changelog management

This repo uses a human-maintained `CHANGELOG.md` at the repository root.

## Format

Keep the structure based on Keep a Changelog:

- `Unreleased`
- dated release sections
- grouped change types

Recommended groups:

- `Added`
- `Changed`
- `Deprecated`
- `Removed`
- `Fixed`
- `Security`

## What needs a changelog entry

Add an entry when a change affects:

- public flow definitions
- schemas
- `flowctl` commands or output
- adapter contracts
- release process
- CI gates
- docs that change how users operate the repo

No changelog entry is required for typo-only edits unless they affect commands, examples, or process instructions.

## Release workflow

Before tagging:

1. Move `Unreleased` entries into a dated section.
2. Add the release version and date.
3. Confirm version bumps match the change type.
4. Link migration notes for breaking changes.
5. Leave a fresh empty `Unreleased` section.

## Changelog quality bar

Entries should be useful to a consuming runtime maintainer.

Prefer:

```text
- Added `flowctl validate-event` for event artifact validation.
```

Avoid:

```text
- Updated files.
```

