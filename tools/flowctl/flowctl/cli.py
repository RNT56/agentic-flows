from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised by users without deps
    raise SystemExit("PyYAML is required. Install with: python -m pip install -e .") from exc

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError as exc:  # pragma: no cover - exercised by users without deps
    raise SystemExit("jsonschema is required. Install with: python -m pip install -e .") from exc


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SCHEMA = REPO_ROOT / "schemas" / "flow.schema.json"
DEFAULT_EVENT_SCHEMA = REPO_ROOT / "schemas" / "event.schema.json"
DEFAULT_RUN_SCHEMA = REPO_ROOT / "schemas" / "run.schema.json"
DEFAULT_SEARCH_ROOTS = [REPO_ROOT / "flows", REPO_ROOT / "templates"]
DEFAULT_EVENT_SEARCH_ROOTS = [REPO_ROOT / "examples"]
DEFAULT_RUN_SEARCH_ROOTS = [REPO_ROOT / "examples" / "runs"]


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


def find_json_files(paths: Iterable[Path]) -> list[Path]:
    selected = list(paths)
    if not selected:
        selected = DEFAULT_EVENT_SEARCH_ROOTS

    files: list[Path] = []
    for path in selected:
        path = path.resolve()
        if path.is_file():
            if not path.name.endswith(".run.json"):
                files.append(path)
            continue
        if not path.exists():
            files.append(path)
            continue
        files.extend(path for path in sorted(path.rglob("*.json")) if not path.name.endswith(".run.json"))

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


def format_error_path(parts: Iterable[Any]) -> str:
    path = "$"
    for part in parts:
        if isinstance(part, int):
            path += f"[{part}]"
        else:
            path += f".{part}"
    return path


def validate_flow_document(document: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = [
        f"{format_error_path(error.path)}: {error.message}"
        for error in sorted(validator.iter_errors(document), key=lambda err: list(err.path))
    ]
    errors.extend(validate_semantics(document))
    return errors


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

    return errors


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
                if not event.get("evidence"):
                    errors.append(f"$.events[{index}].evidence: passed required gates need evidence")

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


def parse_rfc3339(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def is_rfc3339_datetime(value: str) -> bool:
    return parse_rfc3339(value) is not None


def validate_semantics(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    nodes = document.get("nodes", [])
    if not isinstance(nodes, list):
        return errors

    node_ids: list[str] = []
    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            continue
        node_id = node.get("id")
        if isinstance(node_id, str):
            node_ids.append(node_id)
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

    return errors


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
        if path.parts[-3:-1] and "flows" in path.parts and not readme_path.exists():
            issues.append("$.readme: reusable flows require a sibling README.md")
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="flowctl", description="Validate and inspect agentic flow definitions.")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA, help="Path to the flow JSON Schema.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validate flow.yaml files.")
    validate.add_argument("paths", nargs="*", type=Path, help="Flow files or directories. Defaults to flows/ and templates/.")
    validate.add_argument("-v", "--verbose", action="store_true", help="Print each passing file.")
    validate.set_defaults(func=cmd_validate)

    validate_event = subparsers.add_parser("validate-event", help="Validate event JSON files.")
    validate_event.add_argument("paths", nargs="*", type=Path, help="Event files or directories. Defaults to examples/.")
    validate_event.add_argument("--event-schema", type=Path, default=DEFAULT_EVENT_SCHEMA, help="Path to the event JSON Schema.")
    validate_event.add_argument("-v", "--verbose", action="store_true", help="Print each passing file.")
    validate_event.set_defaults(func=cmd_validate_event)

    validate_run = subparsers.add_parser("validate-run", help="Validate completed run bundle JSON files.")
    validate_run.add_argument("paths", nargs="*", type=Path, help="Run bundle files or directories. Defaults to examples/runs/.")
    validate_run.add_argument("--run-schema", type=Path, default=DEFAULT_RUN_SCHEMA, help="Path to the run bundle JSON Schema.")
    validate_run.add_argument("--event-schema", type=Path, default=DEFAULT_EVENT_SCHEMA, help="Path to the event JSON Schema.")
    validate_run.add_argument("-v", "--verbose", action="store_true", help="Print each passing file.")
    validate_run.set_defaults(func=cmd_validate_run)

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
