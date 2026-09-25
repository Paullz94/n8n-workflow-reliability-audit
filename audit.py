"""Deterministic, credential-free checks for exported n8n workflow JSON.

This is a portfolio/validation artifact for the Workflow Reliability Retrofit
service. It deliberately performs static checks only and never claims that a
workflow is production-safe without execution tests and human review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict, deque
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
TRIGGER_MARKERS = ("trigger", "webhook")
RISKY_NODE_MARKERS = ("executecommand", "readwritefile", "ssh", "code")
SIDE_EFFECT_MARKERS = (
    "airtable",
    "googlesheets",
    "postgres",
    "mysql",
    "microsoftsql",
    "slack",
    "gmail",
    "sendemail",
)
SAFE_HTTP_METHODS = {"GET", "HEAD", "OPTIONS"}
IDEMPOTENCY_GUARD_MARKERS = (
    "dedup",
    "duplicate",
    "already processed",
    "processed event",
    "idempotency guard",
    "idempotency check",
    "replay guard",
)
SECRET_KEY = re.compile(r"(?i)(api[_-]?key|password|passwd|secret|authorization|bearer|token)")
SECRET_VALUE = re.compile(r"(?i)(bearer\s+[a-z0-9._-]{12,}|sk-[a-z0-9_-]{12,})")


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    title: str
    node: str | None
    evidence: str
    recommendation: str


def _iter_values(value: Any, path: str = "parameters") -> Iterable[tuple[str, str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            yield child_path, str(key), child
            yield from _iter_values(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _iter_values(child, f"{path}[{index}]")


def _node_type(node: dict[str, Any]) -> str:
    return str(node.get("type", "")).lower()


def _node_name(node: dict[str, Any]) -> str:
    return str(node.get("name", "")).strip()


def _is_trigger(node: dict[str, Any]) -> bool:
    node_type = _node_type(node)
    return any(marker in node_type for marker in TRIGGER_MARKERS)


def _http_method(node: dict[str, Any]) -> str:
    params = node.get("parameters") if isinstance(node.get("parameters"), dict) else {}
    return str(params.get("method", "GET")).upper()


def _is_side_effect_node(node: dict[str, Any]) -> bool:
    node_type = _node_type(node)
    if "httprequest" in node_type:
        return _http_method(node) not in SAFE_HTTP_METHODS
    return any(marker in node_type for marker in SIDE_EFFECT_MARKERS)


def _is_idempotency_guard(node: dict[str, Any]) -> bool:
    identity = f"{_node_name(node)} {_node_type(node)}".lower()
    return any(marker in identity for marker in IDEMPOTENCY_GUARD_MARKERS)


def _connection_targets(connections: Any) -> dict[str, set[str]]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    if not isinstance(connections, dict):
        return adjacency
    for source, outputs in connections.items():
        if not isinstance(outputs, dict):
            continue
        for channel_groups in outputs.values():
            if not isinstance(channel_groups, list):
                continue
            for group in channel_groups:
                if not isinstance(group, list):
                    continue
                for edge in group:
                    if isinstance(edge, dict) and isinstance(edge.get("node"), str):
                        adjacency[str(source)].add(edge["node"])
    return adjacency


def _reachable(adjacency: dict[str, set[str]], roots: set[str]) -> set[str]:
    seen: set[str] = set()
    queue = deque(roots)
    while queue:
        current = queue.popleft()
        if current in seen:
            continue
        seen.add(current)
        queue.extend(adjacency.get(current, set()) - seen)
    return seen


def _unguarded_side_effects(
    node_by_name: dict[str, dict[str, Any]],
    adjacency: dict[str, set[str]],
    roots: set[str],
) -> set[str]:
    """Return reachable side-effect nodes that have at least one unguarded path.

    This is intentionally conservative. A guard is recognized only by explicit
    deduplication/replay-prevention naming, and a side effect remains unguarded
    when any reachable path can reach it before such a guard.
    """
    unguarded: set[str] = set()
    queue = deque((root, False) for root in roots if root in node_by_name)
    seen: set[tuple[str, bool]] = set()

    while queue:
        current, guard_seen = queue.popleft()
        state = (current, guard_seen)
        if state in seen:
            continue
        seen.add(state)

        node = node_by_name.get(current)
        if node is None:
            continue

        guarded_here = guard_seen or _is_idempotency_guard(node)
        if _is_side_effect_node(node) and not guarded_here:
            unguarded.add(current)

        for target in adjacency.get(current, set()):
            if target in node_by_name:
                queue.append((target, guarded_here))

    return unguarded


def failure_threshold_met(result: dict[str, Any], threshold: str) -> bool:
    """Return True when result contains a finding at or above threshold."""
    if threshold == "none":
        return False
    limit = SEVERITY_ORDER[threshold]
    return any(
        SEVERITY_ORDER.get(str(item.get("severity")), len(SEVERITY_ORDER)) <= limit
        for item in result.get("findings", [])
        if isinstance(item, dict)
    )


def audit_workflow(workflow: dict[str, Any]) -> dict[str, Any]:
    """Return a redacted static audit result for one exported workflow."""
    findings: list[Finding] = []
    if not isinstance(workflow.get("id"), str) or not workflow.get("id", "").strip():
        findings.append(Finding(
            "STRUCT-004", "critical", "Missing workflow identifier", None,
            "The export has no non-empty string `id`; current n8n imports require one.",
            "Use an actual n8n export or assign a unique workflow ID before import.",
        ))

    nodes = workflow.get("nodes")
    if not isinstance(nodes, list):
        nodes = []
        findings.append(Finding(
            "STRUCT-001", "critical", "Missing node list", None,
            "The workflow export has no valid `nodes` array.",
            "Export the workflow again and verify the JSON before review.",
        ))

    named_nodes = [node for node in nodes if isinstance(node, dict)]
    names = [_node_name(node) for node in named_nodes]
    valid_names = {name for name in names if name}
    node_by_name = {_node_name(node): node for node in named_nodes if _node_name(node)}

    duplicate_names = sorted(name for name, count in Counter(names).items() if name and count > 1)
    if duplicate_names:
        findings.append(Finding(
            "STRUCT-002", "high", "Duplicate node names", None,
            f"Duplicate names: {', '.join(duplicate_names)}.",
            "Use unique node names so expressions, connections, and incident reports are unambiguous.",
        ))

    unnamed_count = sum(not name for name in names)
    if unnamed_count:
        findings.append(Finding(
            "STRUCT-003", "high", "Unnamed nodes", None,
            f"{unnamed_count} node(s) have no usable name.",
            "Name every node before handoff.",
        ))

    nodes_without_id = [
        _node_name(node) or "<unnamed>"
        for node in named_nodes
        if not isinstance(node.get("id"), str) or not node.get("id", "").strip()
    ]
    if nodes_without_id:
        findings.append(Finding(
            "STRUCT-005", "high", "Nodes missing identifiers", None,
            f"Missing node `id`: {', '.join(nodes_without_id)}.",
            "Assign stable unique node IDs or regenerate the export from n8n before import/handoff.",
        ))

    connections = workflow.get("connections", {})
    adjacency = _connection_targets(connections)

    missing_sources = sorted(source for source in adjacency if source not in valid_names)
    if missing_sources:
        findings.append(Finding(
            "GRAPH-002", "high", "Connections reference missing source nodes", None,
            f"Unknown connection source(s): {', '.join(missing_sources)}.",
            "Regenerate the export or remove stale connection entries before import/handoff.",
        ))

    missing_targets = sorted({
        target
        for targets in adjacency.values()
        for target in targets
        if target not in valid_names
    })
    if missing_targets:
        findings.append(Finding(
            "GRAPH-003", "high", "Connections reference missing target nodes", None,
            f"Unknown connection target(s): {', '.join(missing_targets)}.",
            "Regenerate the export or reconnect the affected branch to an existing node.",
        ))

    incoming: dict[str, int] = {name: 0 for name in valid_names}
    for targets in adjacency.values():
        for target in targets:
            if target in incoming:
                incoming[target] += 1

    roots = {_node_name(node) for node in named_nodes if _is_trigger(node) and _node_name(node)}
    if not roots:
        roots = {name for name, count in incoming.items() if count == 0}

    reachable = _reachable(adjacency, roots)
    disconnected = sorted(valid_names - reachable)
    if disconnected:
        findings.append(Finding(
            "GRAPH-001", "high", "Unreachable nodes", None,
            f"Not reachable from a trigger/root: {', '.join(disconnected)}.",
            "Remove stale nodes or connect them deliberately, then exercise every branch.",
        ))

    settings = workflow.get("settings") if isinstance(workflow.get("settings"), dict) else {}
    active = bool(workflow.get("active"))
    if active and not settings.get("errorWorkflow"):
        findings.append(Finding(
            "RECOVERY-001", "high", "No workflow-level error workflow", None,
            "The workflow is active but `settings.errorWorkflow` is not configured.",
            "Attach an error workflow that records context and alerts an operator without exposing payload secrets.",
        ))

    for node in named_nodes:
        name = _node_name(node) or "<unnamed>"
        node_type = _node_type(node)
        params = node.get("parameters") if isinstance(node.get("parameters"), dict) else {}

        if "webhook" in node_type:
            authentication = str(params.get("authentication", "none")).lower()
            if authentication in {"", "none"}:
                findings.append(Finding(
                    "SEC-001", "high", "Unauthenticated webhook", name,
                    "Webhook authentication is absent or set to none.",
                    "Require an appropriate authentication/signature check, rate limit the endpoint, and reject replayed requests.",
                ))

        if "httprequest" in node_type:
            options = params.get("options") if isinstance(params.get("options"), dict) else {}
            if not node.get("retryOnFail"):
                findings.append(Finding(
                    "RECOVERY-002", "medium", "HTTP call has no node retry policy", name,
                    "`retryOnFail` is not enabled.",
                    "Add bounded retries with backoff only for retry-safe failures; protect writes with idempotency.",
                ))
            if not options.get("timeout"):
                findings.append(Finding(
                    "RECOVERY-003", "medium", "HTTP call has no explicit timeout", name,
                    "No `parameters.options.timeout` value is present.",
                    "Set a finite timeout and route exhausted failures to an observable recovery path.",
                ))

        on_error = str(node.get("onError", "stopWorkflow"))
        if node.get("continueOnFail") is True or on_error not in {"", "stopWorkflow"}:
            mode = "legacy continueOnFail=true" if node.get("continueOnFail") is True else f"onError={on_error}"
            findings.append(Finding(
                "RECOVERY-004", "medium", "Node may convert a failure into a successful execution", name,
                f"The node uses `{mode}`.",
                "Confirm the continuation branch handles and surfaces the failure. A workflow-level Error Trigger runs only when the execution actually ends in error.",
            ))

        if node.get("disabled") is True:
            findings.append(Finding(
                "OPS-002", "medium", "Disabled node remains in workflow graph", name,
                "The exported node has `disabled=true`.",
                "Confirm this is intentional and test the effective connection path; remove stale disabled nodes before handoff.",
            ))

        if any(marker in node_type for marker in RISKY_NODE_MARKERS):
            findings.append(Finding(
                "SEC-002", "medium", "Powerful node requires manual review", name,
                f"Node type `{node.get('type', '')}` can execute code, commands, SSH, or file operations.",
                "Review inputs, escaping, permissions, network/file access, and secret exposure; sandbox where possible.",
            ))

        for path, key, value in _iter_values(params):
            if isinstance(value, str) and value.startswith("={{"):
                continue
            key_suspicious = bool(SECRET_KEY.search(key))
            value_suspicious = isinstance(value, str) and bool(SECRET_VALUE.search(value))
            if (key_suspicious and value not in (None, "", "={{...}}")) or value_suspicious:
                findings.append(Finding(
                    "SEC-003", "critical", "Possible hard-coded secret", name,
                    f"A credential-like value is present at `{path}` (value redacted).",
                    "Remove it from node parameters, rotate if real, and use n8n credentials or an external secret store.",
                ))

    side_effect_nodes = sorted(
        name for name, node in node_by_name.items()
        if name in reachable and _is_side_effect_node(node)
    )
    unguarded_side_effects = sorted(_unguarded_side_effects(node_by_name, adjacency, roots))

    if active and roots and unguarded_side_effects:
        findings.append(Finding(
            "DATA-001", "high", "Side effects are reachable without a visible duplicate-prevention guard", None,
            f"At least one trigger/root path reaches these side-effect node(s) before an explicit deduplication/replay guard: {', '.join(unguarded_side_effects)}.",
            "Persist an idempotency key or processed-event marker before the side effect and test duplicate delivery. This graph heuristic requires human confirmation.",
        ))

    retrying_unguarded_writes = sorted(
        name
        for name in unguarded_side_effects
        if "httprequest" in _node_type(node_by_name[name])
        and _http_method(node_by_name[name]) not in SAFE_HTTP_METHODS
        and node_by_name[name].get("retryOnFail") is True
    )
    if active and retrying_unguarded_writes:
        findings.append(Finding(
            "DATA-002", "high", "Retrying HTTP writes lack a visible upstream idempotency guard", None,
            f"Retry-enabled mutating HTTP node(s) reachable without a guard: {', '.join(retrying_unguarded_writes)}.",
            "Use a stable idempotency key accepted by the destination or persist deduplication state before retrying the write; verify repeated-delivery behavior synthetically.",
        ))

    if active and not workflow.get("versionId"):
        findings.append(Finding(
            "OPS-001", "low", "No exported version identifier", None,
            "The active workflow has no `versionId` in this export.",
            "Record the exact source version and keep before/after exports for rollback.",
        ))

    findings.sort(key=lambda item: (SEVERITY_ORDER[item.severity], item.rule_id, item.node or ""))
    counts = Counter(finding.severity for finding in findings)
    return {
        "tool": "Workflow Reliability Audit",
        "schema_version": 2,
        "workflow": {
            "name": str(workflow.get("name", "Unnamed workflow")),
            "active": active,
            "node_count": len(named_nodes),
            "connection_source_count": len(adjacency),
        },
        "analysis": {
            "root_nodes": sorted(roots),
            "reachable_node_count": len(valid_names & reachable),
            "side_effect_nodes": side_effect_nodes,
            "unguarded_side_effect_nodes": unguarded_side_effects,
        },
        "scope": "Static export review only; execution, credentials, instance configuration, and business correctness remain unverified.",
        "summary": {severity: counts.get(severity, 0) for severity in SEVERITY_ORDER},
        "findings": [asdict(finding) for finding in findings],
    }


def render_markdown(result: dict[str, Any]) -> str:
    workflow = result["workflow"]
    summary = result["summary"]
    analysis = result.get("analysis", {})
    lines = [
        f"# Workflow Reliability Audit — {workflow['name']}",
        "",
        f"- Active: {workflow['active']}",
        f"- Nodes: {workflow['node_count']}",
        f"- Input SHA-256: `{result.get('input_sha256', 'not-recorded')}`",
        f"- Scope: {result['scope']}",
        "- Secrets: values are never printed in this report",
        "",
        "## Summary",
        "",
        "| Critical | High | Medium | Low | Info |",
        "|---:|---:|---:|---:|---:|",
        f"| {summary['critical']} | {summary['high']} | {summary['medium']} | {summary['low']} | {summary['info']} |",
        "",
    ]
    if analysis:
        side_effects = analysis.get("side_effect_nodes", [])
        unguarded = analysis.get("unguarded_side_effect_nodes", [])
        lines.extend([
            "## Graph-aware reliability signals",
            "",
            f"- Reachable side-effect nodes: {len(side_effects)}",
            f"- Side-effect nodes with at least one unguarded path: {len(unguarded)}",
            "",
        ])

    lines.extend(["## Findings", ""])
    if not result["findings"]:
        lines.extend(["No static findings. This does not prove production readiness.", ""])
    for finding in result["findings"]:
        location = f" — `{finding['node']}`" if finding["node"] else ""
        lines.extend([
            f"### {finding['severity'].upper()} {finding['rule_id']}: {finding['title']}{location}",
            "",
            f"Evidence: {finding['evidence']}",
            "",
            f"Recommendation: {finding['recommendation']}",
            "",
        ])
    lines.extend([
        "## Required dynamic evidence before release",
        "",
        "- Re-run defined synthetic happy-path, malformed-input, duplicate-delivery, timeout, rate-limit, and partial-failure cases.",
        "- Independently verify outputs and side effects, not only successful execution status.",
        "- Confirm credential scopes, webhook authentication, instance security audit, logging redaction, and rollback.",
        "- Do not use production personal data or plaintext credentials in the review package.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit an exported n8n workflow JSON file.")
    parser.add_argument("workflow", type=Path)
    parser.add_argument("--output", type=Path, help="Write a Markdown report.")
    parser.add_argument("--json-output", type=Path, help="Write a machine-readable report.")
    parser.add_argument(
        "--fail-on",
        choices=("none", *SEVERITY_ORDER.keys()),
        default="none",
        help="Exit with status 1 when a finding at or above this severity exists.",
    )
    args = parser.parse_args()

    raw = args.workflow.read_bytes()
    workflow = json.loads(raw.decode("utf-8"))
    result = audit_workflow(workflow)
    result["input_sha256"] = hashlib.sha256(raw).hexdigest()
    markdown = render_markdown(result)
    if args.output:
        args.output.write_text(markdown, encoding="utf-8")
    else:
        print(markdown)
    if args.json_output:
        args.json_output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if failure_threshold_met(result, args.fail_on):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
