# Standalone example

Use the standalone path to inspect and validate flows without a core runtime.

```bash
flowctl validate flows/coding/feature-implementation/flow.yaml
flowctl graph flows/coding/feature-implementation/flow.yaml --format json
```

This does not execute nodes. It proves that a flow definition is structurally valid and graph-exportable.

