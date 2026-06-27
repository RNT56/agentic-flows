from pathlib import Path

import json

from flowctl.cli import (
    DEFAULT_SCHEMA,
    build_report_summary,
    find_flow_files,
    find_json_files,
    load_json,
    load_yaml,
    validate_event_document,
    validate_flow_document,
    validate_run_document,
)


def test_repository_flows_are_valid() -> None:
    schema = load_json(DEFAULT_SCHEMA)
    failures: list[str] = []

    for path in find_flow_files([]):
        errors = validate_flow_document(load_yaml(path), schema)
        if errors:
            failures.append(f"{path}: {errors}")

    assert failures == []


def test_missing_edge_target_is_rejected() -> None:
    schema = load_json(DEFAULT_SCHEMA)
    invalid = load_yaml(Path("tests/fixtures/invalid-missing-node.yaml"))

    errors = validate_flow_document(invalid, schema)

    assert any("references missing node 'verify'" in error for error in errors)


def test_sample_event_matches_event_schema() -> None:
    schema = load_json(Path("schemas/event.schema.json"))
    with Path("examples/standalone/event.sample.json").open("r", encoding="utf-8") as handle:
        event = json.load(handle)

    errors = validate_event_document(event, schema)

    assert errors == []


def test_invalid_event_is_rejected() -> None:
    schema = load_json(Path("schemas/event.schema.json"))
    invalid = load_json(Path("tests/fixtures/invalid-event.json"))

    errors = validate_event_document(invalid, schema)

    assert any("$.timestamp" in error for error in errors)
    assert any("$.severity" in error for error in errors)


def test_event_discovery_excludes_run_bundles() -> None:
    paths = find_json_files([Path("examples")])

    assert Path("examples/standalone/event.sample.json").resolve() in paths
    assert Path("examples/runs/feature-implementation.run.json").resolve() not in paths


def test_sample_run_bundle_is_valid() -> None:
    run_schema = load_json(Path("schemas/run.schema.json"))
    event_schema = load_json(Path("schemas/event.schema.json"))
    flow_schema = load_json(DEFAULT_SCHEMA)
    run = load_json(Path("examples/runs/feature-implementation.run.json"))

    errors = validate_run_document(
        run,
        run_schema,
        event_schema,
        flow_schema,
        run_path=Path("examples/runs/feature-implementation.run.json"),
    )

    assert errors == []


def test_run_bundle_missing_required_gate_is_rejected() -> None:
    run_schema = load_json(Path("schemas/run.schema.json"))
    event_schema = load_json(Path("schemas/event.schema.json"))
    flow_schema = load_json(DEFAULT_SCHEMA)
    run = load_json(Path("tests/fixtures/invalid-run-missing-gate.json"))

    errors = validate_run_document(
        run,
        run_schema,
        event_schema,
        flow_schema,
        run_path=Path("tests/fixtures/invalid-run-missing-gate.json"),
    )

    assert any("required quality gate 'project-checks-pass'" in error for error in errors)
    assert any("$.outputs.patch" in error for error in errors)


def test_report_summary_counts_stability_and_cores() -> None:
    summary = build_report_summary(
        [
            {"stability": "preview", "valid": True, "issues": [], "supported_cores": ["standalone", "nilcore"]},
            {"stability": "experimental", "valid": True, "issues": ["needs README"], "supported_cores": ["standalone"]},
        ]
    )

    assert summary["total"] == 2
    assert summary["valid"] == 2
    assert summary["with_issues"] == 1
    assert summary["by_stability"] == {"experimental": 1, "preview": 1}
    assert summary["by_optional_consumer"] == {"nilcore": 1, "standalone": 2}
