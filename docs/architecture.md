# Architecture

`agentic-flows` has three layers.

## Definition layer

The definition layer is the source of truth:

- `flows/`
- `templates/`
- `schemas/`

Each flow declares inputs, outputs, nodes, edges, runtime capabilities, quality gates, and observability events.

## Validation layer

The validation layer prevents drift:

- `tools/flowctl`
- `tests/`
- `.github/workflows/validate.yml`

Validation checks both JSON Schema rules and graph semantics that JSON Schema alone cannot express, such as missing edge targets and unreachable nodes.

## Integration layer

The integration layer tells runtimes how to consume flows:

- `integrations/common/contracts/`
- `integrations/thinclaw/`
- `integrations/nilcore/`
- `integrations/crustcore/`
- `examples/`

The independent consuming project is responsible for execution, state, permissions, sandboxing, and proof. This repository is responsible for stable workflow definitions and compatibility rules.

## Optional consumer responsibilities

These are optional mappings for independent projects. They are not claims that the projects share a runtime.

| Consumer | Possible responsibility | Optional integration path |
| --- | --- | --- |
| ThinClaw | Routines, memory, channels, operator control | Load selected flow references as durable routines and preserve approval metadata. |
| NilCore | Worker execution, supervision, sandboxed checks | Dispatch `agent_task` nodes and run `tool` plans through its sandbox boundary. |
| CrustCore | Proof, audit, verifier-owned completion | Validate required gates and reject incomplete completion evidence. |
| Standalone | Local development and examples | Validate and inspect flows without a full runtime. |

## Data flow

```mermaid
flowchart LR
  A["flow.yaml"] --> B["flowctl validate"]
  B --> C["runtime adapter"]
  C --> D["node execution"]
  D --> E["quality gates"]
  E --> F["event stream"]
  F --> G["operator closeout"]
```
