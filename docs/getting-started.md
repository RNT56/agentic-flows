# Getting started

## Install tooling

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

## Validate flows

```bash
flowctl validate
```

Validate a single flow:

```bash
flowctl validate flows/coding/feature-implementation/flow.yaml
```

## List flows

```bash
flowctl list
```

## Export a graph

```bash
flowctl graph flows/coding/feature-implementation/flow.yaml --format json
flowctl graph flows/coding/feature-implementation/flow.yaml --format dot
```

## Create a new flow

1. Copy a folder from `templates/`.
2. Change `id`, `title`, `summary`, `runtime`, and quality gates.
3. Add or remove nodes and edges.
4. Run `flowctl validate <new-flow-path>`.
5. Add a README next to reusable flows.

