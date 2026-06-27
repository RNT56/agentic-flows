# NilCore example

NilCore should start with `flows/collaboration/multi-agent-supervisor/flow.yaml` and `flows/coding/feature-implementation/flow.yaml`.

Adapter smoke test target:

1. Load the flow.
2. Confirm `nilcore` is in `runtime.supported_cores`.
3. Dispatch `agent_task` nodes to worker jobs.
4. Run `tool` nodes in the configured sandbox.
5. Return worker evidence for required gates.

