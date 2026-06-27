# NilCore integration

NilCore can consume `agentic-flows` as a worker execution and supervisor plan if that independent project chooses to add an adapter.

Possible first adapter:

1. Load and validate a flow.
2. Dispatch `agent_task` nodes to sandboxed workers.
3. Run `tool` nodes through controlled command/browser/tool execution.
4. Route `verifier` nodes through supervisor checks.
5. Return lane and node evidence to the caller.

See [go/README.md](go/README.md) for the initial Go adapter shape.
