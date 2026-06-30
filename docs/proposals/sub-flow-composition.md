# Sub-flow composition

> Status: **Adopted in `agentic-flows/v1.1`** (additive to `agentic-flows/v1`). The `flow_ref` node type and its static (`flowctl check-composition`) and runtime (recursive `sub_runs` in `flowctl validate-run`) checks now ship in the live `schemas/` and `flowctl` — see [CHANGELOG.md](../../CHANGELOG.md) and [flow-spec.md](../flow-spec.md). The empirical finding below describes the pre-implementation state that motivated the design; the evidence gap it warns about is now closed. This document is retained as the design rationale.

## Summary

This proposal specs `flow_ref`: a new node type that lets one flow run another flow as a single step.
It turns the flow catalog from a flat list of independent flows into a composable library, and unblocks
composed "build a whole product" programs. `docs/buildable-now.md` lists sub-flow composition under
**needs-spec-extension** as the primitive that blocks `program.product-release-autopilot`.

A `flow_ref` node names a child flow (`ref.flow_id` + `version_constraint`), binds parent values into the
child's inputs (`with`), and lifts named child outputs back into local artifacts (`expose`). The child runs
as its own run bundle — its own flow id, version, run id, gates, and evidence — and the parent run links to
it. There is no inlining and no flattening.

The honest part of this proposal is the warning attached to it. The **authoring** layer is a clean additive
change: one new node type, one schema diff, and the existing dataflow validator works unchanged. The
**evidence** layer — the whole point of a "pin versions and prove it" system — does not work yet. A
fabricated parent run that claims its sub-flows passed validated with exit 0 *before this proposal landed*.
Shipping "an additive flow v1.1" was necessary but nowhere near sufficient. Six layers had to land for
composition evidence to mean anything, and getting it wrong yields silent dishonesty — all six now ship.

This is **Phase 3** of the lifecycle-evidence reframe (`docs/proposals/lifecycle-evidence-reframe.md`):
loops and fan-out are sibling extensions; composition is the one that crosses run-bundle boundaries and so
puts the most weight on the evidence model.

## Relation to project goals

`docs/goals.md` makes composition both wanted and constrained:

- **Mission** — "the reusable workflow definition layer." A catalog you cannot compose is a list, not a
  library. `flow_ref` is the primitive that makes reuse compound.
- **Primary goal 6** — "let consuming projects pin compatible versions." Composition pins *transitively*:
  a program pins a `version_constraint` per child, and the resolved concrete child version is recorded in run
  evidence for deterministic replay.
- **Operating principle: evidence over assertion** — "every completion path needs required gates and event
  evidence." A parent that asserts "sub-flows passed" without linking to child run bundles that actually
  passed is exactly the assertion this principle forbids.
- **Non-goal: not a runtime** — this repo does not *execute* child flows. It defines the composition contract
  and validates the *consistency* of the evidence a runtime produces. Authenticity (did the child actually
  run?) stays the runtime's burden. See [Inherent limit](#inherent-limit).

`docs/buildable-now.md` frames the bar: a flow is buildable end-to-end only when the full artifact set passes
every `flowctl` validator with **honest** evidence, and the discriminator is whether a completed run bundle is
an honest contract demonstration or a misrepresentation. Composition raises that bar across files: an honest
parent run is only honest if its children are too.

## Inline versus reference: why reference

There are two ways to make one flow run another.

- **Inline / flatten** — the child's nodes, gates, and edges are spliced into the parent graph at author or
  load time. The composed thing is a single flat flow with a single run bundle.
- **Reference** — the parent holds a typed pointer to the child. The child runs as its own run bundle with its
  own id, version, gates, and evidence. The parent run links to the child run.

This proposal **rejects inline** and **adopts reference**.

Inlining destroys the two things this repo exists to protect:

| Property | Inline | Reference |
| --- | --- | --- |
| Independent versioning | Lost — child changes force a parent rev; `version_constraint` is meaningless | Preserved — parent pins a range, child versions independently |
| Independent evidence | Lost — one flat run bundle, child gates indistinguishable from parent gates | Preserved — child has its own gates, its own passed `gate.completed`, its own run status |
| Catalog reuse | Lost — the child is copied, not referenced; drift is invisible | Preserved — one source of truth per child flow |
| Honest failure attribution | Lost — "which stage failed?" is ambiguous | Preserved — a failed child is a failed child run bundle |

For a system whose entire value proposition is "pin versions and show evidence over assertion," inline is the
dishonest model: it launders the child's independent evidence into the parent's. Reference is the single
honest model. The cost — a recursive validator and a representable link — is exactly the cost of honesty, and
the rest of this document is about paying it.

## The primitive

A `flow_ref` node, additive under `spec_version: agentic-flows/v1.1`:

```yaml
- id: backend
  type: flow_ref
  title: Build backend
  description: Run the backend-service sub-flow against an ephemeral datastore.
  ref:
    flow_id: engineering.backend-service
    version_constraint: ">=0.1.0 <0.2.0"
  with:                                      # parent -> child input/param bindings
    target_spec: "{{artifact.design-spec}}"
    stack: "{{input.stack}}"
  expose:                                    # child output -> local artifact name
    service_patch: backend-patch
  requires: [design-spec]
  produces: [backend-patch]                  # == set(expose.values())
```

Field semantics:

- `ref.flow_id` — the child flow's stable id. Resolved against the catalog, not a path.
- `ref.version_constraint` — a semver range. The runtime resolves it to one concrete child version and records
  that resolved version in run evidence.
- `with` — maps child input/parameter ids to parent-scoped template expressions
  (`{{input.*}}`, `{{artifact.*}}`, `{{param.*}}`). Keys are child input ids.
- `expose` — maps child **output** ids to **local artifact** names. `expose` values are the artifacts this node
  produces locally.
- `requires` / `produces` — ordinary dataflow fields. The critical invariant is
  `produces == set(expose.values())`, so the **existing** dataflow validator
  (`validate_requirements_and_outputs`, `cli.py` ~1054–1100) treats a `flow_ref` node exactly like any other
  producing node. No change to reachability, requires-from-upstream, or required-output-produced checks. The
  composition is expressible *as* dataflow; only the cross-flow resolution and the run-time linkage are new.

A `flow_ref` node is a normal graph node: it has incoming and outgoing edges, participates in reachability,
and can sit anywhere a producing node can. The webapp program in the [appendix](#appendix-worked-parent-program)
fans `design` out to `backend` and `frontend`, then joins at `integrate`.

## The empirical finding: the naive evidence model is already broken

Before specifying the layers, state the motivating result plainly, because it is the reason this proposal is
not a one-line schema change.

**A fabricated parent run bundle passes `flowctl validate-run` today (exit 0)** with all of the following:

- `run.status = completed`,
- the parent's `subflows-passed` gate marked `passed` with a `gate.completed` event,
- a `subflow.completed` event whose payload literally reads `"totally happened, trust me"`,
- and **no reference to any child run bundle at all.**

There is nothing to fix in the parent flow to make this fail. The failure is structural, for two reasons.

**(1) `validate-run` never recursively validates a child.** `validate_run_document` (`cli.py` ~392–475) and
`validate_run_events` (`cli.py` ~807–890) have no code path that loads a child run bundle. They validate the
run against its *own* source flow and stop. The only recursive run-bundle validation anywhere in the codebase
is `validate_adapter_smoke_document` (`cli.py` ~630–645), which loads and recursively calls
`validate_run_document` on a run bundle named by an adapter doc's explicit `run_bundle` field. That is a
precedent for the *shape* of the fix — load a referenced bundle, recurse, prefix the errors — but it is never
reached from run validation. From `validate-run`, a child bundle is invisible.

**(2) The link is unrepresentable.** Even if you wanted to point at a child run, there is nowhere to write the
pointer. `run.schema.json` and `event.schema.json` are both `additionalProperties: false`, so a `sub_runs`
array on the run, or a `sub_run` link on an event, is rejected by the schema before any semantic check runs.
And `collect_event_evidence_refs` (`cli.py` ~893–908) reads only evidence `id` and `kind` — never `uri` — so
even an evidence entry pointing at a child bundle file would not be followed.

Conclusion: the authoring layer is 1 of 6 layers and the easy one. The evidence layer — the point of the
system — does not work yet, and a parent that *looks* validated while linking to nothing is worse than no
feature, because it manufactures false confidence.

## The six layers

Each layer below is independently necessary. Layers are ordered by dependency, not by where the work feels
exciting. Layer 4 (catalog + semver) is the load-bearing foundation every other check sits on.

### Layer 1 — Flow schema

Reference: `docs/proposals/schemas/flow.schema.v1_1.json`. Live schema: `schemas/flow.schema.json`.

Add `flow_ref` to the node `type` enum and constrain the new fields with an `if/then` (`allOf`) so that
`ref` + `expose` are **required** when `type == flow_ref`, and `ref`/`with`/`expose` are **forbidden** on every
other node type.

```jsonc
// $defs.node.properties.type — add "flow_ref"
"type": { "enum": ["intake","plan","agent_task","tool","verifier",
                   "approval","decision","handoff","finalizer","flow_ref"] }

// $defs.node.properties — new optional fields
"ref": {
  "type": "object", "additionalProperties": false,
  "required": ["flow_id", "version_constraint"],
  "properties": {
    "flow_id": { "$ref": "#/$defs/flow_id" },
    "version_constraint": { "type": "string", "minLength": 1 }
  }
},
"with":    { "type": "object", "additionalProperties": { "type": "string" } },
"expose":  {
  "type": "object", "minProperties": 1,
  "additionalProperties": { "type": "string", "pattern": "^[a-z0-9][a-z0-9._-]*$" }
}

// $defs.node.allOf — gate the fields on type
"allOf": [
  { "if":   { "properties": { "type": { "const": "flow_ref" } }, "required": ["type"] },
    "then": { "required": ["ref", "expose"] } },
  { "if":   { "not": { "properties": { "type": { "const": "flow_ref" } } } },
    "then": { "properties": { "ref": false, "with": false, "expose": false } } }
]
```

Notes:

- `spec_version` becomes `enum: ["agentic-flows/v1", "agentic-flows/v1.1"]` so existing v1 flows keep
  validating unchanged. A `flow_ref` node is only legal under v1.1.
- `expose` **values** match the artifact-name pattern `^[a-z0-9][a-z0-9._-]*$`, identical to
  `contracts.artifacts` items, so an exposed artifact can be declared in `contracts.artifacts` and referenced
  by gates exactly like any other artifact.
- This layer is purely additive. Every existing flow validates byte-for-byte. The cited proposal schema also
  carries sibling fields (`iteration`, `fan_out`, `parameters`) from the loop/fan-out proposals; they are
  out of scope here and independent of `flow_ref`.

### Layer 2 — Run schema

Reference: `docs/proposals/schemas/run.schema.v1_1.json`. Live schema: `schemas/run.schema.json`.

Add a `sub_runs` array to the run bundle. This is **mandatory**: `run.schema.json` is
`additionalProperties: false`, so without this change the link is rejected by the schema and no semantic check
can ever see it.

```jsonc
// run.schema.json — additive top-level property
"sub_runs": {
  "type": "array",
  "items": {
    "type": "object", "additionalProperties": false,
    "required": ["node_id", "flow", "run", "uri"],
    "properties": {
      "node_id": { "type": "string", "pattern": "^[a-z][a-z0-9-]*$" },
      "flow": {
        "type": "object", "additionalProperties": false,
        "required": ["id", "version"],
        "properties": {
          "id":      { "type": "string", "pattern": "^[a-z0-9][a-z0-9._/\\-]*[a-z0-9]$" },
          "version": { "type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$" }
        }
      },
      "run": {
        "type": "object", "additionalProperties": false,
        "required": ["id", "status"],
        "properties": {
          "id":     { "type": "string", "minLength": 8 },
          "status": { "enum": ["completed", "failed", "cancelled", "running"] }
        }
      },
      "uri":    { "type": "string" },
      "sha256": { "type": "string", "pattern": "^[a-f0-9]{64}$" }
    }
  }
}
```

- `node_id` is the parent `flow_ref` node this sub-run satisfies.
- `flow.version` is the **resolved concrete** child version (not the constraint), for deterministic replay.
- `run.id` + `uri` locate the child run bundle so the validator can load and recurse into it. `uri` is
  resolved the same way `resolve_adapter_artifact_source` resolves an adapter's `run_bundle` (`cli.py`
  ~937–945): absolute, repo-relative, then relative to the parent bundle.
- `sha256` is optional today and **format-checked, not computed** — see [Inherent limit](#inherent-limit).
- `run_version` becomes `enum: ["agentic-flows.run/v1", "agentic-flows.run/v1.1"]`.

### Layer 3 — Event model

Reference: `docs/proposals/schemas/event.schema.v1_1.json`. Live schema: `schemas/event.schema.json`.

Add an optional `sub_run` link to events, and define the two composition event payloads.

```jsonc
// event.schema.json — additive top-level property
"sub_run": {
  "type": "object", "additionalProperties": false,
  "properties": {
    "flow_id": { "type": "string", "pattern": "^[a-z0-9][a-z0-9._/\\-]*[a-z0-9]$" },
    "run_id":  { "type": "string", "minLength": 8 },
    "source":  { "type": "string" }
  }
}
```

Event payloads (the `payload` object stays `additionalProperties: true`; these are the conventional shapes the
validator reads):

```jsonc
// subflow.started
{ "node_id": "backend",
  "child_flow_id": "engineering.backend-service",
  "resolved_version": "0.1.3",
  "sub_run_id": "run-backend-7f3a2c19" }

// subflow.completed
{ "node_id": "backend",
  "child_flow_id": "engineering.backend-service",
  "resolved_version": "0.1.3",
  "sub_run_id": "run-backend-7f3a2c19",
  "child_status": "completed" }
```

`subflow.started` / `subflow.completed` are the composition analogues of `node.started` / `node.completed`,
and `child_status` is the bridge the runtime check keys on. `event_version` becomes
`enum: ["agentic-flows.events/v1", "agentic-flows.events/v1.1"]`.

### Layer 4 — Validator: flow catalog and semver-range parser (the foundation)

This layer builds the two things `flowctl` does not have today and that every composition check depends on.
It must land **first**.

**There is no flow_id -> file resolver.** Flows are discovered only by `rglob("flow.yaml")` /
`rglob("flow.yml")` over input paths (`find_flow_files`, `cli.py` ~124–139), and `resolve_flow_source`
(`cli.py` ~917–924) resolves a literal path string, never an id. Nothing maps `engineering.backend-service`
to a file. Build a catalog index:

```text
build_flow_catalog(paths) -> dict[flow_id, list[CatalogEntry]]
  for each flow file found by find_flow_files(paths):
    doc = load_yaml(file); validate against flow schema (skip invalid, collect error)
    index.setdefault(doc.id, []).append(CatalogEntry(id, version, file, document))
  # one id may have several published versions on disk; keep them all
```

**There is no semver-range parser anywhere.** The live `semver` def is the exact-version pattern
`^[0-9]+\.[0-9]+\.[0-9]+$`; nothing parses `>=0.1.0 <0.2.0`. Build a small, dependency-free range parser
covering the constraint grammar this proposal uses:

```text
parse_constraint(text) -> list[Comparator]     # ">=0.1.0 <0.2.0" -> [(>=,0.1.0),(<,0.2.0)]
  split on whitespace; each token is op + semver; ops: >= > <= < = (and ~, ^ if adopted)
satisfies(version, constraint) -> bool         # all comparators hold
resolve(constraint, available_versions) -> str | None
  candidates = [v for v in available if satisfies(v, constraint)]
  return max(candidates by semver order) or None   # highest matching version wins
```

Keep it intentionally small. Pin the grammar in `version_constraint`'s pattern and reject anything the parser
cannot read, rather than silently accepting a constraint it will mis-evaluate. A constraint that does not parse
is a composition error, not a pass.

These two functions are pure and unit-testable in isolation, and every static check in Layer 5 calls one or
both.

### Layer 5 — Validator: `check-composition`

A new command, `flowctl check-composition`, plus a runtime arm folded into `validate-run`. Split into static
(flow-only) and runtime (run-bundle) checks.

**Static checks** (operate on a flow document + the catalog; no run bundle needed):

For each `flow_ref` node:

1. **Resolve** `ref.flow_id` against the catalog. Unknown id -> error.
2. **Parse + satisfy** `version_constraint`. Unparseable constraint -> error. No catalog version satisfies it
   -> error.
3. **`with`-keys subset of child inputs** — every key in `with` is a declared child input/parameter id.
4. **`with` covers all required child inputs** — every required child input id appears as a `with` key
   (composition cannot leave a required child input unbound).
5. **`expose`-keys are declared child outputs** — every key in `expose` is a child `contracts.outputs[].id`.
6. **`produces == set(expose.values())`** — the node's local `produces` is exactly the exposed artifact set, so
   the existing dataflow validator is correct by construction.
7. **Ref-cycle detection** across the cross-flow ref graph — build the directed graph of
   `flow_id -> referenced flow_id` (resolving each ref to its concrete version), and reject any cycle. A flow
   that transitively references itself is unbuildable.
8. **Capability superset** — the parent's `runtime.required_capabilities` is a superset of the union of all
   children's `required_capabilities`. A program cannot run a child whose capability it does not itself
   require. (The webapp program declares `subflow.dispatch` plus the union of child capabilities.)
9. **Core subset** — the parent's `runtime.supported_cores` is a subset of the **intersection** of all
   children's `supported_cores`. The program can only claim a core that every child it composes also supports.

```text
check_composition_static(flow_doc, catalog) -> list[str]:
  ref_graph = {}
  for node in flow_doc.nodes where node.type == "flow_ref":
    entries = catalog.get(node.ref.flow_id)
    if not entries: error("ref to nonexistent flow_id"); continue
    constraint = parse_constraint(node.ref.version_constraint) or error(...)
    child_ver = resolve(constraint, [e.version for e in entries]) or error("unsatisfiable")
    child = entry_for(node.ref.flow_id, child_ver).document
    child_inputs   = {f.id for f in child.contracts.inputs}
    child_required = {f.id for f in child.contracts.inputs if f.required}
    child_outputs  = {f.id for f in child.contracts.outputs}
    for k in node.with:    if k not in child_inputs:  error("with-key not a child input")
    for k in child_required: if k not in node.with:   error("missing required child input")
    for k in node.expose:  if k not in child_outputs: error("expose-value not a child output")
    if set(node.produces) != set(node.expose.values()): error("produces != expose targets")
    require_superset(parent.required_capabilities, child.required_capabilities)
    core_subset(parent.supported_cores, child.supported_cores)
    ref_graph[flow_doc.id].add(child.id)
  detect_cycles(ref_graph)
```

**Runtime checks** (fold into `validate_run_document`, `cli.py` ~392–475 — the recursion is modeled on
`validate_adapter_smoke_document`, `cli.py` ~630–645):

For each `flow_ref` node reachable in the parent's source flow:

1. **Find the matching `sub_runs` entry** by `node_id`. None -> error.
2. **Load the child bundle** at `sub_run.uri` (resolve like an adapter `run_bundle`).
3. **Recurse**: `validate_run_document(child, ...)`, prefixing errors with
   `$.sub_runs[i].uri(<uri>):` exactly as the adapter path prefixes `$.run_bundle(<path>):`.
4. **Assert child completion** — child `run.status == completed` **and** every child *required* gate has
   passed `gate.completed` evidence (the same rule `validate_run_events` already enforces per-run,
   `cli.py` ~880–888, now asserted on the child).
5. **Make the parent `subflows-passed` gate conditional on THIS**, not on a local artifact. The gate passes
   iff every reachable `flow_ref` node has a `sub_runs` entry whose child bundle recursively validates and whose
   child required gates passed. A passed `subflows-passed` gate with no sub-run evidence is an error.

```text
# inside validate_run_document, after the existing event/output checks
flow_ref_nodes = {n.id: n for n in flow_doc.nodes if n.type == "flow_ref" and n.id in reachable}
sub_runs = {s.node_id: s for s in document.get("sub_runs", [])}
for node_id, node in flow_ref_nodes.items():
    s = sub_runs.get(node_id)
    if not s: error(f"$.sub_runs: no sub_run for flow_ref node '{node_id}'"); continue
    if s.flow.id != node.ref.flow_id: error("sub_run flow_id does not match node ref")
    child_path = resolve_adapter_artifact_source(s.uri, run_path)
    child = load_json(child_path)
    for e in validate_run_document(child, run_schema, event_schema, flow_schema, run_path=child_path):
        error(f"$.sub_runs[{node_id}].uri({s.uri}): {e}")
    if child.run.status != "completed":
        error(f"$.sub_runs[{node_id}]: child run.status is '{child.run.status}', expected completed")
    # child required-gate check is performed by the recursive call above
# 1:1 correspondence (see Honesty rules)
for s in document.get("sub_runs", []):
    if s.node_id not in flow_ref_nodes:
        error(f"$.sub_runs: '{s.node_id}' is not a reachable flow_ref node")
```

### Layer 6 — Versioning and process

- **Transitive deprecation.** A child flow may not be deleted while any parent pins it. Extend the deprecation
  rules in `docs/versioning.md` and the catalog walk in `validate_deprecation_targets` (`cli.py` ~1882) so a
  delete or deprecate of a referenced child is flagged. `release-check` (`cmd_release_check` /
  `validate_release_readiness`, `cli.py` ~1685–1736) gains a **dangling-ref** check: every `ref.flow_id` in
  every release flow resolves in the release catalog at a version satisfying its constraint.
- **Record the resolved version.** Each `sub_runs[].flow.version` is the concrete child version chosen for
  that run, so a replay is deterministic even after the child publishes a new in-range version. The constraint
  lives in the flow; the resolution lives in the run.
- **Docs.** Add a `## Sub-flow composition` section to `docs/flow-spec.md` (the `flow_ref` node, its fields,
  the static and runtime checks); a `## Sub-runs` section to `docs/run-bundles.md` (the `sub_runs` array and
  recursive validation); a `subflow.started` / `subflow.completed` entry to `docs/event-streams.md`; a
  transitive-deprecation subsection to `docs/versioning.md`; and a `CHANGELOG.md` entry describing the
  additive v1.1 surface.

## Honesty rules

These are the invariants that make composition evidence mean what it claims. They are the composition
analogues of the existing run rules (e.g. "every required gate needs a passed `gate.completed`",
`cli.py` ~880–888).

1. **A failed or partial child forces the parent to be incomplete.** If any reachable child's `run.status` is
   in `{failed, cancelled, running}`, or any child *required* gate did not pass, the parent run **must not** be
   `status: completed`. A `completed` parent with a non-completed child is a validation error, not a warning.
2. **1:1 correspondence between reachable `flow_ref` nodes and `sub_runs` entries.** Every reachable
   `flow_ref` node has exactly one `sub_runs` entry, and every `sub_runs` entry's `node_id` is a real,
   reachable `flow_ref` node whose `ref.flow_id` matches `sub_runs[].flow.id`. No orphan sub-runs; no
   unaccounted-for `flow_ref` nodes.
3. **Every reachable `flow_ref` node needs a `subflow.completed` event.** This mirrors "every required gate
   needs a passed `gate.completed`." A `flow_ref` node with no `subflow.completed` event for its `node_id` is
   an incomplete run.

## Inherent limit

State this; do not paper over it.

Even a recursively validated child bundle is an **agent-authorable JSON file.** `flowctl` never dereferences
evidence `uri`s, and `sha256` is **format-checked, not computed** (`collect_event_evidence_refs` reads only
`id`/`kind`, `cli.py` ~893–908; the run/event schemas accept any 64-hex string for `sha256`). So composition
evidence **attests structure, not execution.** A sufficiently determined author can hand-write a parent bundle,
hand-write a child bundle that recursively validates, point one at the other, and pass — having run nothing.

Recursive validation closes the *trivial* lie ("sub-flows passed, trust me," no link at all). It does not and
cannot close the *diligent* lie (a fully consistent fabricated child). The fix is not in this layer; it is the
provenance guardrail from the lifecycle-evidence reframe (`docs/proposals/lifecycle-evidence-reframe.md`):
`sub_runs` need a **runtime/verifier-issued, non-self-forgeable signal** — a signed or content-addressed child
bundle whose authenticity a parent cannot mint. With that, `flowctl` checks *consistency* and the runtime
attests *authenticity*. The docs must say exactly this, in these words: **flowctl checks consistency;
authenticity is the runtime's burden.**

## Negative-fixture matrix

Each composition check ships with a fixture that must fail. One row per failure mode.

| # | Failure mode | Layer / check | Where it fires |
| --- | --- | --- | --- |
| 1 | `version_constraint` satisfied by no catalog version | 4/5 static | `check-composition` |
| 2 | `ref.flow_id` resolves to no catalog flow | 4/5 static | `check-composition` |
| 3 | Ref cycle (A -> B -> A) across the ref graph | 5 static | `check-composition` |
| 4 | `with`-key is not a declared child input | 5 static | `check-composition` |
| 5 | A required child input has no `with` binding | 5 static | `check-composition` |
| 6 | `expose`-value is not a declared child output | 5 static | `check-composition` |
| 7 | `produces != set(expose.values())` | 5 static | `check-composition` |
| 8 | Parent lacks a capability some child requires | 5 static | `check-composition` |
| 9 | `sub_run` points at a child whose required gate did **not** pass | 5 runtime | `validate-run` |
| 10 | `sub_run.run.status != completed` | 5 runtime + honesty 1 | `validate-run` |
| 11 | A reachable `flow_ref` node has no `sub_run` | 5 runtime + honesty 2 | `validate-run` |
| 12 | Parent `subflows-passed` gate passes with no sub-run evidence | 5 runtime + honesty 3 | `validate-run` |

## New surface area

- **Events**: `subflow.started`, `subflow.completed` (declared in a composing flow's `observability.events`;
  payload shapes in [Layer 3](#layer-3--event-model)).
- **Capability**: `subflow.dispatch` (a composing flow declares it in `runtime.required_capabilities`; a core
  that cannot dispatch child runs cannot run the program).
- **Command**: `flowctl check-composition` (static catalog/version/binding/cycle/capability/core checks),
  with the runtime arm folded into `flowctl validate-run`.

## Build order

The order is forced by dependency. Each step is shippable and testable before the next.

1. **Catalog + semver** (Layer 4) — `build_flow_catalog`, `parse_constraint` / `satisfies` / `resolve`. Pure,
   unit-tested, no schema change yet. Nothing else can be built without these.
2. **`flow_ref` node + static `check-composition`** (Layers 1 + 5-static, the v1.1 authoring surface) — flow
   schema diff, `check-composition` command, fixtures 1–8. The webapp program in the appendix validates at the
   end of this step (it already passes the additive v1.1 schema and all flowctl semantic checks).
3. **`sub_runs` + recursive run validation** (Layers 2 + 3 + 5-runtime) — run/event schema diffs, the
   recursion folded into `validate_run_document`, the honesty rules, fixtures 9–12. This is the step that fixes
   the empirical finding: the fabricated parent run now fails.
4. **Provenance + transitive versioning + remaining fixtures** (Layer 6 + the reframe's provenance signal) —
   transitive deprecation, `release-check` dangling-ref, resolved-version replay, the non-self-forgeable
   `sub_runs` signal, doc updates.

This is **Phase 3** of the lifecycle-evidence reframe. Steps 1–2 deliver expressibility; step 3 delivers
honest evidence; step 4 delivers authenticity. Stopping after step 2 ships a feature that *looks* validated and
is not — so step 3 is the minimum honest cut, and the proposal's recommendation is to ship 1–3 together.

## Appendix: worked parent program

`program.webapp-build` composes `design.website-to-spec`, `engineering.backend-service`, and
`engineering.frontend-build`. It passes the additive v1.1 schema and every flowctl semantic check
(reachability, edge targets, requires-from-upstream, required-output-produced, gate `evidence_refs`). It
declares `subflow.dispatch`, the `subflow.started` / `subflow.completed` events, and a `subflows-passed` gate
that — under this proposal — becomes conditional on recursive child validation (Layer 5 runtime), not on a
local artifact.

```yaml
spec_version: agentic-flows/v1.1
id: program.webapp-build
version: 0.1.0
title: Web app build program
summary: Compose design-to-spec, frontend build, and backend build sub-flows into
  one evidence-backed program.
stability: experimental
owners:
- RNT56
tags:
- program
- webapp
- composition
entrypoint: intake
runtime:
  supported_cores:
  - nilcore
  - standalone
  required_capabilities:
  - repo.checkout
  - command.run
  - evidence.capture
  - env.ephemeral-datastore
  - env.headless-browser
  - subflow.dispatch
contracts:
  inputs:
  - id: product_brief
    type: markdown
    required: true
  - id: stack
    type: text
    required: true
  - id: repo
    type: uri
    required: true
  outputs:
  - id: app_patch
    type: patch
    required: true
  - id: closeout
    type: markdown
    required: true
  artifacts:
  - design-spec
  - frontend-patch
  - backend-patch
  - integration-report
nodes:
- id: intake
  type: intake
  title: Intake brief
  description: Capture the product brief, stack, and repo.
  produces:
  - program-scope
- id: plan
  type: plan
  title: Plan the build program
  description: Order the sub-flows and bind their inputs.
  requires:
  - program-scope
  produces:
  - program-plan
- id: design
  type: flow_ref
  title: Design to spec
  description: Run the design-to-spec sub-flow to produce an approved design spec.
  ref:
    flow_id: design.website-to-spec
    version_constraint: '>=0.1.0 <0.2.0'
  with:
    brief: '{{input.product_brief}}'
  expose:
    design_spec: design-spec
  requires:
  - program-plan
  produces:
  - design-spec
- id: backend
  type: flow_ref
  title: Build backend
  description: Run the backend-service sub-flow against an ephemeral datastore.
  ref:
    flow_id: engineering.backend-service
    version_constraint: '>=0.1.0 <0.2.0'
  with:
    target_spec: '{{artifact.design-spec}}'
    stack: '{{input.stack}}'
    repo: '{{input.repo}}'
  expose:
    service_patch: backend-patch
  requires:
  - design-spec
  produces:
  - backend-patch
- id: frontend
  type: flow_ref
  title: Build frontend
  description: Run the frontend-build sub-flow in the chosen stack.
  ref:
    flow_id: engineering.frontend-build
    version_constraint: '>=0.1.0 <0.2.0'
  with:
    design_spec: '{{artifact.design-spec}}'
    stack: '{{input.stack}}'
    repo: '{{input.repo}}'
  expose:
    frontend_patch: frontend-patch
  requires:
  - design-spec
  produces:
  - frontend-patch
- id: integrate
  type: verifier
  title: Integrate and verify
  description: Verify the frontend and backend integrate and the program acceptance
    gates pass.
  requires:
  - frontend-patch
  - backend-patch
  produces:
  - integration-report
  - app_patch
- id: approve
  type: approval
  title: Operator sign-off
  description: Operator approves the assembled application before closeout.
  requires:
  - integration-report
- id: final
  type: finalizer
  title: Close out program
  description: Return the assembled app patch and closeout.
  requires:
  - integration-report
  produces:
  - closeout
edges:
- from: intake
  to: plan
- from: plan
  to: design
- from: design
  to: backend
- from: design
  to: frontend
- from: backend
  to: integrate
- from: frontend
  to: integrate
- from: integrate
  to: approve
- from: approve
  to: final
quality_gates:
- id: subflows-passed
  title: Every sub-flow run passed its own required gates
  type: artifact
  required: true
  evidence: Each flow_ref node references a nested run bundle whose required gates
    passed.
  evidence_refs:
  - integration-report
- id: integration-verified
  title: Frontend and backend integrate
  type: review
  required: true
  evidence: Integration verifier confirms the assembled app works end to end.
  evidence_refs:
  - integration-report
observability:
  events:
  - flow.started
  - node.completed
  - subflow.started
  - subflow.completed
  - gate.completed
  - flow.completed
  metrics:
  - subflows.count
  - duration.seconds
```

## References

- `docs/goals.md` — mission, primary goal 6 (pin compatible versions), evidence-over-assertion, the not-a-runtime non-goal.
- `docs/buildable-now.md` — sub-flow composition under needs-spec-extension; blocks `program.product-release-autopilot`; the evidence-honesty bar.
- `docs/flow-spec.md`, `docs/run-bundles.md`, `docs/event-streams.md`, `docs/versioning.md` — docs to update in Layer 6.
- `docs/proposals/lifecycle-evidence-reframe.md` — the provenance guardrail; this proposal is Phase 3.
- `schemas/flow.schema.json`, `schemas/run.schema.json`, `schemas/event.schema.json` — live schemas (`additionalProperties: false`).
- `docs/proposals/schemas/flow.schema.v1_1.json`, `docs/proposals/schemas/run.schema.v1_1.json`, `docs/proposals/schemas/event.schema.v1_1.json` — the additive v1.1 schemas this proposal references.
- `tools/flowctl/flowctl/cli.py` — `validate_run_document` (~392), `validate_adapter_smoke_document` recursion (~630), `validate_run_events` (~807), `collect_event_evidence_refs` (~893), `resolve_flow_source` (~917), `resolve_adapter_artifact_source` (~937), `validate_requirements_and_outputs` (~1054), `validate_deprecation_targets` (~1882), `cmd_release_check` (~1685).
