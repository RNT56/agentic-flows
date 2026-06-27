# Workflow authoring

## Authoring workflow

1. Start from a template under `templates/`.
2. Pick a stable `id` before the flow is consumed.
3. Declare supported cores conservatively.
4. Declare required capabilities before writing nodes.
5. Write the graph from entrypoint to finalizer.
6. Add at least one required quality gate.
7. Add observability events that a runtime can realistically emit.
8. Add a README next to any reusable production flow.
9. Run `flowctl validate <path>`.
10. Add tests or fixtures when the flow requires new schema behavior.

## Flow review checklist

- Does the flow have one clear purpose?
- Are inputs and outputs concrete enough for a runtime?
- Does every edge reference a real node?
- Is every node reachable from the entrypoint?
- Are quality gates specific and required where needed?
- Are runtime-specific details isolated under `runtime.adapter_hints`?
- Does the flow avoid naming implementation details from one core as universal concepts?
- Does the README explain when to use the flow and which core owns which responsibility?

## Stability promotion

`experimental` can move to `preview` when:

- The graph is useful and validated.
- The README explains expected runtime behavior.
- The flow has at least one realistic example.

`preview` can move to `stable` when:

- Every supported core has adapter smoke evidence.
- Required capabilities are implemented or intentionally mapped.
- Run events validate against `schemas/event.schema.json`.
- Changelog and compatibility notes are updated.

## Deprecation

Do not delete consumed flows without a replacement path.

Deprecated flows should include:

- Why they are deprecated.
- What replaces them.
- Which release will remove them.
- Migration notes for consuming cores.

