from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import unquote

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised by users without deps
    raise SystemExit("PyYAML is required. Install with: python -m pip install -e .") from exc

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError as exc:  # pragma: no cover - exercised by users without deps
    raise SystemExit("jsonschema is required. Install with: python -m pip install -e .") from exc

from flowctl import composition


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SCHEMA = REPO_ROOT / "schemas" / "flow.schema.json"
DEFAULT_ADAPTER_SMOKE_SCHEMA = REPO_ROOT / "schemas" / "adapter-smoke.schema.json"
DEFAULT_EVENT_SCHEMA = REPO_ROOT / "schemas" / "event.schema.json"
DEFAULT_EVENT_STREAM_SCHEMA = REPO_ROOT / "schemas" / "event-stream.schema.json"
DEFAULT_RUN_SCHEMA = REPO_ROOT / "schemas" / "run.schema.json"
DEFAULT_SAMPLE_SCHEMA = REPO_ROOT / "schemas" / "sample.schema.json"
DEFAULT_SEARCH_ROOTS = [REPO_ROOT / "flows", REPO_ROOT / "templates"]
DEFAULT_ADAPTER_SMOKE_SEARCH_ROOTS = [REPO_ROOT / "examples" / "adapters"]
DEFAULT_EVENT_SEARCH_ROOTS = [REPO_ROOT / "examples"]
DEFAULT_EVENT_STREAM_SEARCH_ROOTS = [REPO_ROOT / "examples" / "streams"]
DEFAULT_RUN_SEARCH_ROOTS = [REPO_ROOT / "examples" / "runs"]
DEFAULT_SAMPLE_SEARCH_ROOTS = [REPO_ROOT / "examples" / "samples"]
DEFAULT_MARKDOWN_SEARCH_ROOTS = [
    REPO_ROOT / "README.md",
    REPO_ROOT / "CONTRIBUTING.md",
    REPO_ROOT / "CHANGELOG.md",
    REPO_ROOT / "docs",
    REPO_ROOT / "flows",
    REPO_ROOT / "templates",
    REPO_ROOT / "examples",
    REPO_ROOT / "integrations",
]
DEFAULT_RELEASE_PACKAGE_PATHS = [
    REPO_ROOT / "README.md",
    REPO_ROOT / "CHANGELOG.md",
    REPO_ROOT / "LICENSE",
    REPO_ROOT / "schemas",
    REPO_ROOT / "flows",
    REPO_ROOT / "templates",
    REPO_ROOT / "examples" / "samples",
    REPO_ROOT / "docs" / "release-notes-template.md",
    REPO_ROOT / "docs" / "compatibility-matrix.md",
    REPO_ROOT / "docs" / "versioning.md",
]
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
OPTIONAL_CONSUMERS = {"crustcore", "nilcore", "thinclaw"}
EVIDENCE_CLASS_ORDER = {
    "deterministic": 0,
    "fixture": 1,
    "sandbox-run": 2,
    "judgment": 3,
    "external-production": 4,
}
STANDALONE_FORBIDDEN_EVIDENCE_CLASSES = {"sandbox-run", "external-production"}
MARKDOWN_LINK_PATTERN = re.compile(r"!?\[[^\]]*]\(([^)]+)\)")
PARAM_REFERENCE_PATTERN = re.compile(r"\{\{\s*param\.([a-z][a-z0-9_-]*)(?:\.[a-z0-9_-]+)?\s*\}\}")
FLOW_KEY_ORDER = [
    "spec_version",
    "id",
    "version",
    "title",
    "summary",
    "stability",
    "deprecated_by",
    "migration",
    "owners",
    "tags",
    "entrypoint",
    "runtime",
    "contracts",
    "parameters",
    "nodes",
    "edges",
    "quality_gates",
    "observability",
]
MIGRATION_KEY_ORDER = ["summary", "steps"]
RUNTIME_KEY_ORDER = ["supported_cores", "required_capabilities", "adapter_hints"]
CONTRACTS_KEY_ORDER = ["inputs", "outputs", "artifacts"]
CONTRACT_FIELD_KEY_ORDER = ["id", "type", "required", "description"]
NODE_KEY_ORDER = [
    "id",
    "type",
    "title",
    "description",
    "instructions",
    "command",
    "parameters",
    "inputs_schema",
    "outputs_schema",
    "agent",
    "tool",
    "timeout_seconds",
    "requires",
    "produces",
    "ref",
    "with",
    "expose",
    "environment",
    "iteration",
    "fan_out",
    "on_failure",
    "policy",
]
PARAMETER_KEY_ORDER = ["id", "type", "required", "choices", "default", "description"]
NODE_FIELD_KEY_ORDER = ["id", "type", "required", "description"]
ON_FAILURE_KEY_ORDER = ["action", "max_attempts", "fallback_node"]
EDGE_KEY_ORDER = ["from", "to", "condition"]
QUALITY_GATE_KEY_ORDER = [
    "id",
    "title",
    "type",
    "required",
    "command",
    "evidence",
    "evidence_refs",
    "evidence_class",
    "evidence_class_min",
    "criteria",
    "reviewer_id",
    "acceptance_spec",
    "threshold",
]
PARAMETER_KEY_ORDER = ["id", "type", "required", "choices", "default", "description"]
OBSERVABILITY_KEY_ORDER = ["events", "metrics"]


class IndentedSafeDumper(yaml.SafeDumper):
    def increase_indent(self, flow: bool = False, indentless: bool = False) -> Any:
        return super().increase_indent(flow, False)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)
    if not isinstance(loaded, dict):
        raise ValueError(f"{path}: expected a YAML mapping at document root")
    return loaded


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        loaded = json.load(handle)
    if not isinstance(loaded, dict):
        raise ValueError(f"{path}: expected a JSON object at document root")
    return loaded


def find_flow_files(paths: Iterable[Path]) -> list[Path]:
    selected = list(paths)
    if not selected:
        selected = DEFAULT_SEARCH_ROOTS

    files: list[Path] = []
    for path in selected:
        path = path.resolve()
        if path.is_file():
            files.append(path)
            continue
        if not path.exists():
            files.append(path)
            continue
        files.extend(sorted(path.rglob("flow.yaml")))
        files.extend(sorted(path.rglob("flow.yml")))

    return sorted(dict.fromkeys(files))


def build_flow_catalog(
    paths: Iterable[Path],
) -> tuple[dict[str, list[dict[str, Any]]], list[str]]:
    """Index every flow file by id -> [{version, path, document}], for composition resolution."""
    catalog: dict[str, list[dict[str, Any]]] = {}
    errors: list[str] = []
    for path in find_flow_files(paths):
        if not path.exists():
            continue
        try:
            document = load_yaml(path)
        except Exception as exc:  # noqa: BLE001 - catalog build should report file context
            errors.append(f"{display_path(path)}: {exc}")
            continue
        flow_id = document.get("id")
        version = document.get("version")
        if not isinstance(flow_id, str) or not isinstance(version, str):
            continue
        catalog.setdefault(flow_id, []).append({"version": version, "path": path, "document": document})
    return catalog, errors


def find_json_files(paths: Iterable[Path]) -> list[Path]:
    selected = list(paths)
    if not selected:
        selected = DEFAULT_EVENT_SEARCH_ROOTS

    files: list[Path] = []
    for path in selected:
        path = path.resolve()
        if path.is_file():
            if not is_structured_example_json(path):
                files.append(path)
            continue
        if not path.exists():
            files.append(path)
            continue
        files.extend(path for path in sorted(path.rglob("*.json")) if not is_structured_example_json(path))

    return sorted(dict.fromkeys(files))


def find_adapter_smoke_files(paths: Iterable[Path]) -> list[Path]:
    selected = list(paths)
    if not selected:
        selected = DEFAULT_ADAPTER_SMOKE_SEARCH_ROOTS

    files: list[Path] = []
    for path in selected:
        path = path.resolve()
        if path.is_file():
            files.append(path)
            continue
        if not path.exists():
            files.append(path)
            continue
        files.extend(sorted(path.rglob("*.adapter-smoke.json")))

    return sorted(dict.fromkeys(files))


def find_run_files(paths: Iterable[Path]) -> list[Path]:
    selected = list(paths)
    if not selected:
        selected = DEFAULT_RUN_SEARCH_ROOTS

    files: list[Path] = []
    for path in selected:
        path = path.resolve()
        if path.is_file():
            files.append(path)
            continue
        if not path.exists():
            files.append(path)
            continue
        files.extend(sorted(path.rglob("*.run.json")))

    return sorted(dict.fromkeys(files))


def find_event_stream_files(paths: Iterable[Path]) -> list[Path]:
    selected = list(paths)
    if not selected:
        selected = DEFAULT_EVENT_STREAM_SEARCH_ROOTS

    files: list[Path] = []
    for path in selected:
        path = path.resolve()
        if path.is_file():
            files.append(path)
            continue
        if not path.exists():
            files.append(path)
            continue
        files.extend(sorted(path.rglob("*.stream.json")))

    return sorted(dict.fromkeys(files))


def find_sample_files(paths: Iterable[Path]) -> list[Path]:
    selected = list(paths)
    if not selected:
        selected = DEFAULT_SAMPLE_SEARCH_ROOTS

    files: list[Path] = []
    for path in selected:
        path = path.resolve()
        if path.is_file():
            files.append(path)
            continue
        if not path.exists():
            files.append(path)
            continue
        files.extend(sorted(path.rglob("*.sample.json")))

    return sorted(dict.fromkeys(files))


def find_markdown_files(paths: Iterable[Path]) -> list[Path]:
    selected = list(paths)
    if not selected:
        selected = DEFAULT_MARKDOWN_SEARCH_ROOTS

    files: list[Path] = []
    for path in selected:
        path = path.resolve()
        if path.is_file():
            if path.suffix.lower() == ".md":
                files.append(path)
            continue
        if not path.exists():
            files.append(path)
            continue
        files.extend(sorted(path.rglob("*.md")))

    return sorted(dict.fromkeys(files))


def is_structured_example_json(path: Path) -> bool:
    return (
        path.name.endswith(".run.json")
        or path.name.endswith(".adapter-smoke.json")
        or path.name.endswith(".stream.json")
        or ("samples" in path.parts and path.name.endswith(".sample.json"))
        or "artifacts" in path.parts
    )


def format_error_path(parts: Iterable[Any]) -> str:
    path = "$"
    for part in parts:
        if isinstance(part, int):
            path += f"[{part}]"
        else:
            path += f".{part}"
    return path


def display_path(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(REPO_ROOT)) if resolved.is_relative_to(REPO_ROOT) else str(path)


def validate_flow_document(document: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = [
        f"{format_error_path(error.path)}: {error.message}"
        for error in sorted(validator.iter_errors(document), key=lambda err: list(err.path))
    ]
    errors.extend(validate_semantics(document))
    return errors


def normalize_flow_document(document: dict[str, Any]) -> dict[str, Any]:
    return order_mapping(
        document,
        FLOW_KEY_ORDER,
        child_orders={
            "migration": MIGRATION_KEY_ORDER,
            "runtime": RUNTIME_KEY_ORDER,
            "contracts": CONTRACTS_KEY_ORDER,
            "observability": OBSERVABILITY_KEY_ORDER,
            "on_failure": ON_FAILURE_KEY_ORDER,
        },
        list_child_orders={
            "inputs": CONTRACT_FIELD_KEY_ORDER,
            "outputs": CONTRACT_FIELD_KEY_ORDER,
            "parameters": PARAMETER_KEY_ORDER,
            "nodes": NODE_KEY_ORDER,
            "edges": EDGE_KEY_ORDER,
            "quality_gates": QUALITY_GATE_KEY_ORDER,
            "parameters": PARAMETER_KEY_ORDER,
            "inputs_schema": NODE_FIELD_KEY_ORDER,
            "outputs_schema": NODE_FIELD_KEY_ORDER,
        },
    )


def order_mapping(
    value: Any,
    key_order: list[str] | None = None,
    *,
    child_orders: dict[str, list[str]] | None = None,
    list_child_orders: dict[str, list[str]] | None = None,
) -> Any:
    if isinstance(value, list):
        return [order_mapping(item) for item in value]
    if not isinstance(value, dict):
        return value

    child_orders = child_orders or {}
    list_child_orders = list_child_orders or {}
    ordered: dict[str, Any] = {}
    keys = list(value)
    if key_order:
        keys = [key for key in key_order if key in value] + sorted(key for key in value if key not in key_order)
    else:
        keys = sorted(keys)

    for key in keys:
        item = value[key]
        if key in child_orders and isinstance(item, dict):
            ordered[key] = order_mapping(
                item,
                child_orders[key],
                child_orders=child_orders,
                list_child_orders=list_child_orders,
            )
        elif key in list_child_orders and isinstance(item, list):
            ordered[key] = [
                order_mapping(
                    element,
                    list_child_orders[key],
                    child_orders=child_orders,
                    list_child_orders=list_child_orders,
                )
                if isinstance(element, dict)
                else order_mapping(element, child_orders=child_orders, list_child_orders=list_child_orders)
                for element in item
            ]
        elif isinstance(item, dict):
            ordered[key] = order_mapping(item, child_orders=child_orders, list_child_orders=list_child_orders)
        elif isinstance(item, list):
            ordered[key] = [
                order_mapping(element, child_orders=child_orders, list_child_orders=list_child_orders)
                for element in item
            ]
        else:
            ordered[key] = item

    return ordered


def dump_yaml(document: dict[str, Any]) -> str:
    dumped = yaml.dump(
        document,
        Dumper=IndentedSafeDumper,
        sort_keys=False,
        allow_unicode=False,
        width=120,
    )
    return dumped if dumped.endswith("\n") else dumped + "\n"


def validate_event_document(document: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = [
        f"{format_error_path(error.path)}: {error.message}"
        for error in sorted(validator.iter_errors(document), key=lambda err: list(err.path))
    ]
    timestamp = document.get("timestamp")
    if isinstance(timestamp, str) and not is_rfc3339_datetime(timestamp):
        errors.append("$.timestamp: expected RFC 3339 date-time")
    return errors


def validate_run_document(
    document: dict[str, Any],
    run_schema: dict[str, Any],
    event_schema: dict[str, Any],
    flow_schema: dict[str, Any],
    *,
    run_path: Path | None = None,
    _depth: int = 0,
) -> list[str]:
    validator = Draft202012Validator(run_schema, format_checker=FormatChecker())
    errors = [
        f"{format_error_path(error.path)}: {error.message}"
        for error in sorted(validator.iter_errors(document), key=lambda err: list(err.path))
    ]

    run_info = document.get("run", {})
    flow_info = document.get("flow", {})
    if not isinstance(run_info, dict) or not isinstance(flow_info, dict):
        return errors

    if run_info.get("status") == "completed" and "completed_at" not in run_info:
        errors.append("$.run.completed_at: completed runs require completed_at")
    for field in ("started_at", "completed_at"):
        value = run_info.get(field)
        if isinstance(value, str) and not is_rfc3339_datetime(value):
            errors.append(f"$.run.{field}: expected RFC 3339 date-time")
    if isinstance(run_info.get("started_at"), str) and isinstance(run_info.get("completed_at"), str):
        started = parse_rfc3339(run_info["started_at"])
        completed = parse_rfc3339(run_info["completed_at"])
        if started and completed and completed < started:
            errors.append("$.run.completed_at: must be greater than or equal to started_at")

    flow_document: dict[str, Any] | None = None
    flow_source = flow_info.get("source")
    if isinstance(flow_source, str):
        flow_path = resolve_flow_source(flow_source, run_path)
        if not flow_path.exists():
            errors.append(f"$.flow.source: flow file does not exist: {flow_source}")
        else:
            try:
                flow_document = load_yaml(flow_path)
                for error in validate_flow_document(flow_document, flow_schema):
                    errors.append(f"$.flow.source({flow_source}): {error}")
            except Exception as exc:  # noqa: BLE001 - CLI should report run context
                errors.append(f"$.flow.source: {exc}")

    if flow_document:
        if flow_info.get("id") != flow_document.get("id"):
            errors.append("$.flow.id: does not match source flow id")
        if flow_info.get("version") != flow_document.get("version"):
            errors.append("$.flow.version: does not match source flow version")
        supported_cores = flow_document.get("runtime", {}).get("supported_cores", [])
        if run_info.get("core") not in supported_cores:
            errors.append("$.run.core: is not listed in source flow runtime.supported_cores")

    events = document.get("events", [])
    if isinstance(events, list):
        errors.extend(
            validate_run_events(
                events,
                event_schema,
                flow_document=flow_document,
                flow_id=flow_info.get("id"),
                flow_version=flow_info.get("version"),
                run_id=run_info.get("id"),
                core=run_info.get("core"),
                status=run_info.get("status"),
            )
        )

    if flow_document and run_info.get("status") == "completed":
        required_outputs = [
            field["id"]
            for field in flow_document.get("contracts", {}).get("outputs", [])
            if isinstance(field, dict) and field.get("required") is True
        ]
        outputs = document.get("outputs", {})
        if not isinstance(outputs, dict):
            errors.append("$.outputs: completed runs require an outputs object")
        else:
            for output_id in required_outputs:
                if output_id not in outputs:
                    errors.append(f"$.outputs.{output_id}: required output is missing")

    errors.extend(
        validate_sub_runs(
            document,
            flow_document,
            run_schema,
            event_schema,
            flow_schema,
            run_path=run_path,
            _depth=_depth,
        )
    )

    return errors


def validate_sub_runs(
    document: dict[str, Any],
    flow_document: dict[str, Any] | None,
    run_schema: dict[str, Any],
    event_schema: dict[str, Any],
    flow_schema: dict[str, Any],
    *,
    run_path: Path | None = None,
    _depth: int = 0,
) -> list[str]:
    """Runtime arm of sub-flow composition: recursively validate each flow_ref child bundle.

    A parent run that declares (via its source flow) a ``flow_ref`` node must carry a matching
    ``sub_runs`` entry whose child bundle recursively validates, is ``completed`` (when the parent
    is), and has a ``subflow.completed`` event. A passed ``subflows-passed`` gate is therefore
    backed by honest, recursively-checked child evidence rather than a parent self-assertion.
    """
    errors: list[str] = []
    if not flow_document:
        return errors

    flow_refs = {
        node["id"]: node
        for node in composition.flow_ref_nodes(flow_document)
        if isinstance(node.get("id"), str)
    }
    if not flow_refs:
        return errors

    if _depth > 16:
        return ["$.sub_runs: composition nesting too deep (possible cycle)"]

    sub_runs = document.get("sub_runs", [])
    if not isinstance(sub_runs, list):
        sub_runs = []
    sub_by_node: dict[str, dict[str, Any]] = {}
    seen_node_ids: set[str] = set()
    for index, sub in enumerate(sub_runs):
        if not isinstance(sub, dict):
            continue
        node_id = sub.get("node_id")
        if isinstance(node_id, str):
            if node_id in seen_node_ids:
                errors.append(
                    f"$.sub_runs[{index}].node_id: duplicate sub_run for flow_ref node '{node_id}' "
                    "(each flow_ref node maps to exactly one sub_run)"
                )
            seen_node_ids.add(node_id)
            sub_by_node[node_id] = sub
        if node_id not in flow_refs:
            errors.append(f"$.sub_runs[{index}].node_id: '{node_id}' is not a flow_ref node in the source flow")

    status = document.get("run", {}).get("status") if isinstance(document.get("run"), dict) else None
    completed_subflow_nodes: set[str] = set()
    for event in document.get("events", []):
        if isinstance(event, dict) and event.get("event") == "subflow.completed":
            payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
            node_id = payload.get("node_id") or event.get("node_id")
            if node_id:
                completed_subflow_nodes.add(node_id)

    for node_id, node in flow_refs.items():
        ref = node.get("ref") or {}
        sub = sub_by_node.get(node_id)
        if sub is None:
            if status == "completed":
                errors.append(f"$.sub_runs: completed run has no sub_run for flow_ref node '{node_id}'")
            continue

        child_flow = sub.get("flow", {}) if isinstance(sub.get("flow"), dict) else {}
        if child_flow.get("id") != ref.get("flow_id"):
            errors.append(
                f"$.sub_runs[{node_id}].flow.id: '{child_flow.get('id')}' does not match node ref.flow_id "
                f"'{ref.get('flow_id')}'"
            )
        constraint = composition.parse_constraint(ref.get("version_constraint"))
        if constraint is None:
            errors.append(f"$.sub_runs[{node_id}]: source flow_ref has an unparseable version_constraint")
        elif not composition.version_satisfies(child_flow.get("version"), constraint):
            errors.append(
                f"$.sub_runs[{node_id}].flow.version: '{child_flow.get('version')}' does not satisfy "
                f"'{ref.get('version_constraint')}'"
            )

        uri = sub.get("uri")
        if isinstance(uri, str):
            child_path = resolve_adapter_artifact_source(uri, run_path)
            if not child_path.exists():
                errors.append(f"$.sub_runs[{node_id}].uri: child run bundle does not exist: {uri}")
            else:
                try:
                    child_document = load_json(child_path)
                    child_errors = validate_run_document(
                        child_document,
                        run_schema,
                        event_schema,
                        flow_schema,
                        run_path=child_path,
                        _depth=_depth + 1,
                    )
                    for error in child_errors:
                        errors.append(f"$.sub_runs[{node_id}].uri({uri}): {error}")
                    child_status = child_document.get("run", {}).get("status")
                    if status == "completed" and child_status != "completed":
                        errors.append(
                            f"$.sub_runs[{node_id}]: parent run is completed but child run status is '{child_status}'"
                        )
                except Exception as exc:  # noqa: BLE001 - CLI should report run context
                    errors.append(f"$.sub_runs[{node_id}].uri: {exc}")

        if status == "completed" and node_id not in completed_subflow_nodes:
            errors.append(
                f"$.events: completed run requires a subflow.completed event for flow_ref node '{node_id}'"
            )

    return errors


def validate_event_stream_document(
    document: dict[str, Any],
    stream_schema: dict[str, Any],
    event_schema: dict[str, Any],
    flow_schema: dict[str, Any],
    *,
    stream_path: Path | None = None,
) -> list[str]:
    validator = Draft202012Validator(stream_schema, format_checker=FormatChecker())
    errors = [
        f"{format_error_path(error.path)}: {error.message}"
        for error in sorted(validator.iter_errors(document), key=lambda err: list(err.path))
    ]

    run_info = document.get("run", {})
    flow_info = document.get("flow", {})
    if not isinstance(run_info, dict) or not isinstance(flow_info, dict):
        return errors

    if run_info.get("status") == "completed" and "completed_at" not in run_info:
        errors.append("$.run.completed_at: completed event streams require completed_at")
    for field in ("started_at", "completed_at"):
        value = run_info.get(field)
        if isinstance(value, str) and not is_rfc3339_datetime(value):
            errors.append(f"$.run.{field}: expected RFC 3339 date-time")
    if isinstance(run_info.get("started_at"), str) and isinstance(run_info.get("completed_at"), str):
        started = parse_rfc3339(run_info["started_at"])
        completed = parse_rfc3339(run_info["completed_at"])
        if started and completed and completed < started:
            errors.append("$.run.completed_at: must be greater than or equal to started_at")

    flow_document: dict[str, Any] | None = None
    flow_source = flow_info.get("source")
    if isinstance(flow_source, str):
        flow_path = resolve_flow_source(flow_source, stream_path)
        if not flow_path.exists():
            errors.append(f"$.flow.source: flow file does not exist: {flow_source}")
        else:
            try:
                flow_document = load_yaml(flow_path)
                for error in validate_flow_document(flow_document, flow_schema):
                    errors.append(f"$.flow.source({flow_source}): {error}")
            except Exception as exc:  # noqa: BLE001 - CLI should report stream context
                errors.append(f"$.flow.source: {exc}")

    if flow_document:
        if flow_info.get("id") != flow_document.get("id"):
            errors.append("$.flow.id: does not match source flow id")
        if flow_info.get("version") != flow_document.get("version"):
            errors.append("$.flow.version: does not match source flow version")
        supported_cores = flow_document.get("runtime", {}).get("supported_cores", [])
        if run_info.get("core") not in supported_cores:
            errors.append("$.run.core: is not listed in source flow runtime.supported_cores")

    events = load_event_stream_events(document.get("events", []), stream_path, errors)
    if events:
        errors.extend(
            validate_run_events(
                events,
                event_schema,
                flow_document=flow_document,
                flow_id=flow_info.get("id"),
                flow_version=flow_info.get("version"),
                run_id=run_info.get("id"),
                core=run_info.get("core"),
                status=run_info.get("status"),
            )
        )

    if flow_document and run_info.get("status") == "completed":
        required_outputs = [
            field["id"]
            for field in flow_document.get("contracts", {}).get("outputs", [])
            if isinstance(field, dict) and field.get("required") is True
        ]
        outputs = document.get("outputs", {})
        if not isinstance(outputs, dict):
            errors.append("$.outputs: completed event streams require an outputs object")
        else:
            for output_id in required_outputs:
                if output_id not in outputs:
                    errors.append(f"$.outputs.{output_id}: required output is missing")

    return errors


def validate_adapter_smoke_document(
    document: dict[str, Any],
    adapter_schema: dict[str, Any],
    flow_schema: dict[str, Any],
    run_schema: dict[str, Any],
    event_schema: dict[str, Any],
    stream_schema: dict[str, Any],
    *,
    adapter_path: Path | None = None,
) -> list[str]:
    validator = Draft202012Validator(adapter_schema, format_checker=FormatChecker())
    errors = [
        f"{format_error_path(error.path)}: {error.message}"
        for error in sorted(validator.iter_errors(document), key=lambda err: list(err.path))
    ]

    flow_info = document.get("flow", {})
    if not isinstance(flow_info, dict):
        return errors

    flow_document: dict[str, Any] | None = None
    flow_source = flow_info.get("source")
    if isinstance(flow_source, str):
        flow_path = resolve_flow_source(flow_source, adapter_path)
        if not flow_path.exists():
            errors.append(f"$.flow.source: flow file does not exist: {flow_source}")
        else:
            try:
                flow_document = load_yaml(flow_path)
                for error in validate_flow_document(flow_document, flow_schema):
                    errors.append(f"$.flow.source({flow_source}): {error}")
            except Exception as exc:  # noqa: BLE001 - CLI should report adapter context
                errors.append(f"$.flow.source: {exc}")

    if not flow_document:
        return errors

    consumer = document.get("consumer")
    if flow_info.get("id") != flow_document.get("id"):
        errors.append("$.flow.id: does not match source flow id")
    if flow_info.get("version") != flow_document.get("version"):
        errors.append("$.flow.version: does not match source flow version")

    supported_cores = flow_document.get("runtime", {}).get("supported_cores", [])
    if consumer not in supported_cores:
        errors.append("$.consumer: is not listed in source flow runtime.supported_cores")

    required_capabilities = set(flow_document.get("runtime", {}).get("required_capabilities", []))
    supported_capabilities = {
        capability for capability in document.get("capability_support", []) if isinstance(capability, str)
    }
    missing_capabilities = sorted(required_capabilities - supported_capabilities)
    for capability in missing_capabilities:
        errors.append(f"$.capability_support: missing required capability '{capability}'")

    mappings = document.get("node_type_mappings", {})
    if isinstance(mappings, dict):
        node_types = {
            node["type"]
            for node in flow_document.get("nodes", [])
            if isinstance(node, dict) and isinstance(node.get("type"), str)
        }
        missing_node_types = sorted(node_type for node_type in node_types if node_type not in mappings)
        for node_type in missing_node_types:
            errors.append(f"$.node_type_mappings: missing mapping for node type '{node_type}'")

    run_bundle = document.get("run_bundle")
    if isinstance(run_bundle, str):
        run_path = resolve_adapter_artifact_source(run_bundle, adapter_path)
        if not run_path.exists():
            errors.append(f"$.run_bundle: file does not exist: {run_bundle}")
        else:
            try:
                run_document = load_json(run_path)
                run_errors = validate_run_document(run_document, run_schema, event_schema, flow_schema, run_path=run_path)
                for error in run_errors:
                    errors.append(f"$.run_bundle({run_bundle}): {error}")
                run_core = run_document.get("run", {}).get("core") if isinstance(run_document.get("run"), dict) else None
                if consumer and run_core != consumer:
                    errors.append("$.run_bundle.run.core: does not match adapter consumer")
            except Exception as exc:  # noqa: BLE001 - CLI should report adapter context
                errors.append(f"$.run_bundle: {exc}")

    event_stream = document.get("event_stream")
    if isinstance(event_stream, str):
        stream_path = resolve_adapter_artifact_source(event_stream, adapter_path)
        if not stream_path.exists():
            errors.append(f"$.event_stream: file does not exist: {event_stream}")
        else:
            try:
                stream_document = load_json(stream_path)
                stream_errors = validate_event_stream_document(
                    stream_document,
                    stream_schema,
                    event_schema,
                    flow_schema,
                    stream_path=stream_path,
                )
                for error in stream_errors:
                    errors.append(f"$.event_stream({event_stream}): {error}")
            except Exception as exc:  # noqa: BLE001 - CLI should report adapter context
                errors.append(f"$.event_stream: {exc}")

    negative_run_bundle = document.get("negative_run_bundle")
    if isinstance(negative_run_bundle, dict):
        source = negative_run_bundle.get("source")
        expected_error = negative_run_bundle.get("expected_error")
        if isinstance(source, str) and isinstance(expected_error, str):
            negative_path = resolve_adapter_artifact_source(source, adapter_path)
            if not negative_path.exists():
                errors.append(f"$.negative_run_bundle.source: file does not exist: {source}")
            else:
                try:
                    negative_document = load_json(negative_path)
                    negative_errors = validate_run_document(
                        negative_document,
                        run_schema,
                        event_schema,
                        flow_schema,
                        run_path=negative_path,
                    )
                    if not negative_errors:
                        errors.append("$.negative_run_bundle: expected fixture to fail validation")
                    elif not any(expected_error in error for error in negative_errors):
                        errors.append(f"$.negative_run_bundle.expected_error: did not match validation errors for {source}")
                except Exception as exc:  # noqa: BLE001 - CLI should report adapter context
                    errors.append(f"$.negative_run_bundle.source: {exc}")

    return errors


def load_event_stream_events(event_sources: Any, stream_path: Path | None, errors: list[str]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    if not isinstance(event_sources, list):
        return events

    for index, event_source in enumerate(event_sources):
        if not isinstance(event_source, str):
            continue
        event_path = resolve_stream_event_source(event_source, stream_path)
        if not event_path.exists():
            errors.append(f"$.events[{index}]: event file does not exist: {event_source}")
            continue
        try:
            events.append(load_json(event_path))
        except Exception as exc:  # noqa: BLE001 - CLI should report stream context
            errors.append(f"$.events[{index}]({event_source}): {exc}")
    return events


def validate_sample_document(
    document: dict[str, Any],
    sample_schema: dict[str, Any],
    flow_schema: dict[str, Any],
    *,
    sample_path: Path | None = None,
) -> list[str]:
    validator = Draft202012Validator(sample_schema, format_checker=FormatChecker())
    errors = [
        f"{format_error_path(error.path)}: {error.message}"
        for error in sorted(validator.iter_errors(document), key=lambda err: list(err.path))
    ]

    flow_info = document.get("flow", {})
    if not isinstance(flow_info, dict):
        return errors

    flow_document: dict[str, Any] | None = None
    flow_source = flow_info.get("source")
    if isinstance(flow_source, str):
        flow_path = resolve_flow_source(flow_source, sample_path)
        if not flow_path.exists():
            errors.append(f"$.flow.source: flow file does not exist: {flow_source}")
        else:
            try:
                flow_document = load_yaml(flow_path)
                for error in validate_flow_document(flow_document, flow_schema):
                    errors.append(f"$.flow.source({flow_source}): {error}")
            except Exception as exc:  # noqa: BLE001 - CLI should report sample context
                errors.append(f"$.flow.source: {exc}")

    if not flow_document:
        return errors

    if flow_info.get("id") != flow_document.get("id"):
        errors.append("$.flow.id: does not match source flow id")
    if flow_info.get("version") != flow_document.get("version"):
        errors.append("$.flow.version: does not match source flow version")

    inputs = document.get("inputs", {})
    expected_outputs = document.get("expected_outputs", {})
    if isinstance(inputs, dict):
        errors.extend(validate_contract_values(inputs, flow_document.get("contracts", {}).get("inputs", []), "$.inputs"))
    if isinstance(expected_outputs, dict):
        errors.extend(
            validate_contract_values(
                expected_outputs,
                flow_document.get("contracts", {}).get("outputs", []),
                "$.expected_outputs",
            )
        )

    return errors


def validate_contract_values(values: dict[str, Any], contract_fields: list[Any], path: str) -> list[str]:
    errors: list[str] = []
    fields = {field["id"]: field for field in contract_fields if isinstance(field, dict) and isinstance(field.get("id"), str)}
    required = {field_id for field_id, field in fields.items() if field.get("required") is True}

    for field_id in sorted(required - set(values)):
        errors.append(f"{path}.{field_id}: required contract field is missing")
    for field_id in sorted(set(values) - set(fields)):
        errors.append(f"{path}.{field_id}: is not declared by the source flow contract")
    for field_id, value in values.items():
        field = fields.get(field_id)
        if not field:
            continue
        type_error = validate_contract_value_type(value, field.get("type"))
        if type_error:
            errors.append(f"{path}.{field_id}: {type_error}")

    return errors


def validate_contract_value_type(value: Any, expected_type: Any) -> str | None:
    if expected_type in {"text", "markdown", "patch", "command", "uri"}:
        if not isinstance(value, str):
            return f"expected {expected_type} string"
        if expected_type == "uri" and not ("://" in value or value.startswith("file:") or value.startswith("artifact:")):
            return "expected URI-like string"
        return None
    if expected_type == "json":
        if isinstance(value, (dict, list, str, int, float, bool)) or value is None:
            return None
        return "expected JSON-compatible value"
    if expected_type == "boolean":
        return None if isinstance(value, bool) else "expected boolean"
    if expected_type == "number":
        return None if isinstance(value, (int, float)) and not isinstance(value, bool) else "expected number"
    return None


def validate_run_events(
    events: list[Any],
    event_schema: dict[str, Any],
    *,
    flow_document: dict[str, Any] | None,
    flow_id: Any,
    flow_version: Any,
    run_id: Any,
    core: Any,
    status: Any,
) -> list[str]:
    errors: list[str] = []
    observed_events: set[str] = set()
    passed_gate_ids: set[str] = set()
    known_node_ids = {node["id"] for node in flow_document.get("nodes", [])} if flow_document else set()
    known_event_names = set(flow_document.get("observability", {}).get("events", [])) if flow_document else set()
    source_gates = flow_document.get("quality_gates", []) if flow_document else []
    gate_evidence_refs = {
        gate["id"]: set(gate.get("evidence_refs", []))
        for gate in source_gates
        if isinstance(gate, dict)
        and isinstance(gate.get("id"), str)
        and isinstance(gate.get("evidence_refs"), list)
    }
    gate_evidence_class = {
        gate["id"]: (gate.get("evidence_class"), gate.get("evidence_class_min"))
        for gate in source_gates
        if isinstance(gate, dict) and isinstance(gate.get("id"), str)
    }
    gate_types = {
        gate["id"]: gate.get("type")
        for gate in source_gates
        if isinstance(gate, dict) and isinstance(gate.get("id"), str)
    }
    producing_agents = {
        node["agent"]
        for node in (flow_document.get("nodes", []) if flow_document else [])
        if isinstance(node, dict) and isinstance(node.get("agent"), str)
    }

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            errors.append(f"$.events[{index}]: expected event object")
            continue

        for error in validate_event_document(event, event_schema):
            errors.append(prefix_error_path(error, f"$.events[{index}]"))

        observed_events.add(str(event.get("event")))

        if event.get("flow_id") != flow_id:
            errors.append(f"$.events[{index}].flow_id: does not match run flow id")
        if event.get("flow_version") != flow_version:
            errors.append(f"$.events[{index}].flow_version: does not match run flow version")
        if event.get("run_id") != run_id:
            errors.append(f"$.events[{index}].run_id: does not match run id")
        if event.get("core") != core:
            errors.append(f"$.events[{index}].core: does not match run core")

        node_id = event.get("node_id")
        if isinstance(node_id, str) and known_node_ids and node_id not in known_node_ids:
            errors.append(f"$.events[{index}].node_id: references missing source flow node '{node_id}'")

        event_name = event.get("event")
        if isinstance(event_name, str) and known_event_names and event_name not in known_event_names:
            errors.append(f"$.events[{index}].event: is not declared in source flow observability.events")

        payload = event.get("payload", {})
        if event_name == "gate.completed" and isinstance(payload, dict):
            gate_id = payload.get("gate_id")
            gate_status = payload.get("status")
            if isinstance(gate_id, str) and gate_status == "passed":
                passed_gate_ids.add(gate_id)
                evidence = event.get("evidence")
                if not evidence:
                    errors.append(f"$.events[{index}].evidence: passed required gates need evidence")
                else:
                    if gate_evidence_refs.get(gate_id):
                        observed_evidence_refs = collect_event_evidence_refs(evidence)
                        expected_refs = gate_evidence_refs[gate_id]
                        if observed_evidence_refs.isdisjoint(expected_refs):
                            expected = ", ".join(sorted(expected_refs))
                            errors.append(
                                f"$.events[{index}].evidence: passed gate '{gate_id}' needs evidence id or kind matching one of: {expected}"
                            )
                    exact_class, floor_class = gate_evidence_class.get(gate_id, (None, None))
                    if exact_class or floor_class:
                        observed_classes = collect_event_evidence_classes(evidence)
                        if not evidence_class_satisfies(observed_classes, exact_class, floor_class):
                            requirement = exact_class if exact_class else f">= {floor_class}"
                            got = ", ".join(sorted(observed_classes)) or "none"
                            errors.append(
                                f"$.events[{index}].evidence: passed gate '{gate_id}' requires evidence_class "
                                f"{requirement}; got {got}"
                            )
                if gate_types.get(gate_id) in {"judgment", "acceptance"}:
                    reviewer_id = payload.get("reviewer_id")
                    if not isinstance(reviewer_id, str) or not reviewer_id:
                        errors.append(
                            f"$.events[{index}].payload.reviewer_id: {gate_types[gate_id]} gate '{gate_id}' "
                            "requires a reviewer_id"
                        )
                    elif reviewer_id in producing_agents:
                        errors.append(
                            f"$.events[{index}].payload.reviewer_id: reviewer '{reviewer_id}' for gate '{gate_id}' "
                            "must not be a producing agent (no self-review)"
                        )

    if core == "standalone":
        for index, event in enumerate(events):
            if not isinstance(event, dict):
                continue
            for forbidden in collect_event_evidence_classes(event.get("evidence")) & STANDALONE_FORBIDDEN_EVIDENCE_CLASSES:
                errors.append(
                    f"$.events[{index}].evidence: standalone runs may not emit '{forbidden}' evidence; "
                    "that evidence class requires a runtime that provisioned the environment"
                )

    errors.extend(validate_environment_provenance(events, flow_document, producing_agents))

    if status == "completed" and "flow.completed" not in observed_events:
        errors.append("$.events: completed runs require a flow.completed event")

    if flow_document and status == "completed":
        required_gate_ids = [
            gate["id"]
            for gate in flow_document.get("quality_gates", [])
            if isinstance(gate, dict) and gate.get("required") is True
        ]
        for gate_id in required_gate_ids:
            if gate_id not in passed_gate_ids:
                errors.append(f"$.events: required quality gate '{gate_id}' is missing passed gate.completed evidence")

    return errors


def collect_event_evidence_refs(evidence: Any) -> set[str]:
    if not isinstance(evidence, list):
        return set()

    refs: set[str] = set()
    for item in evidence:
        if not isinstance(item, dict):
            continue
        evidence_id = item.get("id")
        if isinstance(evidence_id, str):
            refs.add(evidence_id)
            continue
        kind = item.get("kind")
        if isinstance(kind, str):
            refs.add(kind)
    return refs


def collect_event_evidence_classes(evidence: Any) -> set[str]:
    if not isinstance(evidence, list):
        return set()
    classes: set[str] = set()
    for item in evidence:
        if isinstance(item, dict) and isinstance(item.get("evidence_class"), str):
            classes.add(item["evidence_class"])
    return classes


def evidence_class_satisfies(observed: set[str], exact: Any, floor: Any) -> bool:
    """Whether observed evidence classes meet a gate's declared class requirement."""
    if exact and exact in observed:
        return True
    if floor and floor in EVIDENCE_CLASS_ORDER:
        floor_rank = EVIDENCE_CLASS_ORDER[floor]
        if any(EVIDENCE_CLASS_ORDER.get(value, -1) >= floor_rank for value in observed):
            return True
    return False


def validate_environment_provenance(
    events: list[Any],
    flow_document: dict[str, Any] | None,
    producing_agents: set[str],
) -> list[str]:
    """Provenance backbone for `sandbox-run` evidence (reframe guardrail G1).

    `sandbox-run` evidence is only honest if a runtime — not the authoring agent — actually
    provisioned the environment. So an `env.provisioned` event must be runtime-issued (its
    `provisioner` is not one of the flow's producing agents), an environment whose
    `teardown_required` is set must record an `env.torn_down`, and any `sandbox-run` evidence
    must be backed by an `env.provisioned` event.
    """
    errors: list[str] = []
    env_nodes = {
        node["id"]: (node.get("environment") or {})
        for node in (flow_document.get("nodes", []) if flow_document else [])
        if isinstance(node, dict) and isinstance(node.get("id"), str) and isinstance(node.get("environment"), dict)
    }

    torn_down_node_ids: set[str] = set()
    provisioned_events: list[tuple[int, dict[str, Any]]] = []
    sandbox_present = False
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            continue
        if "sandbox-run" in collect_event_evidence_classes(event.get("evidence")):
            sandbox_present = True
        payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
        node_id = payload.get("node_id") or event.get("node_id")
        if event.get("event") == "env.torn_down" and node_id:
            torn_down_node_ids.add(node_id)
        if event.get("event") == "env.provisioned":
            provisioned_events.append((index, event))

    for index, event in provisioned_events:
        payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
        provisioner = payload.get("provisioner")
        node_id = payload.get("node_id") or event.get("node_id")
        if not isinstance(provisioner, str) or not provisioner:
            errors.append(f"$.events[{index}].payload.provisioner: env.provisioned requires a provisioner id")
        elif provisioner in producing_agents:
            errors.append(
                f"$.events[{index}].payload.provisioner: provisioner '{provisioner}' must be a runtime, "
                "not a producing agent (provenance must be non-self-issued)"
            )
        if env_nodes.get(node_id, {}).get("teardown_required", True) and node_id and node_id not in torn_down_node_ids:
            errors.append(
                f"$.events[{index}]: env.provisioned for node '{node_id}' requires a matching env.torn_down event"
            )

    if sandbox_present and not provisioned_events:
        errors.append(
            "$.events: sandbox-run evidence requires an env.provisioned provenance event "
            "(flowctl checks consistency; the runtime attests authenticity)"
        )

    return errors


def prefix_error_path(error: str, prefix: str) -> str:
    if error.startswith("$"):
        return prefix + error[1:]
    return f"{prefix}: {error}"


def resolve_flow_source(source: str, run_path: Path | None) -> Path:
    source_path = Path(source)
    if source_path.is_absolute():
        return source_path
    repo_relative = REPO_ROOT / source_path
    if repo_relative.exists() or run_path is None:
        return repo_relative
    return run_path.parent / source_path


def resolve_stream_event_source(source: str, stream_path: Path | None) -> Path:
    source_path = Path(source)
    if source_path.is_absolute():
        return source_path
    repo_relative = REPO_ROOT / source_path
    if repo_relative.exists() or stream_path is None:
        return repo_relative
    return stream_path.parent / source_path


def resolve_adapter_artifact_source(source: str, adapter_path: Path | None) -> Path:
    source_path = Path(source)
    if source_path.is_absolute():
        return source_path
    repo_relative = REPO_ROOT / source_path
    if repo_relative.exists() or adapter_path is None:
        return repo_relative
    return adapter_path.parent / source_path


def parse_rfc3339(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def is_rfc3339_datetime(value: str) -> bool:
    return parse_rfc3339(value) is not None


def validate_semantics(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if "deprecated_by" in document and "migration" not in document:
        errors.append("$.migration: deprecated flows require migration guidance")
    if "migration" in document and "deprecated_by" not in document:
        errors.append("$.deprecated_by: migration guidance requires deprecated_by")

    nodes = document.get("nodes", [])
    if not isinstance(nodes, list):
        return errors

    node_ids: list[str] = []
    produced_by_node: dict[str, set[str]] = {}
    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            continue
        node_id = node.get("id")
        if isinstance(node_id, str):
            node_ids.append(node_id)
            produced_by_node[node_id] = {
                item for item in node.get("produces", []) if isinstance(item, str)
            }
        else:
            errors.append(f"$.nodes[{index}].id: expected string id")

    duplicate_ids = sorted({node_id for node_id in node_ids if node_ids.count(node_id) > 1})
    for node_id in duplicate_ids:
        errors.append(f"$.nodes: duplicate node id '{node_id}'")

    node_id_set = set(node_ids)
    entrypoint = document.get("entrypoint")
    if isinstance(entrypoint, str) and entrypoint not in node_id_set:
        errors.append(f"$.entrypoint: references missing node '{entrypoint}'")

    adjacency: dict[str, list[str]] = {node_id: [] for node_id in node_id_set}
    for index, edge in enumerate(document.get("edges", [])):
        if not isinstance(edge, dict):
            continue
        start = edge.get("from")
        end = edge.get("to")
        if isinstance(start, str) and start not in node_id_set:
            errors.append(f"$.edges[{index}].from: references missing node '{start}'")
        if isinstance(end, str) and end not in node_id_set:
            errors.append(f"$.edges[{index}].to: references missing node '{end}'")
        if isinstance(start, str) and isinstance(end, str) and start in node_id_set and end in node_id_set:
            adjacency[start].append(end)

    if isinstance(entrypoint, str) and entrypoint in node_id_set:
        reachable = collect_reachable(entrypoint, adjacency)
        unreachable = sorted(node_id_set - reachable)
        for node_id in unreachable:
            errors.append(f"$.nodes: node '{node_id}' is not reachable from entrypoint '{entrypoint}'")
        errors.extend(validate_requirements_and_outputs(document, nodes, adjacency, entrypoint, produced_by_node, reachable))

    gates = document.get("quality_gates", [])
    if isinstance(gates, list):
        required_gate_count = sum(1 for gate in gates if isinstance(gate, dict) and gate.get("required") is True)
        if required_gate_count == 0:
            errors.append("$.quality_gates: at least one gate must be required")
        for index, gate in enumerate(gates):
            if not isinstance(gate, dict):
                continue
            if gate.get("type") == "command" and not gate.get("command"):
                errors.append(f"$.quality_gates[{index}].command: command gates require a command")
            errors.extend(validate_quality_gate_evidence_refs(document, gate, index))

    errors.extend(validate_parameter_references(document))
    errors.extend(validate_node_extensions(document))

    return errors


def validate_node_extensions(document: dict[str, Any]) -> list[str]:
    """Bounds checks for the v1.1 `iteration` and `fan_out` node primitives.

    Loops must terminate (a mandatory `max_iterations`) and reference a real gate;
    fan-out must declare what it ranges over, a bounded cardinality, and an aggregation
    rule. This extends the existing "execution steps are bounded" guarantee to loops and
    fan-out instead of letting them escape it.
    """
    errors: list[str] = []
    gate_ids = {
        gate["id"]
        for gate in document.get("quality_gates", [])
        if isinstance(gate, dict) and isinstance(gate.get("id"), str)
    }
    for index, node in enumerate(document.get("nodes", [])):
        if not isinstance(node, dict):
            continue

        iteration = node.get("iteration")
        if isinstance(iteration, dict):
            if not isinstance(iteration.get("max_iterations"), int):
                errors.append(
                    f"$.nodes[{index}].iteration.max_iterations: bounded loops require an integer max_iterations"
                )
            until = iteration.get("until")
            if isinstance(until, str) and until.startswith("gate:"):
                gate_id = until.split(":", 1)[1]
                if gate_id not in gate_ids:
                    errors.append(f"$.nodes[{index}].iteration.until: references unknown gate '{gate_id}'")

        fan_out = node.get("fan_out")
        if isinstance(fan_out, dict):
            if not isinstance(fan_out.get("over"), str) or not fan_out.get("over"):
                errors.append(f"$.nodes[{index}].fan_out.over: fan-out requires a non-empty 'over' source")
            cardinality = fan_out.get("cardinality")
            if not isinstance(cardinality, dict) or not isinstance(cardinality.get("min"), int):
                errors.append(
                    f"$.nodes[{index}].fan_out.cardinality: fan-out requires a cardinality with an integer min"
                )
            if not isinstance(fan_out.get("aggregate"), str):
                errors.append(f"$.nodes[{index}].fan_out.aggregate: fan-out requires an aggregate rule")

        environment = node.get("environment")
        if isinstance(environment, dict):
            provides = environment.get("provides")
            if not isinstance(provides, list) or not provides:
                errors.append(
                    f"$.nodes[{index}].environment.provides: a declared environment must provide at least one capability"
                )

    return errors


def validate_parameter_references(document: dict[str, Any]) -> list[str]:
    """Check `parameters` declarations and that every `{{param.x}}` reference resolves.

    This is what lets a flow be reusable across stacks via one parameterized contract
    (the build/test commands resolve from a declared parameter) instead of a separate
    per-stack flow.
    """
    errors: list[str] = []
    parameters = document.get("parameters", [])
    if not isinstance(parameters, list):
        parameters = []
    declared = {param["id"] for param in parameters if isinstance(param, dict) and isinstance(param.get("id"), str)}

    for index, param in enumerate(parameters):
        if isinstance(param, dict) and param.get("type") == "enum":
            choices = param.get("choices")
            if not isinstance(choices, list) or not choices:
                errors.append(f"$.parameters[{index}].choices: enum parameters require a non-empty choices list")

    references: list[tuple[str, str]] = []
    for index, gate in enumerate(document.get("quality_gates", [])):
        if isinstance(gate, dict) and isinstance(gate.get("command"), str):
            references.append((f"$.quality_gates[{index}].command", gate["command"]))
    for index, node in enumerate(document.get("nodes", [])):
        if not isinstance(node, dict):
            continue
        if isinstance(node.get("tool"), str):
            references.append((f"$.nodes[{index}].tool", node["tool"]))
        bindings = node.get("with")
        if isinstance(bindings, dict):
            for key, value in bindings.items():
                if isinstance(value, str):
                    references.append((f"$.nodes[{index}].with.{key}", value))

    for location, text in references:
        for match in PARAM_REFERENCE_PATTERN.finditer(text):
            param_id = match.group(1)
            if param_id not in declared:
                errors.append(f"{location}: references undeclared parameter '{param_id}'")

    return errors


def validate_quality_gate_evidence_refs(document: dict[str, Any], gate: dict[str, Any], index: int) -> list[str]:
    errors: list[str] = []
    evidence_refs = gate.get("evidence_refs")
    if gate.get("required") is True and not evidence_refs:
        errors.append(f"$.quality_gates[{index}].evidence_refs: required gates need at least one evidence reference")
        return errors
    if not isinstance(evidence_refs, list):
        return errors

    declared_artifacts = {
        item for item in document.get("contracts", {}).get("artifacts", []) if isinstance(item, str)
    }
    declared_events = {
        item for item in document.get("observability", {}).get("events", []) if isinstance(item, str)
    }
    allowed_refs = declared_artifacts | declared_events

    for ref in evidence_refs:
        if isinstance(ref, str) and ref not in allowed_refs:
            errors.append(
                f"$.quality_gates[{index}].evidence_refs: '{ref}' is not declared in contracts.artifacts or observability.events"
            )

    return errors


def validate_requirements_and_outputs(
    document: dict[str, Any],
    nodes: list[Any],
    adjacency: dict[str, list[str]],
    entrypoint: str,
    produced_by_node: dict[str, set[str]],
    reachable: set[str],
) -> list[str]:
    errors: list[str] = []
    reverse_adjacency: dict[str, list[str]] = {node_id: [] for node_id in adjacency}
    for start, ends in adjacency.items():
        for end in ends:
            reverse_adjacency.setdefault(end, []).append(start)

    declared_artifacts = {
        item for item in document.get("contracts", {}).get("artifacts", []) if isinstance(item, str)
    }
    contract_inputs = {
        field["id"]
        for field in document.get("contracts", {}).get("inputs", [])
        if isinstance(field, dict) and isinstance(field.get("id"), str)
    }

    for node_index, node in enumerate(nodes):
        if not isinstance(node, dict):
            continue
        node_id = node.get("id")
        if not isinstance(node_id, str) or node_id not in reachable:
            continue
        available = declared_artifacts | contract_inputs | upstream_produces(node_id, reverse_adjacency, produced_by_node)
        for requirement in node.get("requires", []):
            if isinstance(requirement, str) and requirement not in available:
                errors.append(
                    f"$.nodes[{node_index}].requires: '{requirement}' is not produced by a reachable upstream node, contract input, or declared artifact"
                )

    all_reachable_produces = set().union(*(produced_by_node.get(node_id, set()) for node_id in reachable))
    required_outputs = [
        field["id"]
        for field in document.get("contracts", {}).get("outputs", [])
        if isinstance(field, dict) and field.get("required") is True and isinstance(field.get("id"), str)
    ]
    for output_id in required_outputs:
        if output_id not in all_reachable_produces:
            errors.append(f"$.contracts.outputs.{output_id}: required output is not produced by a reachable node")

    return errors


def upstream_produces(
    node_id: str,
    reverse_adjacency: dict[str, list[str]],
    produced_by_node: dict[str, set[str]],
) -> set[str]:
    seen: set[str] = set()
    stack = list(reverse_adjacency.get(node_id, []))
    produced: set[str] = set()
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        produced.update(produced_by_node.get(current, set()))
        stack.extend(reverse_adjacency.get(current, []))
    return produced


def collect_reachable(entrypoint: str, adjacency: dict[str, list[str]]) -> set[str]:
    seen: set[str] = set()
    stack = [entrypoint]
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        stack.extend(adjacency.get(current, []))
    return seen


def cmd_validate(args: argparse.Namespace) -> int:
    schema = load_json(args.schema)
    flow_files = find_flow_files(args.paths)
    if not flow_files:
        print("No flow.yaml files found", file=sys.stderr)
        return 1

    failures = 0
    for path in flow_files:
        if not path.exists():
            print(f"FAIL {path}: path does not exist", file=sys.stderr)
            failures += 1
            continue
        try:
            document = load_yaml(path)
            errors = validate_flow_document(document, schema)
        except Exception as exc:  # noqa: BLE001 - CLI should report file context
            print(f"FAIL {path}: {exc}", file=sys.stderr)
            failures += 1
            continue

        if errors:
            failures += 1
            print(f"FAIL {path}", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
        elif args.verbose:
            print(f"OK   {path}")

    if failures:
        print(f"{failures} flow file(s) failed validation", file=sys.stderr)
        return 1

    print(f"Validated {len(flow_files)} flow file(s)")
    return 0


def cmd_validate_adapter_smoke(args: argparse.Namespace) -> int:
    adapter_schema = load_json(args.adapter_schema)
    flow_schema = load_json(args.schema)
    run_schema = load_json(args.run_schema)
    event_schema = load_json(args.event_schema)
    stream_schema = load_json(args.stream_schema)
    adapter_files = find_adapter_smoke_files(args.paths)
    if not adapter_files:
        print("No adapter smoke files found", file=sys.stderr)
        return 1

    failures = 0
    for path in adapter_files:
        if not path.exists():
            print(f"FAIL {path}: path does not exist", file=sys.stderr)
            failures += 1
            continue
        try:
            document = load_json(path)
            errors = validate_adapter_smoke_document(
                document,
                adapter_schema,
                flow_schema,
                run_schema,
                event_schema,
                stream_schema,
                adapter_path=path,
            )
        except Exception as exc:  # noqa: BLE001 - CLI should report file context
            print(f"FAIL {path}: {exc}", file=sys.stderr)
            failures += 1
            continue

        if errors:
            failures += 1
            print(f"FAIL {path}", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
        elif args.verbose:
            print(f"OK   {path}")

    if failures:
        print(f"{failures} adapter smoke file(s) failed validation", file=sys.stderr)
        return 1

    print(f"Validated {len(adapter_files)} adapter smoke file(s)")
    return 0


def cmd_normalize(args: argparse.Namespace) -> int:
    schema = load_json(args.schema)
    flow_files = find_flow_files(args.paths)
    if not flow_files:
        print("No flow.yaml files found", file=sys.stderr)
        return 1

    failures = 0
    changed = 0
    for path in flow_files:
        if not path.exists():
            print(f"FAIL {path}: path does not exist", file=sys.stderr)
            failures += 1
            continue
        try:
            document = load_yaml(path)
            errors = validate_flow_document(document, schema)
            if errors:
                failures += 1
                print(f"FAIL {path}", file=sys.stderr)
                for error in errors:
                    print(f"  - {error}", file=sys.stderr)
                continue
            normalized = dump_yaml(normalize_flow_document(document))
            current = path.read_text(encoding="utf-8")
        except Exception as exc:  # noqa: BLE001 - CLI should report file context
            print(f"FAIL {path}: {exc}", file=sys.stderr)
            failures += 1
            continue

        if normalized == current:
            if args.verbose:
                print(f"OK   {path}")
            continue

        changed += 1
        if args.write:
            path.write_text(normalized, encoding="utf-8")
            if args.verbose:
                print(f"WROTE {path}")
        else:
            print(f"FAIL {path}: not normalized", file=sys.stderr)
            failures += 1

    if failures:
        print(f"{failures} flow file(s) failed normalization", file=sys.stderr)
        return 1

    if args.write:
        print(f"Normalized {changed} of {len(flow_files)} flow file(s)")
    else:
        print(f"Checked normalization for {len(flow_files)} flow file(s)")
    return 0


def cmd_validate_event(args: argparse.Namespace) -> int:
    schema = load_json(args.event_schema)
    event_files = find_json_files(args.paths)
    if not event_files:
        print("No event JSON files found", file=sys.stderr)
        return 1

    failures = 0
    for path in event_files:
        if not path.exists():
            print(f"FAIL {path}: path does not exist", file=sys.stderr)
            failures += 1
            continue
        try:
            document = load_json(path)
            errors = validate_event_document(document, schema)
        except Exception as exc:  # noqa: BLE001 - CLI should report file context
            print(f"FAIL {path}: {exc}", file=sys.stderr)
            failures += 1
            continue

        if errors:
            failures += 1
            print(f"FAIL {path}", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
        elif args.verbose:
            print(f"OK   {path}")

    if failures:
        print(f"{failures} event file(s) failed validation", file=sys.stderr)
        return 1

    print(f"Validated {len(event_files)} event file(s)")
    return 0


def cmd_validate_stream(args: argparse.Namespace) -> int:
    stream_schema = load_json(args.stream_schema)
    event_schema = load_json(args.event_schema)
    flow_schema = load_json(args.schema)
    stream_files = find_event_stream_files(args.paths)
    if not stream_files:
        print("No event stream manifest files found", file=sys.stderr)
        return 1

    failures = 0
    for path in stream_files:
        if not path.exists():
            print(f"FAIL {path}: path does not exist", file=sys.stderr)
            failures += 1
            continue
        try:
            document = load_json(path)
            errors = validate_event_stream_document(
                document,
                stream_schema,
                event_schema,
                flow_schema,
                stream_path=path,
            )
        except Exception as exc:  # noqa: BLE001 - CLI should report file context
            print(f"FAIL {path}: {exc}", file=sys.stderr)
            failures += 1
            continue

        if errors:
            failures += 1
            print(f"FAIL {path}", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
        elif args.verbose:
            print(f"OK   {path}")

    if failures:
        print(f"{failures} event stream file(s) failed validation", file=sys.stderr)
        return 1

    print(f"Validated {len(stream_files)} event stream file(s)")
    return 0


def cmd_validate_run(args: argparse.Namespace) -> int:
    run_schema = load_json(args.run_schema)
    event_schema = load_json(args.event_schema)
    flow_schema = load_json(args.schema)
    run_files = find_run_files(args.paths)
    if not run_files:
        print("No run bundle files found", file=sys.stderr)
        return 1

    failures = 0
    for path in run_files:
        if not path.exists():
            print(f"FAIL {path}: path does not exist", file=sys.stderr)
            failures += 1
            continue
        try:
            document = load_json(path)
            errors = validate_run_document(document, run_schema, event_schema, flow_schema, run_path=path)
        except Exception as exc:  # noqa: BLE001 - CLI should report file context
            print(f"FAIL {path}: {exc}", file=sys.stderr)
            failures += 1
            continue

        if errors:
            failures += 1
            print(f"FAIL {path}", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
        elif args.verbose:
            print(f"OK   {path}")

    if failures:
        print(f"{failures} run bundle file(s) failed validation", file=sys.stderr)
        return 1

    print(f"Validated {len(run_files)} run bundle file(s)")
    return 0


def cmd_replay(args: argparse.Namespace) -> int:
    run_schema = load_json(args.run_schema)
    event_schema = load_json(args.event_schema)
    flow_schema = load_json(args.schema)
    run_files = find_run_files(args.paths)
    if not run_files:
        print("No run bundle files found", file=sys.stderr)
        return 1

    failures = 0
    summaries: list[dict[str, Any]] = []
    for path in run_files:
        if not path.exists():
            print(f"FAIL {path}: path does not exist", file=sys.stderr)
            failures += 1
            continue
        try:
            document = load_json(path)
            errors = validate_run_document(document, run_schema, event_schema, flow_schema, run_path=path)
        except Exception as exc:  # noqa: BLE001 - CLI should report file context
            print(f"FAIL {path}: {exc}", file=sys.stderr)
            failures += 1
            continue

        if errors:
            failures += 1
            print(f"FAIL {path}", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            continue

        summary = build_replay_summary(document)
        summary["path"] = str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
        summaries.append(summary)

    if failures:
        print(f"{failures} run bundle file(s) failed replay validation", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(summaries, indent=2))
    else:
        print_replay_summaries(summaries)
    return 0


def build_replay_summary(document: dict[str, Any]) -> dict[str, Any]:
    flow_info = document.get("flow", {})
    run_info = document.get("run", {})
    events = document.get("events", [])
    outputs = document.get("outputs", {})

    timeline: list[dict[str, Any]] = []
    gates: list[dict[str, Any]] = []
    for event in events if isinstance(events, list) else []:
        if not isinstance(event, dict):
            continue
        replay_event = {
            "timestamp": event.get("timestamp"),
            "event": event.get("event"),
            "node_id": event.get("node_id"),
            "severity": event.get("severity"),
        }
        timeline.append({key: value for key, value in replay_event.items() if value is not None})

        payload = event.get("payload", {})
        if event.get("event") == "gate.completed" and isinstance(payload, dict):
            gates.append(
                {
                    "gate_id": payload.get("gate_id"),
                    "status": payload.get("status"),
                    "node_id": event.get("node_id"),
                    "evidence_refs": sorted(collect_event_evidence_refs(event.get("evidence"))),
                }
            )

    return {
        "flow": {
            "id": flow_info.get("id"),
            "version": flow_info.get("version"),
            "source": flow_info.get("source"),
        },
        "run": {
            "id": run_info.get("id"),
            "core": run_info.get("core"),
            "status": run_info.get("status"),
            "started_at": run_info.get("started_at"),
            "completed_at": run_info.get("completed_at"),
        },
        "event_count": len(timeline),
        "gates": gates,
        "outputs": sorted(outputs) if isinstance(outputs, dict) else [],
        "timeline": timeline,
    }


def print_replay_summaries(summaries: list[dict[str, Any]]) -> None:
    for summary_index, summary in enumerate(summaries):
        if summary_index:
            print()
        flow = summary["flow"]
        run = summary["run"]
        print(f"Run {run.get('id')} ({run.get('status')})")
        print(f"Flow: {flow.get('id')}@{flow.get('version')}  Core: {run.get('core')}  Events: {summary['event_count']}")
        print(f"Outputs: {', '.join(summary['outputs']) if summary['outputs'] else 'none'}")
        if summary["gates"]:
            print("Gates:")
            for gate in summary["gates"]:
                refs = ", ".join(gate.get("evidence_refs", [])) or "none"
                print(f"  - {gate.get('gate_id')}: {gate.get('status')} ({refs})")
        print("Timeline:")
        for event in summary["timeline"]:
            node = f" [{event['node_id']}]" if "node_id" in event else ""
            print(f"  - {event.get('timestamp')} {event.get('event')}{node} {event.get('severity')}")


def cmd_validate_samples(args: argparse.Namespace) -> int:
    sample_schema = load_json(args.sample_schema)
    flow_schema = load_json(args.schema)
    sample_files = find_sample_files(args.paths)
    if not sample_files:
        print("No flow sample files found", file=sys.stderr)
        return 1

    failures = 0
    sampled_flow_ids: set[str] = set()
    for path in sample_files:
        if not path.exists():
            print(f"FAIL {path}: path does not exist", file=sys.stderr)
            failures += 1
            continue
        try:
            document = load_json(path)
            errors = validate_sample_document(document, sample_schema, flow_schema, sample_path=path)
            flow_info = document.get("flow", {})
            if isinstance(flow_info, dict) and isinstance(flow_info.get("id"), str):
                sampled_flow_ids.add(flow_info["id"])
        except Exception as exc:  # noqa: BLE001 - CLI should report file context
            print(f"FAIL {path}: {exc}", file=sys.stderr)
            failures += 1
            continue

        if errors:
            failures += 1
            print(f"FAIL {path}", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
        elif args.verbose:
            print(f"OK   {path}")

    if not args.paths:
        missing_flow_ids = production_flow_ids(flow_schema) - sampled_flow_ids
        if missing_flow_ids:
            failures += 1
            print("FAIL examples/samples: missing samples for production flows", file=sys.stderr)
            for flow_id in sorted(missing_flow_ids):
                print(f"  - {flow_id}", file=sys.stderr)

    if failures:
        print(f"{failures} flow sample file(s) failed validation", file=sys.stderr)
        return 1

    print(f"Validated {len(sample_files)} flow sample file(s)")
    return 0


def cmd_changelog_check(args: argparse.Namespace) -> int:
    errors = validate_changelog(args.changelog, release=args.release)
    if errors:
        print(f"FAIL {args.changelog}", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    if args.release:
        print(f"Changelog contains release {args.release}")
    else:
        print(f"Changelog check passed for {args.changelog}")
    return 0


def validate_changelog(path: Path, *, release: str | None = None) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"{path}: file does not exist"]

    content = path.read_text(encoding="utf-8")
    if not content.startswith("# Changelog"):
        errors.append("missing top-level '# Changelog' heading")
    unreleased = extract_changelog_section(content, "Unreleased")
    if unreleased is None:
        errors.append("missing '## Unreleased' section")
    elif not re.search(r"^###\s+\w+", unreleased, flags=re.MULTILINE):
        errors.append("'## Unreleased' section needs at least one subsection")
    elif not re.search(r"^\s*-\s+\S+", unreleased, flags=re.MULTILINE):
        errors.append("'## Unreleased' section needs at least one bullet")

    for match in re.finditer(r"^##\s+([0-9]+\.[0-9]+\.[0-9]+)\s+-\s+([0-9]{4}-[0-9]{2}-[0-9]{2})\s*$", content, flags=re.MULTILINE):
        date_value = match.group(2)
        try:
            datetime.strptime(date_value, "%Y-%m-%d")
        except ValueError:
            errors.append(f"release {match.group(1)} has invalid date {date_value}")

    if release and not re.search(rf"^##\s+{re.escape(release)}\s+-\s+[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}\s*$", content, flags=re.MULTILINE):
        errors.append(f"missing release heading for {release}")

    return errors


def extract_changelog_section(content: str, heading: str) -> str | None:
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$", content, flags=re.MULTILINE)
    if not match:
        return None
    next_heading = re.search(r"^##\s+", content[match.end() :], flags=re.MULTILINE)
    end = match.end() + next_heading.start() if next_heading else len(content)
    return content[match.end() : end]


def cmd_check_links(args: argparse.Namespace) -> int:
    files = find_markdown_files(args.paths)
    if not files:
        print("No Markdown files found", file=sys.stderr)
        return 1

    failures = 0
    for path in files:
        if not path.exists():
            print(f"FAIL {path}: path does not exist", file=sys.stderr)
            failures += 1
            continue
        errors = validate_markdown_links(path)
        if errors:
            failures += 1
            print(f"FAIL {path}", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
        elif args.verbose:
            print(f"OK   {path}")

    if failures:
        print(f"{failures} Markdown file(s) failed link validation", file=sys.stderr)
        return 1

    print(f"Validated links in {len(files)} Markdown file(s)")
    return 0


def cmd_package_release(args: argparse.Namespace) -> int:
    output_path = args.output.resolve()
    files = collect_release_package_files(args.paths)
    if not files:
        print("No release package files found", file=sys.stderr)
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive_path = path.relative_to(REPO_ROOT).as_posix()
            info = zipfile.ZipInfo(archive_path, date_time=ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())

    print(f"Wrote release package {output_path} with {len(files)} file(s)")
    return 0


def collect_release_package_files(paths: Iterable[Path]) -> list[Path]:
    selected = list(paths)
    if not selected:
        selected = DEFAULT_RELEASE_PACKAGE_PATHS

    files: list[Path] = []
    for path in selected:
        path = path.resolve()
        if path.is_file():
            files.append(path)
            continue
        if not path.exists():
            continue
        files.extend(item for item in sorted(path.rglob("*")) if item.is_file())

    output_safe_files = [
        path
        for path in sorted(dict.fromkeys(files))
        if ".git" not in path.parts and "__pycache__" not in path.parts and path.name != ".DS_Store"
    ]
    return output_safe_files


def cmd_release_check(args: argparse.Namespace) -> int:
    flow_files = find_flow_files(args.paths)
    errors = validate_release_readiness(
        flow_files,
        load_json(args.schema),
        load_json(args.adapter_schema),
        load_json(args.run_schema),
        load_json(args.event_schema),
        load_json(args.stream_schema),
        load_json(args.sample_schema),
    )
    if errors:
        print("Release check failed", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"Release check passed for {len(flow_files)} flow file(s)")
    return 0


def validate_release_readiness(
    flow_files: Iterable[Path],
    flow_schema: dict[str, Any],
    adapter_schema: dict[str, Any],
    run_schema: dict[str, Any],
    event_schema: dict[str, Any],
    stream_schema: dict[str, Any],
    sample_schema: dict[str, Any],
) -> list[str]:
    entries, errors = load_release_flow_entries(flow_files, flow_schema)
    sample_flow_ids, sample_errors = load_valid_sample_flow_ids(sample_schema, flow_schema)
    adapter_pairs, adapter_errors = load_valid_adapter_smoke_pairs(
        adapter_schema,
        flow_schema,
        run_schema,
        event_schema,
        stream_schema,
    )
    completed_run_pairs, run_errors = load_valid_completed_run_pairs(run_schema, event_schema, flow_schema)

    errors.extend(sample_errors)
    errors.extend(adapter_errors)
    errors.extend(run_errors)
    errors.extend(validate_deprecation_targets(entries))

    for entry in entries:
        document = entry["document"]
        if document.get("stability") == "stable":
            errors.extend(validate_stable_flow_readiness(entry, sample_flow_ids, adapter_pairs, completed_run_pairs))

    return errors


def load_release_flow_entries(
    flow_files: Iterable[Path],
    flow_schema: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str]]:
    selected = list(flow_files)
    if not selected:
        return [], ["flows: no flow files found"]

    entries: list[dict[str, Any]] = []
    errors: list[str] = []
    paths_by_id: dict[str, list[str]] = {}
    for path in selected:
        if not path.exists():
            errors.append(f"{display_path(path)}: path does not exist")
            continue
        try:
            document = load_yaml(path)
        except Exception as exc:  # noqa: BLE001 - release check should report file context
            errors.append(f"{display_path(path)}: {exc}")
            continue

        flow_errors = validate_flow_document(document, flow_schema)
        if flow_errors:
            errors.extend(f"{display_path(path)}: {error}" for error in flow_errors)
            continue

        flow_id = document.get("id")
        if isinstance(flow_id, str):
            paths_by_id.setdefault(flow_id, []).append(display_path(path))
        entries.append({"path": path, "document": document})

    for flow_id, paths in sorted(paths_by_id.items()):
        if len(paths) > 1:
            joined_paths = ", ".join(paths)
            errors.append(f"$.id: duplicate flow id '{flow_id}' in {joined_paths}")

    return entries, errors


def load_valid_sample_flow_ids(
    sample_schema: dict[str, Any],
    flow_schema: dict[str, Any],
) -> tuple[set[str], list[str]]:
    flow_ids: set[str] = set()
    errors: list[str] = []
    for path in find_sample_files([]):
        if not path.exists():
            errors.append(f"{display_path(path)}: path does not exist")
            continue
        try:
            document = load_json(path)
            sample_errors = validate_sample_document(document, sample_schema, flow_schema, sample_path=path)
        except Exception as exc:  # noqa: BLE001 - release check should report file context
            errors.append(f"{display_path(path)}: {exc}")
            continue

        if sample_errors:
            errors.extend(f"{display_path(path)}: {error}" for error in sample_errors)
            continue

        flow_info = document.get("flow", {})
        if isinstance(flow_info, dict) and isinstance(flow_info.get("id"), str):
            flow_ids.add(flow_info["id"])

    return flow_ids, errors


def load_valid_adapter_smoke_pairs(
    adapter_schema: dict[str, Any],
    flow_schema: dict[str, Any],
    run_schema: dict[str, Any],
    event_schema: dict[str, Any],
    stream_schema: dict[str, Any],
) -> tuple[set[tuple[str, str]], list[str]]:
    pairs: set[tuple[str, str]] = set()
    errors: list[str] = []
    for path in find_adapter_smoke_files([]):
        if not path.exists():
            errors.append(f"{display_path(path)}: path does not exist")
            continue
        try:
            document = load_json(path)
            adapter_errors = validate_adapter_smoke_document(
                document,
                adapter_schema,
                flow_schema,
                run_schema,
                event_schema,
                stream_schema,
                adapter_path=path,
            )
        except Exception as exc:  # noqa: BLE001 - release check should report file context
            errors.append(f"{display_path(path)}: {exc}")
            continue

        if adapter_errors:
            errors.extend(f"{display_path(path)}: {error}" for error in adapter_errors)
            continue

        flow_info = document.get("flow", {})
        consumer = document.get("consumer")
        if isinstance(flow_info, dict) and isinstance(flow_info.get("id"), str) and isinstance(consumer, str):
            pairs.add((flow_info["id"], consumer))

    return pairs, errors


def load_valid_completed_run_pairs(
    run_schema: dict[str, Any],
    event_schema: dict[str, Any],
    flow_schema: dict[str, Any],
) -> tuple[set[tuple[str, str]], list[str]]:
    pairs: set[tuple[str, str]] = set()
    errors: list[str] = []
    for path in find_run_files([REPO_ROOT / "examples"]):
        if not path.exists():
            errors.append(f"{display_path(path)}: path does not exist")
            continue
        try:
            document = load_json(path)
            run_errors = validate_run_document(document, run_schema, event_schema, flow_schema, run_path=path)
        except Exception as exc:  # noqa: BLE001 - release check should report file context
            errors.append(f"{display_path(path)}: {exc}")
            continue

        if run_errors:
            errors.extend(f"{display_path(path)}: {error}" for error in run_errors)
            continue

        flow_info = document.get("flow", {})
        run_info = document.get("run", {})
        if (
            isinstance(flow_info, dict)
            and isinstance(run_info, dict)
            and run_info.get("status") == "completed"
            and isinstance(flow_info.get("id"), str)
            and isinstance(run_info.get("core"), str)
        ):
            pairs.add((flow_info["id"], run_info["core"]))

    return pairs, errors


def validate_deprecation_targets(entries: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    entries_by_id = {
        entry["document"]["id"]: entry
        for entry in entries
        if isinstance(entry.get("document"), dict) and isinstance(entry["document"].get("id"), str)
    }

    for entry in entries:
        path = entry["path"]
        document = entry["document"]
        flow_id = document.get("id")
        replacement_id = document.get("deprecated_by")
        if not isinstance(flow_id, str) or not isinstance(replacement_id, str):
            continue
        if replacement_id == flow_id:
            errors.append(f"{display_path(path)}: $.deprecated_by: cannot reference itself")
            continue
        replacement_entry = entries_by_id.get(replacement_id)
        if not replacement_entry:
            errors.append(
                f"{display_path(path)}: $.deprecated_by: replacement flow '{replacement_id}' is not in the release catalog"
            )
            continue
        replacement_document = replacement_entry["document"]
        if replacement_document.get("deprecated_by"):
            errors.append(
                f"{display_path(path)}: $.deprecated_by: replacement flow '{replacement_id}' is also deprecated"
            )
        is_production_flow = path.resolve().is_relative_to(REPO_ROOT / "flows")
        replacement_is_production_flow = replacement_entry["path"].resolve().is_relative_to(REPO_ROOT / "flows")
        if is_production_flow and not replacement_is_production_flow:
            errors.append(
                f"{display_path(path)}: $.deprecated_by: production flows must be replaced by another production flow"
            )

    return errors


def validate_stable_flow_readiness(
    entry: dict[str, Any],
    sample_flow_ids: set[str],
    adapter_pairs: set[tuple[str, str]],
    completed_run_pairs: set[tuple[str, str]],
) -> list[str]:
    errors: list[str] = []
    path = entry["path"]
    document = entry["document"]
    flow_id = document.get("id")
    if not isinstance(flow_id, str):
        return errors

    if document.get("deprecated_by"):
        errors.append(f"{display_path(path)}: $.deprecated_by: stable flows must not be deprecated")

    readme_path = path.with_name("README.md")
    if not readme_path.exists():
        errors.append(f"{display_path(path)}: $.readme: stable flows require a sibling README.md")
    elif not readme_has_maturity_rubric(readme_path):
        errors.append(f"{display_path(path)}: $.readme: stable flow README requires a maturity rubric")

    if flow_id not in sample_flow_ids:
        errors.append(
            f"{display_path(path)}: $.sample: stable flows require a valid examples/samples/*.sample.json file"
        )

    supported_cores = set(document.get("runtime", {}).get("supported_cores", []))
    for consumer in sorted(supported_cores & OPTIONAL_CONSUMERS):
        if (flow_id, consumer) not in adapter_pairs:
            errors.append(
                f"{display_path(path)}: $.runtime.supported_cores: stable flow requires adapter smoke evidence for {consumer}"
            )
    if "standalone" in supported_cores and (flow_id, "standalone") not in completed_run_pairs:
        errors.append(
            f"{display_path(path)}: $.runtime.supported_cores: stable flow requires completed standalone run evidence"
        )

    return errors


def validate_markdown_links(path: Path) -> list[str]:
    errors: list[str] = []
    content = path.read_text(encoding="utf-8")
    for line_number, line in enumerate(content.splitlines(), start=1):
        for match in MARKDOWN_LINK_PATTERN.finditer(line):
            target = match.group(1).strip()
            if should_skip_markdown_link(target):
                continue
            target_path_text = unquote(target.split("#", 1)[0])
            if not target_path_text:
                continue
            target_path = (path.parent / target_path_text).resolve()
            if not target_path.exists():
                errors.append(f"line {line_number}: missing local link target {target}")
    return errors


def should_skip_markdown_link(target: str) -> bool:
    lowered = target.lower()
    return (
        lowered.startswith("http://")
        or lowered.startswith("https://")
        or lowered.startswith("mailto:")
        or lowered.startswith("tel:")
        or lowered.startswith("app://")
    )


def production_flow_ids(flow_schema: dict[str, Any]) -> set[str]:
    flow_ids: set[str] = set()
    for path in find_flow_files([REPO_ROOT / "flows"]):
        try:
            document = load_yaml(path)
        except Exception:
            continue
        if not validate_flow_document(document, flow_schema) and isinstance(document.get("id"), str):
            flow_ids.add(document["id"])
    return flow_ids


def cmd_check_composition(args: argparse.Namespace) -> int:
    catalog, catalog_errors = build_flow_catalog([])
    targets = find_flow_files(args.paths)
    if not targets:
        print("No flow.yaml files found", file=sys.stderr)
        return 1

    failures = 0
    if catalog_errors:
        print("Catalog build warnings:", file=sys.stderr)
        for error in catalog_errors:
            print(f"  - {error}", file=sys.stderr)

    composing = 0
    for path in targets:
        if not path.exists():
            print(f"FAIL {path}: path does not exist", file=sys.stderr)
            failures += 1
            continue
        try:
            document = load_yaml(path)
        except Exception as exc:  # noqa: BLE001 - CLI should report file context
            print(f"FAIL {path}: {exc}", file=sys.stderr)
            failures += 1
            continue
        if not composition.flow_ref_nodes(document):
            continue
        composing += 1
        errors = composition.validate_composition_static(document, catalog)
        if errors:
            failures += 1
            print(f"FAIL {display_path(path)}", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
        elif args.verbose:
            print(f"OK   {display_path(path)}")

    if failures:
        print(f"{failures} flow file(s) failed composition checks", file=sys.stderr)
        return 1

    print(f"Checked composition for {composing} composing flow file(s)")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    schema = load_json(args.schema)
    rows: list[tuple[str, str, str, str]] = []
    failures = 0
    for path in find_flow_files(args.paths):
        try:
            document = load_yaml(path)
            errors = validate_flow_document(document, schema)
        except Exception as exc:  # noqa: BLE001 - CLI should report file context
            print(f"FAIL {path}: {exc}", file=sys.stderr)
            failures += 1
            continue
        if errors:
            print(f"FAIL {path}: invalid flow", file=sys.stderr)
            failures += 1
            continue
        runtime = document.get("runtime", {})
        supported = ", ".join(runtime.get("supported_cores", []))
        rows.append((document["id"], document["version"], document["stability"], supported))

    if failures:
        return 1

    if args.json:
        print(json.dumps([{"id": row[0], "version": row[1], "stability": row[2], "supported_cores": row[3].split(", ")} for row in rows], indent=2))
        return 0

    print(f"{'ID':42} {'VERSION':10} {'STABILITY':12} CORES")
    print("-" * 90)
    for row in rows:
        print(f"{row[0]:42} {row[1]:10} {row[2]:12} {row[3]}")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    schema = load_json(args.schema)
    entries: list[dict[str, Any]] = []
    failures = 0
    sampled_flow_ids = load_sampled_flow_ids()

    for path in find_flow_files(args.paths):
        try:
            document = load_yaml(path)
            errors = validate_flow_document(document, schema)
        except Exception as exc:  # noqa: BLE001 - CLI should report file context
            entries.append({"path": str(path), "valid": False, "issues": [str(exc)]})
            failures += 1
            continue

        issues = list(errors)
        readme_path = path.with_name("README.md")
        is_production_flow = "flows" in path.parts
        has_sample = document.get("id") in sampled_flow_ids
        has_maturity_rubric = readme_path.exists() and readme_has_maturity_rubric(readme_path)
        if is_production_flow and not readme_path.exists():
            issues.append("$.readme: reusable flows require a sibling README.md")
        if is_production_flow and readme_path.exists() and not has_maturity_rubric:
            issues.append("$.readme: production flow README requires a maturity rubric")
        if is_production_flow and not has_sample:
            issues.append("$.sample: production flows require an examples/samples/*.sample.json file")
        if document.get("stability") == "stable":
            issues.append("$.stability: stable flows require external adapter evidence before promotion")

        runtime = document.get("runtime", {})
        gates = document.get("quality_gates", [])
        required_gates = [gate for gate in gates if isinstance(gate, dict) and gate.get("required") is True]
        entries.append(
            {
                "id": document.get("id"),
                "version": document.get("version"),
                "stability": document.get("stability"),
                "path": str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path),
                "valid": not errors,
                "issues": issues,
                "supported_cores": runtime.get("supported_cores", []),
                "required_capabilities": runtime.get("required_capabilities", []),
                "nodes": len(document.get("nodes", [])),
                "quality_gates": len(gates),
                "required_quality_gates": len(required_gates),
                "has_readme": readme_path.exists(),
                "has_maturity_rubric": has_maturity_rubric,
                "has_sample": has_sample,
            }
        )
        if errors:
            failures += 1

    summary = build_report_summary(entries)
    report = {"summary": summary, "flows": entries}

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_text_report(report)

    if failures:
        return 1
    return 0


def load_sampled_flow_ids() -> set[str]:
    flow_ids: set[str] = set()
    for sample_path in find_sample_files([]):
        try:
            sample = load_json(sample_path)
        except Exception:
            continue
        flow_info = sample.get("flow", {})
        if isinstance(flow_info, dict) and isinstance(flow_info.get("id"), str):
            flow_ids.add(flow_info["id"])
    return flow_ids


def readme_has_maturity_rubric(path: Path) -> bool:
    try:
        content = path.read_text(encoding="utf-8").lower()
    except OSError:
        return False
    return "## maturity rubric" in content


def build_report_summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
    stability = Counter(str(entry.get("stability")) for entry in entries)
    core_counts: Counter[str] = Counter()
    for entry in entries:
        core_counts.update(entry.get("supported_cores", []))
    return {
        "total": len(entries),
        "valid": sum(1 for entry in entries if entry.get("valid")),
        "with_issues": sum(1 for entry in entries if entry.get("issues")),
        "by_stability": dict(sorted(stability.items())),
        "by_optional_consumer": dict(sorted(core_counts.items())),
    }


def print_text_report(report: dict[str, Any]) -> None:
    summary = report["summary"]
    print("Flow report")
    print(f"Total: {summary['total']}  Valid: {summary['valid']}  With issues: {summary['with_issues']}")
    print(f"By stability: {', '.join(f'{key}={value}' for key, value in summary['by_stability'].items())}")
    print(f"By optional consumer: {', '.join(f'{key}={value}' for key, value in summary['by_optional_consumer'].items())}")
    print()
    print(f"{'ID':42} {'STABILITY':12} {'OPTIONAL CONSUMERS':48} {'NODES':5} {'GATES':5} ISSUES")
    print("-" * 130)
    for entry in report["flows"]:
        cores = ",".join(entry.get("supported_cores", []))
        issue_count = len(entry.get("issues", []))
        issue_text = "ok" if issue_count == 0 else str(issue_count)
        print(
            f"{str(entry.get('id')):42} "
            f"{str(entry.get('stability')):12} "
            f"{cores[:48]:48} "
            f"{entry.get('nodes', 0):5} "
            f"{entry.get('quality_gates', 0):5} "
            f"{issue_text}"
        )


def cmd_graph(args: argparse.Namespace) -> int:
    schema = load_json(args.schema)
    document = load_yaml(args.flow)
    errors = validate_flow_document(document, schema)
    if errors:
        print(f"FAIL {args.flow}", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    output = graph_as_dot(document) if args.format == "dot" else json.dumps(graph_as_json(document), indent=2)
    if args.output:
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0


def graph_as_json(document: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": document["id"],
        "version": document["version"],
        "entrypoint": document["entrypoint"],
        "nodes": [
            {
                "id": node["id"],
                "type": node["type"],
                "title": node["title"],
            }
            for node in document["nodes"]
        ],
        "edges": document["edges"],
    }


def graph_as_dot(document: dict[str, Any]) -> str:
    lines = [f'digraph "{escape_dot(document["id"])}" {{', "  rankdir=LR;"]
    for node in document["nodes"]:
        label = f'{node["title"]}\\n{node["type"]}'
        lines.append(f'  "{escape_dot(node["id"])}" [label="{escape_dot(label)}"];')
    for edge in document["edges"]:
        label = edge.get("condition")
        if label:
            lines.append(f'  "{escape_dot(edge["from"])}" -> "{escape_dot(edge["to"])}" [label="{escape_dot(label)}"];')
        else:
            lines.append(f'  "{escape_dot(edge["from"])}" -> "{escape_dot(edge["to"])}";')
    lines.append("}")
    return "\n".join(lines)


def escape_dot(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


# --- Reference runner: execute a flow with local handlers and emit real evidence ---

SUBSTITUTION_PATTERN = re.compile(r"\$\{(param|input)\.([a-z0-9_-]+)\}")
ARTIFACT_KIND_BY_EXT = {"command-output": "log", "command-error": "log", "json": "json", "markdown": "md"}


def parse_kv_list(items: Iterable[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for item in items or []:
        if "=" not in item:
            raise ValueError(f"expected key=value, got {item!r}")
        key, value = item.split("=", 1)
        values[key] = value
    return values


def substitute_command(template: str, params: dict[str, Any], inputs: dict[str, Any]) -> str:
    def repl(match: re.Match[str]) -> str:
        scope, name = match.group(1), match.group(2)
        source = params if scope == "param" else inputs
        return str(source[name]) if name in source else match.group(0)

    return SUBSTITUTION_PATTERN.sub(repl, template)


def execution_order(document: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = list(document.get("nodes", []))
    produced_by = {p: n["id"] for n in nodes for p in n.get("produces", [])}
    deps = {
        n["id"]: {produced_by[r] for r in n.get("requires", []) if r in produced_by and produced_by[r] != n["id"]}
        for n in nodes
    }
    order: list[dict[str, Any]] = []
    resolved: set[str] = set()
    pending = nodes[:]
    while pending:
        nxt = next((n for n in pending if deps[n["id"]] <= resolved), pending[0])
        order.append(nxt)
        resolved.add(nxt["id"])
        pending.remove(nxt)
    return order


DATA_NODE_TYPES = ("intake", "plan", "decision", "verifier", "finalizer")


def plan_flow(document: dict[str, Any], handlers: dict[str, str] | None = None) -> dict[str, Any]:
    """Classify each node's execution disposition without running anything.

    Disposition is one of: 'command' (the flow runs a command), 'data' (the
    runner assembles a record), 'handler' (a consumer-supplied handler is bound),
    or 'needs-handler' (an agent_task/approval/handoff a consumer must bind).
    """
    handlers = handlers or {}
    steps: list[dict[str, Any]] = []
    needs_handlers: list[str] = []
    for node in execution_order(document):
        node_id = node["id"]
        node_type = node["type"]
        if node.get("command"):
            disposition = "command"
        elif node_type in DATA_NODE_TYPES:
            disposition = "data"
        elif node_id in handlers:
            disposition = "handler"
        else:
            disposition = "needs-handler"
            needs_handlers.append(node_id)
        steps.append({"id": node_id, "type": node_type, "disposition": disposition})
    return {
        "order": [step["id"] for step in steps],
        "steps": steps,
        "needs_handlers": needs_handlers,
    }


def run_flow(
    document: dict[str, Any],
    flow_source: str,
    inputs: dict[str, Any],
    params: dict[str, Any],
    workdir: Path,
    out_dir: Path,
    handlers: dict[str, str] | None = None,
    simulate: bool = False,
) -> tuple[dict[str, Any], str, list[str]]:
    handlers = handlers or {}
    flow_id = document["id"]
    flow_version = document["version"]
    core = "standalone"
    run_id = "run-" + re.sub(r"[^a-z0-9]+", "-", flow_id) + "-local"
    artifacts_dir = out_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    declared_artifacts = set(document.get("contracts", {}).get("artifacts", []))
    output_ids = {f["id"] for f in document.get("contracts", {}).get("outputs", []) if isinstance(f, dict)}
    param_values = dict(params)
    for node in document["nodes"]:
        for param in node.get("parameters", []):
            if param["id"] not in param_values and "default" in param:
                param_values[param["id"]] = param["default"]

    events: list[dict[str, Any]] = []
    artifacts: dict[str, dict[str, Any]] = {}
    artifact_ok: dict[str, bool] = {}
    produced_by_node: dict[str, str] = {}
    outputs: dict[str, Any] = {}
    needs_handler: list[str] = []
    status = "completed"

    def now() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def emit(event: str, node: str | None = None, payload: Any = None, evidence: Any = None, severity: str = "info") -> None:
        record = {
            "event_version": "agentic-flows.events/v1",
            "flow_id": flow_id,
            "flow_version": flow_version,
            "run_id": run_id,
            **({"node_id": node} if node else {}),
            "event": event,
            "timestamp": now(),
            "core": core,
            "severity": severity,
        }
        if payload is not None:
            record["payload"] = payload
        if evidence is not None:
            record["evidence"] = evidence
        events.append(record)

    def write_file(name: str, content: str, kind: str) -> str:
        ext = ARTIFACT_KIND_BY_EXT.get(kind, "txt")
        filename = re.sub(r"[^a-z0-9._-]+", "-", name) + "." + ext
        (artifacts_dir / filename).write_text(content, encoding="utf-8")
        return f"artifacts/{filename}"

    def record_artifact(name: str, content: str, kind: str, node_id: str, ok: bool) -> None:
        uri = write_file(name, content, kind)
        artifacts[name] = {"id": name, "kind": kind, "uri": uri}
        artifact_ok[name] = ok
        produced_by_node[name] = node_id

    def record_output(name: str, content: str, kind: str) -> None:
        outputs[name] = write_file("output-" + name, content, kind)

    def emit_produces(node: dict[str, Any], content: str, kind: str, ok: bool) -> None:
        names = node.get("produces", []) or [f"{node['id']}-output"]
        for name in names:
            if name in output_ids:
                record_output(name, content, "markdown")
            else:
                record_artifact(name, content, kind, node["id"], ok)

    emit("flow.started")
    start_at = now()

    for node in execution_order(document):
        node_id = node["id"]
        node_type = node["type"]
        flow_command = node.get("command")
        handler_command = handlers.get(node_id)
        command = flow_command or handler_command
        if simulate and node_type not in DATA_NODE_TYPES:
            # Wiring check: assume every working/agent step succeeds and produces
            # its declared outputs, without running anything. Verifies that gates
            # are satisfiable and required outputs are produced.
            emit_produces(node, f"[simulated] {node_id} produced its declared outputs\n", "command-output", True)
            emit("node.completed", node=node_id, payload={"simulated": True})
        elif command:
            rendered = substitute_command(command, param_values, inputs)
            on_failure = node.get("on_failure") or {}
            attempts = on_failure.get("max_attempts", 1) if on_failure.get("action") == "retry" else 1
            returncode = 1
            output = ""
            for _ in range(max(1, attempts)):
                try:
                    proc = subprocess.run(
                        rendered, shell=True, cwd=str(workdir), capture_output=True, text=True,
                        timeout=node.get("timeout_seconds", 600),
                    )
                    returncode = proc.returncode
                    output = (proc.stdout or "") + (proc.stderr or "")
                except Exception as exc:  # noqa: BLE001 - runner reports command failures
                    returncode, output = 1, str(exc)
                if returncode == 0:
                    break
            ok = returncode == 0
            log = f"$ {rendered}\n(exit {returncode})\n\n{output}"
            emit_produces(node, log, "command-output" if ok else "command-error", ok)
            payload: dict[str, Any] = {"exit_code": returncode}
            if handler_command and not flow_command:
                payload["handler"] = "consumer"
            emit("node.completed", node=node_id, severity="info" if ok else "error", payload=payload)
            if not ok and on_failure.get("action") not in ("skip", "escalate"):
                status = "failed"
        elif node_type == "intake":
            emit_produces(node, json.dumps({"inputs": inputs, "params": param_values}, indent=2), "json", True)
            emit("node.completed", node=node_id)
        elif node_type in ("plan", "decision", "verifier", "finalizer"):
            body = f"# {node['title']}\n\n{node.get('instructions', node['description'])}\n"
            emit_produces(node, body, "markdown", True)
            emit("node.completed", node=node_id)
        else:  # agent_task / approval / handoff without a local command
            needs_handler.append(node_id)
            emit("node.completed", node=node_id, severity="warning", payload={"status": "needs-handler"})
            status = "incomplete" if status == "completed" else status

    required_gates = [g for g in document.get("quality_gates", []) if g.get("required")]
    for gate in required_gates:
        refs = gate.get("evidence_refs", [])
        if refs and all(r in artifacts and artifact_ok.get(r) for r in refs):
            evidence = [artifacts[r] for r in refs]
            emit("gate.completed", node=produced_by_node.get(refs[0]),
                 payload={"gate_id": gate["id"], "status": "passed"}, evidence=evidence)
        elif status == "completed":
            status = "incomplete"

    required_outputs = [f["id"] for f in document.get("contracts", {}).get("outputs", []) if f.get("required")]
    if any(o not in outputs for o in required_outputs) and status == "completed":
        status = "incomplete"

    bundle_status = "completed" if status == "completed" else "failed"
    if bundle_status == "completed":
        emit("flow.completed")

    bundle = {
        "run_version": "agentic-flows.run/v1",
        "flow": {"id": flow_id, "version": flow_version, "source": flow_source},
        "run": {
            "id": run_id, "core": core, "status": bundle_status,
            "started_at": start_at, "completed_at": now(),
        },
        "inputs": inputs,
        "outputs": outputs,
        "artifacts": list(artifacts.values()),
        "events": events,
    }
    return bundle, status, needs_handler


def cmd_run(args: argparse.Namespace) -> int:
    flow_schema = load_json(args.schema)
    if not args.flow.exists():
        print(f"FAIL {args.flow}: flow file does not exist", file=sys.stderr)
        return 1
    document = load_yaml(args.flow)
    errors = validate_flow_document(document, flow_schema)
    if errors:
        print(f"FAIL {args.flow}", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    try:
        inputs = parse_kv_list(args.input)
        params = parse_kv_list(args.param)
        handlers = parse_kv_list(args.handler)
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    node_ids = {node["id"] for node in document["nodes"]}
    unknown_handlers = sorted(node_id for node_id in handlers if node_id not in node_ids)
    if unknown_handlers:
        print(f"FAIL: handler targets unknown node(s): {', '.join(unknown_handlers)}", file=sys.stderr)
        return 1

    if args.plan:
        plan = plan_flow(document, handlers)
        print(f"Plan for {document['id']}@{document['version']}")
        width = max((len(step["id"]) for step in plan["steps"]), default=0)
        for index, step in enumerate(plan["steps"], start=1):
            note = "  <- consumer must bind" if step["disposition"] == "needs-handler" else ""
            print(f"  {index}. {step['id']:<{width}}  [{step['disposition']}] {step['type']}{note}")
        surface = plan["needs_handlers"]
        print(f"Consumer must bind: {', '.join(surface) if surface else 'nothing (runnable as-is)'}")
        return 0

    workdir = Path(args.workdir).resolve() if args.workdir else Path.cwd()
    flow_path = args.flow.resolve()
    source = str(flow_path.relative_to(REPO_ROOT)) if flow_path.is_relative_to(REPO_ROOT) else str(flow_path)
    out_dir = (Path(args.out) if args.out else REPO_ROOT / ".agentic-runs" / re.sub(r"[^a-z0-9]+", "-", document["id"])).resolve()

    bundle, status, needs_handler = run_flow(document, source, inputs, params, workdir, out_dir, handlers, args.simulate)
    bundle_path = out_dir / f"{bundle['run']['id']}.run.json"
    bundle_path.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")

    run_schema = load_json(args.run_schema)
    event_schema = load_json(args.event_schema)
    validation_errors = validate_run_document(bundle, run_schema, event_schema, flow_schema, run_path=bundle_path)

    print(f"Run {bundle['run']['id']} ({bundle['run']['status']})")
    print(f"Flow: {document['id']}@{document['version']}  Out: {display_path(bundle_path)}")
    passed = [e["payload"]["gate_id"] for e in bundle["events"] if e["event"] == "gate.completed"]
    print(f"Gates passed: {', '.join(passed) if passed else 'none'}")
    print(f"Outputs: {', '.join(sorted(bundle['outputs'])) if bundle['outputs'] else 'none'}")
    if needs_handler:
        print(f"Needs consumer handler: {', '.join(needs_handler)}")
    if validation_errors:
        print("Produced run bundle failed validation:", file=sys.stderr)
        for error in validation_errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    return 0 if bundle["run"]["status"] == "completed" else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="flowctl", description="Validate and inspect agentic flow definitions.")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA, help="Path to the flow JSON Schema.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validate flow.yaml files.")
    validate.add_argument("paths", nargs="*", type=Path, help="Flow files or directories. Defaults to flows/ and templates/.")
    validate.add_argument("-v", "--verbose", action="store_true", help="Print each passing file.")
    validate.set_defaults(func=cmd_validate)

    run = subparsers.add_parser("run", help="Execute a runnable flow with local handlers and emit a real run bundle.")
    run.add_argument("flow", type=Path, help="Path to flow.yaml.")
    run.add_argument("--input", action="append", default=[], metavar="id=value", help="Flow input value.")
    run.add_argument("--param", action="append", default=[], metavar="id=value", help="Parameter override.")
    run.add_argument("--handler", action="append", default=[], metavar="node_id=command",
                     help="Bind a node that needs a consumer handler (agent_task/approval/handoff, or a tool without a command) to a command.")
    run.add_argument("--plan", action="store_true",
                     help="Print the execution order and the consumer handler surface without running anything.")
    run.add_argument("--simulate", action="store_true",
                     help="Wiring check: assume every working/agent step succeeds and verify gates and required outputs, without running commands.")
    run.add_argument("--workdir", type=Path, help="Working directory for command nodes. Defaults to the current directory.")
    run.add_argument("--out", type=Path, help="Output directory for the run bundle and artifacts. Defaults to .agentic-runs/<flow>.")
    run.add_argument("--run-schema", type=Path, default=DEFAULT_RUN_SCHEMA, help="Path to the run bundle JSON Schema.")
    run.add_argument("--event-schema", type=Path, default=DEFAULT_EVENT_SCHEMA, help="Path to the event JSON Schema.")
    run.set_defaults(func=cmd_run)

    validate_adapter = subparsers.add_parser("validate-adapter-smoke", help="Validate adapter smoke manifests.")
    validate_adapter.add_argument("paths", nargs="*", type=Path, help="Adapter smoke files or directories. Defaults to examples/adapters/.")
    validate_adapter.add_argument("--adapter-schema", type=Path, default=DEFAULT_ADAPTER_SMOKE_SCHEMA, help="Path to the adapter smoke JSON Schema.")
    validate_adapter.add_argument("--run-schema", type=Path, default=DEFAULT_RUN_SCHEMA, help="Path to the run bundle JSON Schema.")
    validate_adapter.add_argument("--event-schema", type=Path, default=DEFAULT_EVENT_SCHEMA, help="Path to the event JSON Schema.")
    validate_adapter.add_argument("--stream-schema", type=Path, default=DEFAULT_EVENT_STREAM_SCHEMA, help="Path to the event stream JSON Schema.")
    validate_adapter.add_argument("-v", "--verbose", action="store_true", help="Print each passing file.")
    validate_adapter.set_defaults(func=cmd_validate_adapter_smoke)

    normalize = subparsers.add_parser("normalize", help="Check or rewrite flow.yaml files into canonical YAML order.")
    normalize.add_argument("paths", nargs="*", type=Path, help="Flow files or directories. Defaults to flows/ and templates/.")
    normalize.add_argument("--write", action="store_true", help="Rewrite files instead of checking them.")
    normalize.add_argument("-v", "--verbose", action="store_true", help="Print each passing or written file.")
    normalize.set_defaults(func=cmd_normalize)

    validate_event = subparsers.add_parser("validate-event", help="Validate event JSON files.")
    validate_event.add_argument("paths", nargs="*", type=Path, help="Event files or directories. Defaults to examples/.")
    validate_event.add_argument("--event-schema", type=Path, default=DEFAULT_EVENT_SCHEMA, help="Path to the event JSON Schema.")
    validate_event.add_argument("-v", "--verbose", action="store_true", help="Print each passing file.")
    validate_event.set_defaults(func=cmd_validate_event)

    validate_stream = subparsers.add_parser("validate-stream", help="Validate multi-file event stream manifests.")
    validate_stream.add_argument("paths", nargs="*", type=Path, help="Stream files or directories. Defaults to examples/streams/.")
    validate_stream.add_argument("--stream-schema", type=Path, default=DEFAULT_EVENT_STREAM_SCHEMA, help="Path to the event stream JSON Schema.")
    validate_stream.add_argument("--event-schema", type=Path, default=DEFAULT_EVENT_SCHEMA, help="Path to the event JSON Schema.")
    validate_stream.add_argument("-v", "--verbose", action="store_true", help="Print each passing file.")
    validate_stream.set_defaults(func=cmd_validate_stream)

    validate_run = subparsers.add_parser("validate-run", help="Validate completed run bundle JSON files.")
    validate_run.add_argument("paths", nargs="*", type=Path, help="Run bundle files or directories. Defaults to examples/runs/.")
    validate_run.add_argument("--run-schema", type=Path, default=DEFAULT_RUN_SCHEMA, help="Path to the run bundle JSON Schema.")
    validate_run.add_argument("--event-schema", type=Path, default=DEFAULT_EVENT_SCHEMA, help="Path to the event JSON Schema.")
    validate_run.add_argument("-v", "--verbose", action="store_true", help="Print each passing file.")
    validate_run.set_defaults(func=cmd_validate_run)

    replay = subparsers.add_parser("replay", help="Validate and replay run bundle timelines.")
    replay.add_argument("paths", nargs="*", type=Path, help="Run bundle files or directories. Defaults to examples/runs/.")
    replay.add_argument("--run-schema", type=Path, default=DEFAULT_RUN_SCHEMA, help="Path to the run bundle JSON Schema.")
    replay.add_argument("--event-schema", type=Path, default=DEFAULT_EVENT_SCHEMA, help="Path to the event JSON Schema.")
    replay.add_argument("--json", action="store_true", help="Emit replay summaries as JSON.")
    replay.set_defaults(func=cmd_replay)

    validate_samples = subparsers.add_parser("validate-samples", help="Validate flow sample input/output JSON files.")
    validate_samples.add_argument("paths", nargs="*", type=Path, help="Sample files or directories. Defaults to examples/samples/.")
    validate_samples.add_argument("--sample-schema", type=Path, default=DEFAULT_SAMPLE_SCHEMA, help="Path to the sample JSON Schema.")
    validate_samples.add_argument("-v", "--verbose", action="store_true", help="Print each passing file.")
    validate_samples.set_defaults(func=cmd_validate_samples)

    changelog_check = subparsers.add_parser("changelog-check", help="Validate changelog structure.")
    changelog_check.add_argument("--changelog", type=Path, default=REPO_ROOT / "CHANGELOG.md", help="Path to CHANGELOG.md.")
    changelog_check.add_argument("--release", help="Require a dated release heading for this version.")
    changelog_check.set_defaults(func=cmd_changelog_check)

    check_links = subparsers.add_parser("check-links", help="Validate local Markdown links.")
    check_links.add_argument("paths", nargs="*", type=Path, help="Markdown files or directories. Defaults to repo docs surfaces.")
    check_links.add_argument("-v", "--verbose", action="store_true", help="Print each passing file.")
    check_links.set_defaults(func=cmd_check_links)

    package_release = subparsers.add_parser("package-release", help="Build a deterministic release package zip.")
    package_release.add_argument("--output", type=Path, required=True, help="Output zip path.")
    package_release.add_argument("paths", nargs="*", type=Path, help="Files or directories to include. Defaults to release package contents.")
    package_release.set_defaults(func=cmd_package_release)

    release_check = subparsers.add_parser("release-check", help="Validate pre-tag release readiness rules.")
    release_check.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Flow files or directories. Defaults to flows/ and templates/.",
    )
    release_check.add_argument(
        "--adapter-schema",
        type=Path,
        default=DEFAULT_ADAPTER_SMOKE_SCHEMA,
        help="Path to the adapter smoke JSON Schema.",
    )
    release_check.add_argument(
        "--run-schema",
        type=Path,
        default=DEFAULT_RUN_SCHEMA,
        help="Path to the run bundle JSON Schema.",
    )
    release_check.add_argument(
        "--event-schema",
        type=Path,
        default=DEFAULT_EVENT_SCHEMA,
        help="Path to the event JSON Schema.",
    )
    release_check.add_argument(
        "--stream-schema",
        type=Path,
        default=DEFAULT_EVENT_STREAM_SCHEMA,
        help="Path to the event stream JSON Schema.",
    )
    release_check.add_argument(
        "--sample-schema",
        type=Path,
        default=DEFAULT_SAMPLE_SCHEMA,
        help="Path to the sample JSON Schema.",
    )
    release_check.set_defaults(func=cmd_release_check)

    check_composition = subparsers.add_parser(
        "check-composition",
        help="Validate flow_ref sub-flow composition (resolution, bindings, cycles, capabilities) against the catalog.",
    )
    check_composition.add_argument("paths", nargs="*", type=Path, help="Flow files or directories. Defaults to flows/ and templates/.")
    check_composition.add_argument("-v", "--verbose", action="store_true", help="Print each passing composing file.")
    check_composition.set_defaults(func=cmd_check_composition)

    list_cmd = subparsers.add_parser("list", help="List valid flow definitions.")
    list_cmd.add_argument("paths", nargs="*", type=Path, help="Flow files or directories. Defaults to flows/ and templates/.")
    list_cmd.add_argument("--json", action="store_true", help="Print JSON output.")
    list_cmd.set_defaults(func=cmd_list)

    report = subparsers.add_parser("report", help="Summarize flow catalog maturity and compatibility.")
    report.add_argument("paths", nargs="*", type=Path, help="Flow files or directories. Defaults to flows/ and templates/.")
    report.add_argument("--json", action="store_true", help="Print JSON output.")
    report.set_defaults(func=cmd_report)

    graph = subparsers.add_parser("graph", help="Export a flow graph.")
    graph.add_argument("flow", type=Path, help="Path to flow.yaml.")
    graph.add_argument("--format", choices=("json", "dot"), default="json")
    graph.add_argument("--output", type=Path, help="Write output to a file.")
    graph.set_defaults(func=cmd_graph)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
