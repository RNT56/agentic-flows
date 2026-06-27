# Governance

## Ownership

This repository owns:

- flow definitions
- schemas
- validation tooling
- adapter contracts
- examples
- documentation and release process

The consuming cores own:

- runtime execution
- sandboxing
- memory
- operator UX
- policy enforcement
- proof generation

## Review requirements

Require review for:

- schema changes
- stable flow changes
- adapter contract changes
- release process changes
- removal or deprecation of consumed flows

## Compatibility policy

- Additive schema changes are allowed within the same major spec version.
- Breaking schema changes require a new `spec_version`.
- Flows should not remove required inputs, outputs, or gates without a major flow version bump.
- A flow should not list a core as supported without loader evidence once adapter smoke tests exist.

## Deprecation policy

Deprecated flows must include:

- replacement flow
- reason for deprecation
- migration guidance
- removal target release

## Decision records

Use lightweight docs or issues for major decisions.

Decision records should capture:

- context
- decision
- alternatives considered
- compatibility impact
- follow-up tasks

