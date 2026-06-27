# ThinClaw integration

ThinClaw can consume `agentic-flows` as durable operator-facing routines if that independent project chooses to add an adapter.

Possible first adapter:

1. Load and validate a flow.
2. Create a routine from the flow graph.
3. Persist intake, plan, approval, and finalizer state.
4. Record operator decisions as durable memory.
5. Link run evidence back to the source flow version.

See [rust/README.md](rust/README.md) for the initial Rust adapter shape.
