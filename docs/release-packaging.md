# Release packaging

Release packages are deterministic zip files containing the contract assets a consumer needs to pin.

Build one with:

```bash
flowctl package-release --output /tmp/agentic-flows-release.zip
```

## Included assets

The default package includes:

- `README.md`
- `CHANGELOG.md`
- `LICENSE`
- `schemas/`
- `flows/`
- `templates/`
- `examples/samples/`
- selected release docs

It does not include generated caches, local virtual environments, or untracked files.

## Publication decision

Keep `flowctl` repo-local for now.

Reasons:

- the CLI reads schemas and examples from the repo root
- the public contract is still changing before stable adapter adoption
- consuming projects can pin this repo directly by commit or tag

Reconsider publishing `flowctl` separately after at least one independent consumer has a real adapter and stable flow evidence.
