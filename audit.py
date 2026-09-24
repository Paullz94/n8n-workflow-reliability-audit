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
    "httpRequest",
)
IDEMPOTENCY_MARKERS = ("dedup", "idempoten", "duplicate", "already processed")
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


def _is_trigger(node: dict[str, Any]) -> bool:
    node_type = _node_type(node)
    return any(marker in node_type for marker in TRIGGER_MARKERS)


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
    names = [str(node.get("name", "")).strip() for node in named_nodes]
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

    nodes_without_id = [str(node.get("name", "<unnamed>")) for node in named_nodes if not isinstance(node.get("id"), str) or not node.get("id", "").strip()]
    if nodes_without_id:
        findings.append(Finding(
            "STRUCT-005", "high", "Nodes missing identifiers", None,
            f"Missing node `id`: {', '.join(nodes_without_id)}.",
            "Assign stable unique node IDs or regenerate the export from n8n before import/handoff.",
        ))

    connections = workflow.get("connections", {})
    adjacency = _connection_targets(connections)
    incoming: dict[str, int] = {name: 0 for name in names if name}
    for targets in adjacency.values():
        for target in targets:
            incoming[target] = incoming.get(target, 0) + 1
    roots = {str(node.get("name")) for node in named_nodes if _is_trigger(node)}
    if not roots:
        roots = {name for name, count in incoming.items() if count == 0}
    reachable = _reachable(adjacency, roots)
    disconnected = sorted(set(incoming) - reachable)
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

    has_side_effect = False
    has_idempotency_signal = False
    for node in named_nodes:
        name = str(node.get("name", "")) or "<unnamed>"
        node_type = _node_type(node)
        params = node.get("parameters") if isinstance(node.get("parameters"), dict) else {}
        combined_identity = f"{name} {node_type}".lower()

        if any(marker in combined_identity for marker in IDEMPOTENCY_MARKERS):
            has_idempotency_signal = True
        if any(marker.lower() in node_type for marker in SIDE_EFFECT_MARKERS):
            has_side_effect = True

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

    if active and roots and has_side_effect and not has_idempotency_signal:
        findings.append(Finding(
            "DATA-001", "high", "No visible duplicate-prevention step", None,
            "An active trigger reaches side-effect-capable nodes, but no node name/type signals deduplication or idempotency.",
            "Define an idempotency key, persist processed-event state, and test repeated delivery. This heuristic requires human confirmation.",
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
        "schema_version": 1,
        "workflow": {
            "name": str(workflow.get("name", "Unnamed workflow")),
            "active": active,
            "node_count": len(named_nodes),
            "connection_source_count": len(adjacency),
        },
        "scope": "Static export review only; execution, credentials, instance configuration, and business correctness remain unverified.",
        "summary": {severity: counts.get(severity, 0) for severity in SEVERITY_ORDER},
        "findings": [asdict(finding) for finding in findings],
    }


def render_markdown(result: dict[str, Any]) -> str:
    workflow = result["workflow"]
    summary = result["summary"]
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
        "## Findings",
        "",
    ]
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


if __name__ == "__main__":
    main()
