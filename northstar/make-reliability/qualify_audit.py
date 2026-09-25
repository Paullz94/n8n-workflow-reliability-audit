#!/usr/bin/env python3
"""Deterministically qualify a PCFlows audit request.

This is an internal routing gate, not a customer-facing score.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import audit_make
import report_builder


HIGH_VALUE_RULES = {
    "write-without-error-handler",
    "write-skip-handler-data-loss-review",
    "write-resume-handler-silent-success-review",
    "retrying-write-idempotency-review",
    "http-write-idempotency-review",
    "concurrency-review",
    "incomplete-executions-disabled-review",
    "data-loss-enabled",
    "write-commit-partial-state-review",
    "rollback-limited-by-autocommit-review",
}


class QualificationError(ValueError):
    pass


def qualify(blueprint: dict[str, Any], raw_context: dict[str, Any] | None = None) -> dict[str, Any]:
    context = report_builder.sanitize_context(raw_context or {})
    findings = audit_make.scan_blueprint(blueprint)
    rules = {f.rule for f in findings}

    if "possible-secret-in-blueprint" in rules:
        return {
            "route": "resanitize_required",
            "paid_candidate": False,
            "reason": "Possible secret-like literal detected. Do not accept the blueprint until it is sanitized again.",
            "next_action": "Request a new sanitized export. Do not store or analyze the supplied file further.",
        }

    if "invalid-blueprint" in rules or "empty-flow" in rules:
        return {
            "route": "invalid_input",
            "paid_candidate": False,
            "reason": "The supplied JSON is not a usable Make.com scenario blueprint for this audit.",
            "next_action": "Ask for a fresh Make.com blueprint export.",
        }

    missing_context = [
        key for key in ("scenario_name", "business_goal")
        if not isinstance(context.get(key), str) or not context[key].strip()
    ]
    if missing_context:
        return {
            "route": "context_required",
            "paid_candidate": False,
            "reason": "The blueprint is analyzable but the paid audit needs non-sensitive business context.",
            "missing_context": missing_context,
            "next_action": "Use the local PCFlows intake generator and provide the missing fields.",
        }

    high_value = [f for f in findings if f.rule in HIGH_VALUE_RULES]
    high_or_critical = [f for f in findings if f.severity in {"critical", "high"}]
    critical_side_effects = context.get("critical_side_effects") or []

    if high_value or high_or_critical or critical_side_effects:
        return {
            "route": "paid_audit_candidate",
            "paid_candidate": True,
            "reason": "The scenario has reliability/data-integrity signals or business-critical side effects that justify contextual prioritization and verification.",
            "finding_count": len(findings),
            "high_value_rules": sorted({f.rule for f in high_value}),
            "next_action": "Offer the fixed-scope Data Integrity Audit; keep production credentials out of scope.",
        }

    return {
        "route": "free_preflight_sufficient",
        "paid_candidate": False,
        "reason": "The current static evidence does not yet justify selling a deeper audit.",
        "finding_count": len(findings),
        "next_action": "Give the free preflight result and ask the user to return if runtime symptoms or business-critical concerns exist.",
    }


def load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise QualificationError(f"{label} is not valid readable JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise QualificationError(f"{label} root must be an object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("blueprint", type=Path)
    parser.add_argument("--context", type=Path)
    args = parser.parse_args()

    try:
        blueprint = load_object(args.blueprint, "blueprint")
        context = load_object(args.context, "context") if args.context else {}
        result = qualify(blueprint, context)
    except QualificationError as exc:
        print(json.dumps({"error": str(exc)}))
        return 2

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
