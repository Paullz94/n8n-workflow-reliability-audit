#!/usr/bin/env python3
"""Static reliability audit for exported Make.com scenario blueprints.

Designed for Project Northstar Ledger's zero-owner-capital validation wedge.
It never contacts Make or third-party services; it inspects local JSON only.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

SEVERITY_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
WRITE_ACTIONS = ("create", "update", "delete", "remove", "send", "post", "put", "patch", "upload", "insert", "add", "write", "set")
SECRET_PATTERNS = [
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{16,}", re.I),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"https://hooks\.slack\.com/services/[A-Za-z0-9/_-]+", re.I),
    re.compile(r"https://hook(?:\.[a-z0-9-]+)?\.make\.com/[A-Za-z0-9_-]{12,}", re.I),
    re.compile(r"https://hook\.integromat\.com/[A-Za-z0-9_-]{12,}", re.I),
    re.compile(r"(?:api[_-]?key|secret|token)\s*[:=]\s*[A-Za-z0-9._~+/=-]{12,}", re.I),
]
HTTP_WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    message: str
    module_id: int | str | None = None
    module: str | None = None
    path: str | None = None


def _children(module: dict[str, Any]) -> Iterable[tuple[str, list[dict[str, Any]]]]:
    for key in ("routes", "onerror", "branches"):
        value = module.get(key)
        if not isinstance(value, list):
            continue
        for idx, item in enumerate(value):
            if isinstance(item, dict) and isinstance(item.get("flow"), list):
                yield f"{key}[{idx}].flow", item["flow"]
            elif isinstance(item, dict) and "module" in item:
                yield f"{key}[{idx}]", [item]


def walk_modules(flow: list[dict[str, Any]], prefix: str = "flow") -> Iterable[tuple[dict[str, Any], str]]:
    for idx, module in enumerate(flow):
        if not isinstance(module, dict):
            continue
        path = f"{prefix}[{idx}]"
        yield module, path
        for child_name, child_flow in _children(module):
            yield from walk_modules(child_flow, f"{path}.{child_name}")


def _string_values(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from _string_values(v)
    elif isinstance(value, list):
        for v in value:
            yield from _string_values(v)


def _has_error_handler(module: dict[str, Any]) -> bool:
    onerror = module.get("onerror")
    return isinstance(onerror, list) and len(onerror) > 0


def _module_name(module: dict[str, Any]) -> str:
    return str(module.get("module") or "")


def _is_write_module(module: dict[str, Any]) -> bool:
    name = _module_name(module)
    namespace = name.split(":", 1)[0].lower() if ":" in name else ""
    if namespace in {"util", "json", "builtin", "tools"}:
        return False
    action = name.rsplit(":", 1)[-1].lower()
    if any(action.startswith(word) or action.startswith("action" + word) for word in WRITE_ACTIONS):
        return True
    if name.lower().startswith("http:"):
        mapper = module.get("mapper") if isinstance(module.get("mapper"), dict) else {}
        method = str(mapper.get("method") or module.get("method") or "").upper()
        return method in HTTP_WRITE_METHODS
    return False


def normalize_blueprint(doc: dict[str, Any]) -> dict[str, Any]:
    """Accept direct exports plus common API/wrapper/module-export shapes."""
    if isinstance(doc.get("flow"), list):
        return doc

    wrapped = doc.get("blueprint")
    if isinstance(wrapped, dict):
        return wrapped
    if isinstance(wrapped, str):
        try:
            parsed = json.loads(wrapped)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict):
            return parsed

    subflows = doc.get("subflows")
    if isinstance(subflows, list) and subflows:
        first = subflows[0]
        if isinstance(first, dict) and isinstance(first.get("flow"), list):
            return {"name": doc.get("name", "Module export"), "flow": first["flow"], "metadata": doc.get("metadata", {})}

    return doc


def _truthy(value: Any) -> bool:
    if value is True or value == 1:
        return True
    return isinstance(value, str) and value.strip().lower() in {"1", "true", "yes"}


def _error_directives(module: dict[str, Any]) -> set[str]:
    onerror = module.get("onerror")
    if not isinstance(onerror, list):
        return set()
    directives: set[str] = set()
    stack = [item for item in onerror if isinstance(item, dict)]
    while stack:
        item = stack.pop()
        name = str(item.get("module", "")).lower()
        if name.startswith("builtin:"):
            directives.add(name)
        flow = item.get("flow")
        if isinstance(flow, list):
            stack.extend(x for x in flow if isinstance(x, dict))
    return directives


def _has_retry_handler(module: dict[str, Any]) -> bool:
    onerror = module.get("onerror")
    if not isinstance(onerror, list):
        return False
    stack = [item for item in onerror if isinstance(item, dict)]
    while stack:
        item = stack.pop()
        if str(item.get("module", "")).lower() == "builtin:break":
            mapper = item.get("mapper") if isinstance(item.get("mapper"), dict) else {}
            if _truthy(mapper.get("retry")):
                return True
        flow = item.get("flow")
        if isinstance(flow, list):
            stack.extend(x for x in flow if isinstance(x, dict))
    return False


def scan_blueprint(bp: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    bp = normalize_blueprint(bp)
    flow = bp.get("flow")
    if not isinstance(flow, list):
        return [Finding("invalid-blueprint", "critical", "Top-level 'flow' array is missing or invalid.")]
    if not flow:
        findings.append(Finding("empty-flow", "high", "Scenario contains no modules."))
        return findings

    modules = list(walk_modules(flow))
    writes = [(m, p) for m, p in modules if _is_write_module(m)]

    for module, path in modules:
        name = _module_name(module)
        mid = module.get("id")

        if _is_write_module(module) and not _has_error_handler(module):
            findings.append(Finding(
                "write-without-error-handler",
                "high",
                "Write-like module has no exported onerror route; verify failure handling and recovery behavior.",
                mid, name, path,
            ))

        if _is_write_module(module) and _has_retry_handler(module):
            findings.append(Finding(
                "retrying-write-idempotency-review",
                "medium",
                "Write-like module has an automatic retry handler. Verify a retry cannot duplicate or repeat an external side effect.",
                mid, name, path,
            ))

        if _is_write_module(module):
            directives = _error_directives(module)
            if "builtin:ignore" in directives:
                findings.append(Finding(
                    "write-skip-handler-data-loss-review",
                    "high",
                    "Write-like module uses Make's Skip/Ignore directive. A failed bundle can be dropped while the scenario continues and may still appear successful.",
                    mid, name, path,
                ))
            if "builtin:resume" in directives:
                findings.append(Finding(
                    "write-resume-handler-silent-success-review",
                    "high",
                    "Write-like module uses Make's Resume directive. The failed write can be replaced with substitute output while downstream processing continues.",
                    mid, name, path,
                ))
            if "builtin:commit" in directives:
                findings.append(Finding(
                    "write-commit-partial-state-review",
                    "medium",
                    "Write-like module uses Make's Commit directive. Earlier transactional changes can be preserved while the current run stops, creating intentional partial state.",
                    mid, name, path,
                ))

        if name.lower().startswith("http:"):
            mapper = module.get("mapper") if isinstance(module.get("mapper"), dict) else {}
            method = str(mapper.get("method") or module.get("method") or "").upper()
            if method in HTTP_WRITE_METHODS:
                findings.append(Finding(
                    "http-write-idempotency-review",
                    "medium",
                    f"HTTP {method} can mutate external state; verify duplicate protection/idempotency before retries.",
                    mid, name, path,
                ))

        if module.get("filter") and _is_write_module(module):
            findings.append(Finding(
                "filtered-write-silent-skip-review",
                "medium",
                "A filter gates a write-like module. Verify that a non-match cannot produce a business-level silent success.",
                mid, name, path,
            ))

        designer = module.get("metadata", {}).get("designer", {}) if isinstance(module.get("metadata"), dict) else {}
        messages = designer.get("messages", []) if isinstance(designer, dict) else []
        if isinstance(messages, list):
            for msg in messages:
                if isinstance(msg, dict) and str(msg.get("severity", "")).lower() in {"warning", "error"}:
                    sev = "medium" if str(msg.get("severity")).lower() == "warning" else "high"
                    findings.append(Finding(
                        "exported-designer-message",
                        sev,
                        f"Make exported a {msg.get('severity')} for this module: {msg.get('message', 'no message')}",
                        mid, name, path,
                    ))

    metadata = bp.get("metadata", {}) if isinstance(bp.get("metadata"), dict) else {}
    scenario_meta = metadata.get("scenario", {}) if isinstance(metadata.get("scenario"), dict) else {}
    instant = metadata.get("instant") is True

    if writes and scenario_meta.get("sequential") is False:
        findings.append(Finding(
            "concurrency-review",
            "medium" if instant else "low",
            "Scenario allows overlapping runs and contains write-like modules. Verify concurrent executions cannot race or duplicate writes.",
        ))

    if writes and scenario_meta.get("autoCommit") is True:
        findings.append(Finding(
            "auto-commit-recovery-review",
            "low",
            "Scenario has autoCommit=true and performs writes. For transaction-capable modules, earlier committed changes may no longer be reversible after a later failure.",
        ))

    rollback_paths = [
        p for m, p in modules
        if "builtin:rollback" in _error_directives(m)
    ]
    if rollback_paths and scenario_meta.get("autoCommit") is True:
        findings.append(Finding(
            "rollback-limited-by-autocommit-review",
            "medium",
            "Rollback handler is present while autoCommit=true. Make documents that previously committed transactional changes cannot be rolled back by a later error.",
            path=rollback_paths[0],
        ))

    if writes and scenario_meta.get("dlq") is False:
        findings.append(Finding(
            "incomplete-executions-disabled-review",
            "medium",
            "Exported scenario has dlq=false. Verify that disabling stored incomplete executions is intentional for a workflow with external writes.",
        ))

    if scenario_meta.get("dataloss") is True:
        findings.append(Finding(
            "data-loss-enabled",
            "high",
            "Scenario is exported with data-loss mode enabled; failed data may be discarded when incomplete-execution storage cannot accept more items.",
        ))

    if scenario_meta.get("confidential") is True:
        findings.append(Finding(
            "confidential-observability-review",
            "low",
            "Keep-data-confidential is enabled. Verify external observability exists because Make execution logs retain less payload detail.",
        ))

    for text in _string_values(bp):
        if any(p.search(text) for p in SECRET_PATTERNS):
            findings.append(Finding(
                "possible-secret-in-blueprint",
                "critical",
                "Possible credential or secret-like literal detected. Sanitize the blueprint before sharing or storing it.",
            ))
            break

    return sorted(findings, key=lambda f: (-SEVERITY_ORDER[f.severity], f.rule, f.path or ""))


def summary(findings: list[Finding]) -> dict[str, int]:
    out = {k: 0 for k in SEVERITY_ORDER}
    for f in findings:
        out[f.severity] += 1
    return out


def render_markdown(source: str, findings: list[Finding]) -> str:
    counts = summary(findings)
    lines = [
        "# Make Scenario Reliability Audit",
        "",
        f"Source: `{source}`",
        "",
        "## Summary",
        "",
        f"Critical: {counts['critical']} · High: {counts['high']} · Medium: {counts['medium']} · Low: {counts['low']} · Info: {counts['info']}",
        "",
        "## Findings",
        "",
    ]
    if not findings:
        lines += ["No static reliability findings detected by the current rule set.", ""]
    else:
        for idx, f in enumerate(findings, 1):
            where = f" — module `{f.module}` id `{f.module_id}`" if f.module else ""
            lines += [f"### {idx}. {f.severity.upper()} — {f.rule}{where}", "", f.message, ""]
    lines += [
        "## Scope limitation",
        "",
        "This is a static blueprint review. It cannot prove runtime correctness, third-party availability, credential validity, data quality, or business outcomes.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("blueprint", type=Path)
    ap.add_argument("--json-out", type=Path)
    ap.add_argument("--md-out", type=Path)
    ap.add_argument("--fail-on", choices=list(SEVERITY_ORDER))
    args = ap.parse_args()

    try:
        bp = json.loads(args.blueprint.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 2

    if not isinstance(bp, dict):
        findings = [Finding("invalid-blueprint", "critical", "Blueprint root must be a JSON object.")]
    else:
        findings = scan_blueprint(bp)

    payload = {
        "source": str(args.blueprint),
        "summary": summary(findings),
        "findings": [asdict(f) for f in findings],
    }
    if args.json_out:
        args.json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if args.md_out:
        args.md_out.write_text(render_markdown(str(args.blueprint), findings), encoding="utf-8")
    if not args.json_out and not args.md_out:
        print(json.dumps(payload, indent=2))

    if args.fail_on:
        threshold = SEVERITY_ORDER[args.fail_on]
        if any(SEVERITY_ORDER[f.severity] >= threshold for f in findings):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
