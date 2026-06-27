# Workflow authoring

## Authoring workflow

1. Start from a template under `templates/`.
2. Pick a stable `id` before the flow is consumed.
3. Declare optional consumers conservatively in `runtime.supported_cores`.
4. Declare required capabilities before writing nodes.
5. Write the graph from entrypoint to finalizer.
6. Add at least one required quality gate.
7. Add `evidence_refs` to every required gate, pointing only to declared artifacts or events.
8. Add observability events that a runtime can realistically emit.
9. Add a README with a maturity rubric next to any reusable production flow.
10. Add a sample under `examples/samples/` for reusable production flows.
11. Run `flowctl normalize --write <path>`.
12. Run `flowctl validate <path>`.
13. Run `flowctl validate-samples`.
14. Add tests or fixtures when the flow requires new schema behavior.

## Flow review checklist

- Does the flow have one clear purpose?
- Are inputs and outputs concrete enough for a runtime?
- Does every edge reference a real node?
- Is every node reachable from the entrypoint?
- Are quality gates specific and required where needed?
- Do required gates name machine-checkable `evidence_refs`?
- Are runtime-specific details isolated under `runtime.adapter_hints`?
- Does the flow avoid naming implementation details from one core as universal concepts?
- Does the README explain when to use the flow and how optional consumers could map it?
- Does the README include a maturity rubric with evidence and promotion gaps?
- Does the flow have a sample with required inputs and expected outputs?

## Stability promotion

`experimental` can move to `preview` when:

- The graph is useful and validated.
- The README explains expected runtime behavior.
- The flow has at least one realistic example.

`preview` can move to `stable` when:

- Every declared optional consumer has adapter smoke evidence.
- Required capabilities are implemented or intentionally mapped.
- Run events validate against `schemas/event.schema.json`.
- Changelog and compatibility notes are updated.

## Deprecation

Do not delete consumed flows without a replacement path.

Deprecated flows should include:

- Why they are deprecated.
- What replaces them.
- Which release will remove them.
- `deprecated_by` plus `migration.summary` and `migration.steps`.
