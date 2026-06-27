# ThinClaw example

ThinClaw should start with `flows/general/human-in-the-loop-review/flow.yaml` and `flows/coding/feature-implementation/flow.yaml`.

Adapter smoke test target:

1. Load the flow.
2. Confirm `thinclaw` is in `runtime.supported_cores`.
3. Persist intake, approval, and finalizer state as routine data.
4. Store operator decisions with enough context for future memory.
5. Link closeout evidence back to the source flow version.

