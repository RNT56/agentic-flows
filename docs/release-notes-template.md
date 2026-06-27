# Release notes template

Use this template when publishing a GitHub release.

```markdown
## agentic-flows vX.Y.Z

### Summary

One or two sentences describing the release impact.

### Added

- 

### Changed

- 

### Fixed

- 

### Compatibility

- Schema version:
- Flow compatibility:
- Optional consumer evidence:

### Validation

- `flowctl validate`
- `flowctl validate-event examples/`
- `flowctl validate-run examples/runs/`
- `flowctl report`
- `pytest`
- GitHub Actions run:

### Migration notes

- 
```

Before publishing, copy the relevant section from `CHANGELOG.md` and add validation links.

