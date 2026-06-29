# Proposals

Design records for the `agentic-flows/v1.1` reframe, **now adopted**. The two documents below were
written as forward-looking proposals; v1.1 has since landed additively in the live `schemas/` and is
enforced by `flowctl` (see [CHANGELOG.md](../../CHANGELOG.md) and [flow-spec.md](../flow-spec.md)). They
are retained as the design rationale, not as pending work.

## Documents

| Proposal | What it does |
| --- | --- |
| [Lifecycle and evidence reframe](lifecycle-evidence-reframe.md) | Reframes the project so generative / in-depth flows (build-a-backend, build-a-frontend, design-a-website, composed programs) become first-class. One keystone (typed `evidence_class`) plus five additive shifts and six guardrails. |
| [Sub-flow composition](sub-flow-composition.md) | Specs the `flow_ref` node so one flow can run another as a step (Phase 3 of the reframe). Includes the empirical finding that the naive evidence model is already broken, and the six layers needed to make composition evidence honest. |

## Draft schemas

The original additive `v1.1` schema drafts, under [`schemas/`](schemas/). These have since been **merged into
the live `schemas/*.json`** (they differ only by `$id`); they are kept here as the historical drafts that
accompanied the proposals. The live schemas are the source of truth.

| File | Adds |
| --- | --- |
| [`flow.schema.v1_1.json`](schemas/flow.schema.v1_1.json) | `parameters`; node `flow_ref`/`ref`/`with`/`expose`/`environment`/`iteration`/`fan_out`; gate types `judgment`/`acceptance`/`probe`; gate `evidence_class`/`acceptance_spec`/`reviewer_id`/`criteria`/`threshold`. |
| [`node.schema.v1_1.json`](schemas/node.schema.v1_1.json) | The standalone-node counterpart of the node additions above. |
| [`run.schema.v1_1.json`](schemas/run.schema.v1_1.json) | `sub_runs` array (links a parent run to its children). |
| [`event.schema.v1_1.json`](schemas/event.schema.v1_1.json) | `sub_run` link; `evidence_class` on evidence items. |
| [`capability-registry.schema.json`](schemas/capability-registry.schema.json) | Closed, classified capability vocabulary with advisory per-core ownership. |
| [`runtime-profile.schema.json`](schemas/runtime-profile.schema.json) | What capabilities a runtime implements and which evidence classes it may not emit. |

## Adoption status

The v1.1 surface landed additively (a strict superset — every existing `v1` flow validates unchanged) and is
now enforced by `flowctl`:

- **`flow_ref` composition** — static `flowctl check-composition` plus recursive `sub_runs` validation in
  `flowctl validate-run`.
- **`evidence_class`** — class-match and the standalone-honesty rule in `validate-run`.
- **`parameters`** — `{{param.x}}` resolution and `enum` `choices` in `validate`.
- **`judgment`/`acceptance` reviewer-identity** — no self-review, in `validate-run`.
- **`iteration` / `fan_out`** — mandatory bounds in `validate`.
- **`environment` + provenance** — `sandbox-run` evidence must be backed by a non-self-issued
  `env.provisioned` event with teardown, in `validate-run`.

The worked `program.webapp-build` flow and its recursively-validated child run bundles ship under
[`flows/program/webapp-build`](../../flows/program/webapp-build) and
[`examples/runs/`](../../examples/runs/).

> Note: `flowctl` checks evidence-class and provenance **consistency**, not **authenticity** — the runtime
> attests that a `sandbox-run` log or a reviewer decision is genuine. See the "inherent limit" section of the
> sub-flow doc and the guardrails of the reframe doc for that boundary.
