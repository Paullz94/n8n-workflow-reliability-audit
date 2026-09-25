#!/usr/bin/env python3
"""Create a privacy-bounded AI review packet from deterministic PCFlows findings.

This is a preparation layer only. It does not call any model or external API.
The packet intentionally contains:
- allowlisted non-sensitive business context;
- deterministic finding metadata/messages;
- official-rule references where available.

It deliberately excludes:
- the raw blueprint;
- module mapper/parameter payloads;
- credentials or customer records.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import audit_make
import report_builder


class PacketError(ValueError):
    pass


def load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PacketError(f"{label} is not valid readable JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise PacketError(f"{label} root must be an object")
    return value


def make_packet(
    blueprint: dict[str, Any],
    raw_context: dict[str, Any],
) -> dict[str, Any]:
    context = report_builder.sanitize_context(raw_context)
    findings = audit_make.scan_blueprint(blueprint)

    if any(f.rule == "possible-secret-in-blueprint" for f in findings):
        raise PacketError(
            "Possible secret-like literal detected. Do not create an AI packet until the blueprint is re-sanitized."
        )

    rows = report_builder.enriched_findings(findings, context)
    packet_findings = []
    for row in rows:
        f = row["finding"]
        g = row["guidance"]
        packet_findings.append({
            "rule": f.rule,
            "severity": f.severity,
            "module_id": f.module_id,
            "module_type": f.module,
            "path": f.path,
            "evidence": f.message,
            "pillar": g.pillar,
            "deterministic_impact": g.impact,
            "deterministic_action": g.action,
            "deterministic_verification": g.verify,
            "official_reference": report_builder.RULE_REFERENCES.get(f.rule),
        })

    return {
        "schema": "pcflows.ai-review-packet.v1",
        "purpose": "bounded interpretation of deterministic Make.com reliability findings",
        "context": context,
        "summary": audit_make.summary(findings),
        "findings": packet_findings,
        "model_instructions": {
            "must": [
                "Treat deterministic findings as evidence, not as proof of a production defect.",
                "Prioritize business impact using only the supplied context and findings.",
                "Distinguish documented platform behavior from inference.",
                "Call out ambiguity explicitly instead of inventing missing runtime facts.",
                "Prefer synthetic verification steps that do not require production credentials.",
                "Keep implementation advice bounded to the reported risk.",
            ],
            "must_not": [
                "Invent runtime failures, customer impact, logs, credentials, or API behavior not present in the packet.",
                "Claim that a static audit proves correctness, security, compliance, or absence of defects.",
                "Request passwords, API keys, private webhook secrets, or production credentials.",
                "Echo or reconstruct sensitive blueprint payloads.",
            ],
            "requested_output": {
                "top_risks": "Up to 3 highest-value risks with concise rationale.",
                "ambiguities": "Findings that need human/runtime confirmation before remediation.",
                "verification_plan": "Smallest safe synthetic tests in priority order.",
                "executive_summary": "Short client-facing summary with limitations.",
            },
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("blueprint", type=Path)
    parser.add_argument("--context", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    try:
        blueprint = load_object(args.blueprint, "blueprint")
        context = load_object(args.context, "context")
        packet = make_packet(blueprint, context)
    except PacketError as exc:
        print(json.dumps({"error": str(exc)}))
        return 2

    payload = json.dumps(packet, indent=2) + "\n"
    if args.out:
        args.out.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
