# Changelog

All notable changes to this project will be documented in this file.

This project follows semantic versioning for releases and keeps flow compatibility notes in the relevant release section.

## Unreleased

### Added

- Added the project operating handbook under `docs/`.
- Added changelog and release management guidance.
- Added `flowctl validate-event` for event artifact validation.
- Added CI coverage for event validation.
- Added `schemas/run.schema.json` for completed run bundles.
- Added `flowctl validate-run` for source-flow, event, output, and gate-evidence validation.
- Added `flowctl report` for catalog maturity and optional-consumer summaries.
- Added a completed feature implementation run example.
- Added a compatibility matrix and run-bundle guidance.
- Added a release notes template.
- Added a pull request checklist for validation and independent-consumer framing.
- Clarified that ThinClaw, NilCore, and CrustCore are independent optional consumers, not an already-integrated stack.

## 0.1.0 - 2026-06-27

### Added

- Initialized the `agentic-flows` repository.
- Added schemas for flows, nodes, and events.
- Added the `flowctl` CLI with flow validation, listing, and graph export.
- Added initial reusable flows for coding, research, collaboration, and review workflows.
- Added starter templates for feature, refactor, and research report workflows.
- Added adapter contract sketches for ThinClaw, NilCore, and CrustCore.
- Added GitHub Actions validation.
