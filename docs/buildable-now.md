# Buildable-now workflow assessment

This document records which workflows from [todo-workflows.md](../todo-workflows.md) can be built **end-to-end now**, inside this repo's contract and evidence model, without inventing new schema primitives and without fabricating real external state.

It is a planning aid, not a contract. It is regenerated when the backlog or the spec changes.

## What "end-to-end now" means

A workflow is buildable end-to-end now only when the full artifact set can be authored here today and pass every `flowctl` validator with honest evidence, mirroring the three reference flows (`coding.feature-implementation`, `collaboration.multi-agent-supervisor`, `general.human-in-the-loop-review`):

1. `flows/<area>/<name>/flow.yaml` valid against `schemas/flow.schema.json` and the semantic checks.
2. `flows/<area>/<name>/README.md` with a `## Maturity rubric`.
3. `examples/samples/<area>/<name>.sample.json` whose inputs and expected outputs match the contract.
4. `examples/runs/<name>.run.json`, a completed standalone run bundle.
5. An optional multi-file event stream under `examples/streams/<name>/`.
6. A repo-local contract-smoke `examples/adapters/<consumer>-<name>.adapter-smoke.json` per consumer, each with a target-core run bundle and a negative fixture.

## The real discriminator: evidence honesty

Almost every backlog workflow is *expressible* in the current spec. Loops are available through cyclic edges plus edge conditions (see the `revise -> assess` back-edge in `general.human-in-the-loop-review`), and branching is available through `decision` nodes. The decisive question is therefore not expressibility but whether a completed standalone run bundle is an honest contract demonstration or a misrepresentation:

- **Faithful standalone** — evidence is naturally a repo-local artifact (a diff, test log, cited report, decision record, capability matrix, or the repo's own run and stream bundles). Build now.
- **Requires real external state** — meaning depends on live deployment health, real secret rotation, real cloud billing, production metrics, live CI or PR state, or third-party connectors. A "completed" run would fabricate that state. Defer.

## Assessment summary

Of 83 assessed workflows (78 numbered backlog items plus 5 Wave 0 spine items):

| Verdict | Count | Meaning |
| --- | --- | --- |
| build-now-e2e | 46 | Full honest artifact set is authorable today. |
| contract-first | 16 | Ship `flow.yaml` + README + sample now; run and adapter evidence would be illustrative-only. |
| needs-spec-extension | 2 | Needs a primitive the closed spec lacks (loop, fan-out, or sub-flow). |
| defer | 19 | Meaning depends on real external state the repo cannot honestly stand in for. |

## Recommended first batch

The integration spine plus the two product anchors. The first three are shipped in this catalog; the rest are the next increment.

1. `ops.flow-intake-and-routing` — shipped.
2. `ops.capability-negotiation` — shipped.
3. `ops.event-and-evidence-bridge` — shipped.
4. `engineering.issue-to-verified-pr` — near-structural twin of `coding.feature-implementation`.
5. `proof.verified-patch-acceptance` — canonical CrustCore verifier-completion pattern.
6. `ops.adapter-certification` — its deliverable is the adapter-smoke artifact itself.

## Honesty corrections to the official build order

The build order in `todo-workflows.md` lists three items that are not honestly buildable end-to-end now:

- `personal.daily-command-center` (#4) — defer; depends on live inboxes, calendar, and approvals.
- `engineering.release-train` (#9) — defer; pushing a tag and publishing a release are irreversible external actions.
- `program.product-release-autopilot` (#15) — defer; depends on real deployment health and needs sub-flow composition.

## Needs spec extension

| Primitive | What it unblocks |
| --- | --- |
| Bounded loop / iteration node | `program.repo-maintenance-autopilot`, `program.security-hardening-campaign`; recurring reviews in `research.competitor-watch` and `research.technology-radar`. |
| Parallel fan-out cardinality | One-node-to-N-instances execution with per-instance evidence aggregation; today a swarm is modeled as a single dispatch node. |
| Sub-flow composition | Multi-stage programs such as `program.product-release-autopilot` that should compose other flows. |
| Scheduler / cron trigger | Recurring watch cadence; note these items also require real external evidence, so the trigger alone does not make them honest. |

## Defer (depends on real external state)

`personal.daily-command-center`, `personal.inbox-triage-and-reply`, `engineering.browser-regression`, `engineering.merge-readiness`, `engineering.release-train`, `engineering.cross-platform-regression`, `security.secret-leak-response`, `research.competitor-watch`, `ops.deploy-and-verify`, `ops.rollback`, `ops.infrastructure-drift`, `ops.backup-restore-drill`, `ops.cost-anomaly`, `ops.scheduler-health`, `product.experiment-readout`, `product.pricing-or-packaging-analysis`, `product.customer-success-brief`, `product.churn-risk-review`, `program.product-release-autopilot`.
