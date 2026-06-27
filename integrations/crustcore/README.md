# CrustCore integration

CrustCore can consume `agentic-flows` as a proof and verifier contract if that independent project chooses to add an adapter.

Possible first adapter:

1. Load and validate a flow.
2. Convert `quality_gates` into verifier-owned completion criteria.
3. Require evidence for patch outputs.
4. Emit flow events into an audit timeline.

See [rust/README.md](rust/README.md) for the initial Rust adapter shape.
