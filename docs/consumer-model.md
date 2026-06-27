# Consumer model

ThinClaw, NilCore, and CrustCore are independent projects.

`agentic-flows` must not assume they already share runtime concepts, APIs, state, or orchestration. This repository defines reusable workflow contracts that those projects may choose to consume later.

## What `supported_cores` means

The current schema field is named `runtime.supported_cores`.

In this project, it means:

- the flow is intended to be compatible with that optional consumer
- the flow only requires capabilities that consumer could reasonably implement
- future adapter work should start from that declaration

It does not mean:

- the consumer already has an adapter
- the consumer already executes this flow
- the projects are part of one unified runtime
- the flow is stable for that consumer

## Consumer states

Use these states when discussing a project:

- `target`: the flow is designed with that project in mind, but no adapter evidence exists.
- `adapter-smoke`: the project can load and validate the flow.
- `run-smoke`: the project can produce a valid run bundle for the flow.
- `stable`: the project has repeatable adapter and run evidence for the flow.

## Documentation rule

Use optional language until evidence exists.

Prefer:

```text
ThinClaw can use this as a durable routine if it implements an adapter.
```

Avoid:

```text
ThinClaw owns this workflow.
```

## Promotion rule

A flow can be listed as `preview` when its contract is coherent.

A flow can only be listed as `stable` for a consumer after that independent project produces adapter or run evidence.

