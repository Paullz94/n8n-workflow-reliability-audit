"""Create a deterministic customer delivery pack from one sanitized n8n export."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from audit import audit_workflow, render_markdown


def _summary_markdown(result: dict[str, Any], order_ref: str | None) -> str:
    workflow = result["workflow"]
    summary = result["summary"]
    total = sum(summary.values())
    high_risk = summary["critical"] + summary["high"]
    ref = order_ref or "not-provided"
    return "\n".join([
        f"# PCFlows client summary — {workflow['name']}",
        "",
        f"- Order reference: {ref}",
        f"- Workflow nodes reviewed: {workflow['node_count']}",
        f"- Static findings: {total}",
        f"- Critical/high findings: {high_risk}",
        f"- Input SHA-256: {result['input_sha256']}",
        "",
        "## What this package proves",
        "",
        "It records a deterministic static review of the exact supplied export, identified by SHA-256.",
        "",
        "## What this package does not prove",
        "",
        "It does not certify production safety, credentials, remote API behavior, instance configuration, regulatory compliance, or real-world side effects.",
        "",
        "## Recommended next step",
        "",
        "Review the ranked findings, then execute the synthetic verification plan before any production change is accepted.",
        "",
    ])


def _verification_plan(result: dict[str, Any]) -> str:
    rule_ids = {finding["rule_id"] for finding in result["findings"]}
    checks = [
        ("Happy path", "Run one synthetic valid event and independently verify every intended side effect."),
        ("Malformed input", "Send missing/invalid required fields and confirm the workflow fails safely without partial writes."),
        ("Duplicate delivery", "Replay the same synthetic business event and verify duplicate external side effects are prevented."),
        ("Timeout ambiguity", "Simulate a remote timeout after a possible write and verify retry/reconciliation cannot create a duplicate."),
        ("Partial failure", "Force a downstream failure after an earlier successful side effect and verify recovery is explicit and traceable."),
    ]

    if "SEC-001" in rule_ids:
        checks.append(("Webhook authentication", "Confirm unauthenticated/replayed requests are rejected with no side effects."))
    if "RECOVERY-001" in rule_ids:
        checks.append(("Error routing", "Force an execution failure and confirm the operator-visible recovery path receives redacted context."))
    if "RECOVERY-004" in rule_ids:
        checks.append(("Continued failure", "Force the affected node to fail and confirm continuation logic cannot masquerade as business success."))
    if "SEC-003" in rule_ids:
        checks.append(("Secret rotation", "Remove/rotate any real credential-like literal and confirm the workflow uses managed credentials or a secret store."))

    lines = [
        "# Synthetic verification plan",
        "",
        "Use synthetic/non-production data only. Record expected and actual outcomes for each test.",
        "",
        "| Test | Acceptance evidence |",
        "|---|---|",
    ]
    for name, acceptance in checks:
        lines.append(f"| {name} | {acceptance} |")

    lines.extend([
        "",
        "## Release evidence",
        "",
        "- Exact before/after export hashes.",
        "- Test inputs that contain no real personal data or secrets.",
        "- Independent verification of downstream side effects.",
        "- Rollback procedure and owner.",
        "- Known residual risks accepted in writing.",
        "",
    ])
    return "\n".join(lines)


def create_delivery_pack(workflow_path: Path, output_dir: Path, order_ref: str | None = None) -> dict[str, Any]:
    raw = workflow_path.read_bytes()
    workflow = json.loads(raw.decode("utf-8"))
    if not isinstance(workflow, dict):
        raise ValueError("Expected one n8n workflow JSON object.")

    output_dir.mkdir(parents=True, exist_ok=True)

    result = audit_workflow(workflow)
    result["input_sha256"] = hashlib.sha256(raw).hexdigest()
    result["order_reference"] = order_ref

    files = {
        "audit_markdown": output_dir / "01-audit-report.md",
        "audit_json": output_dir / "02-audit-report.json",
        "client_summary": output_dir / "03-client-summary.md",
        "verification_plan": output_dir / "04-synthetic-verification-plan.md",
        "manifest": output_dir / "MANIFEST.json",
    }

    files["audit_markdown"].write_text(render_markdown(result), encoding="utf-8")
    files["audit_json"].write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    files["client_summary"].write_text(_summary_markdown(result, order_ref), encoding="utf-8")
    files["verification_plan"].write_text(_verification_plan(result), encoding="utf-8")

    manifest = {
        "package": "PCFlows n8n Reliability Audit",
        "schema_version": 1,
        "order_reference": order_ref,
        "input_filename": workflow_path.name,
        "input_sha256": result["input_sha256"],
        "workflow_name": result["workflow"]["name"],
        "finding_summary": result["summary"],
        "files": {},
    }

    for key, path in files.items():
        if key == "manifest":
            continue
        payload = path.read_bytes()
        manifest["files"][path.name] = {
            "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload),
        }

    files["manifest"].write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a PCFlows customer delivery pack.")
    parser.add_argument("workflow", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--order-ref", type=str)
    args = parser.parse_args()
    create_delivery_pack(args.workflow, args.output_dir, args.order_ref)


if __name__ == "__main__":
    main()
