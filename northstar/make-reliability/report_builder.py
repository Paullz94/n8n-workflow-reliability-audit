#!/usr/bin/env python3
"""Build a deterministic data-integrity audit from Northstar Make findings.

No network calls. The builder consumes a sanitized blueprint plus optional
non-sensitive business context and emits a prioritized Markdown report.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import audit_make


@dataclass(frozen=True)
class Guidance:
    pillar: str
    impact: str
    action: str
    verify: str


GUIDANCE: dict[str, Guidance] = {
    "possible-secret-in-blueprint": Guidance(
        "prevent",
        "A shared blueprint may expose a credential or secret-like literal.",
        "Remove the literal, rotate it if it may be real, and use the platform's credential/connection mechanism.",
        "Re-export a sanitized blueprint and confirm the secret check is clear.",
    ),
    "data-loss-enabled": Guidance(
        "recover",
        "Failed bundles may be discarded under configured data-loss behavior instead of remaining recoverable.",
        "Confirm whether dropping failed work is acceptable; otherwise configure recovery/incomplete-execution behavior for the business process.",
        "Force a safe synthetic failure and verify the failed work remains visible/recoverable as intended.",
    ),
    "write-without-error-handler": Guidance(
        "recover",
        "A failed external write may stop or diverge without an explicit exported recovery path.",
        "Define the expected behavior for transient and permanent failure: retry, quarantine, alert, compensate, or stop deliberately.",
        "Inject a synthetic downstream failure and confirm the chosen recovery path is observable and bounded.",
    ),
    "retrying-write-idempotency-review": Guidance(
        "prevent",
        "Automatic retry can repeat an external side effect if the first attempt actually committed before the failure became visible.",
        "Add an idempotency key, upsert/deduplication guard, or pre-write existence check appropriate to the destination semantics.",
        "Replay the same synthetic business event twice and confirm only the intended final state/side effect exists.",
    ),
    "write-skip-handler-data-loss-review": Guidance(
        "detect",
        "A failed write can be dropped while Make continues with later bundles and can report the run as successful.",
        "Use Skip only when losing the failed business event is explicitly acceptable; otherwise route it to retry, recovery, quarantine or an operator-visible failure path.",
        "Force a safe synthetic write failure and confirm the missing business action is visible rather than silently discarded.",
    ),
    "write-resume-handler-silent-success-review": Guidance(
        "detect",
        "Resume can substitute output for a failed write and allow downstream steps to continue as though useful output existed.",
        "Document the fallback contract and prevent downstream success from being interpreted as proof that the external write occurred.",
        "Force the write to fail and verify downstream systems cannot mistake substitute output for a completed side effect.",
    ),
    "write-commit-partial-state-review": Guidance(
        "recover",
        "Commit intentionally preserves earlier transactional changes and stops the run, which can leave a partial but intentional state.",
        "Document the reconciliation path for work committed before the failure and ensure operators can distinguish complete from partial processing.",
        "Trigger a synthetic failure after an earlier transaction and verify the partial state is detectable and recoverable.",
    ),
    "auto-commit-recovery-review": Guidance(
        "recover",
        "Auto-commit can make earlier transactional changes irreversible before later modules finish.",
        "Confirm that incremental commits are required and define compensating/reconciliation behavior for later failures.",
        "Trigger a later synthetic failure and verify earlier committed state is either acceptable or explicitly compensated.",
    ),
    "rollback-limited-by-autocommit-review": Guidance(
        "recover",
        "Rollback cannot undo transactional changes that Make already committed earlier when auto-commit is enabled.",
        "If full transactional rollback is intended, review the scenario's auto-commit setting and the transaction capabilities of the affected modules.",
        "Create a safe test where an early transaction succeeds and a later module fails; verify the actual rollback boundary matches the design.",
    ),
    "http-write-idempotency-review": Guidance(
        "prevent",
        "POST/PUT/PATCH/DELETE requests can change remote state and may be unsafe to repeat without endpoint-specific duplicate protection.",
        "Document the endpoint's idempotency semantics and add a stable business key or idempotency mechanism before enabling retries.",
        "Repeat a synthetic request with the same business key and verify the remote system does not create an unintended duplicate.",
    ),
    "filtered-write-silent-skip-review": Guidance(
        "detect",
        "A bundle can be filtered out before a business write, which may look like successful scenario execution while the expected side effect never occurs.",
        "Make the non-match path explicit: count it, log it, alert on unexpected volume, or route it to a review queue.",
        "Provide a synthetic non-matching event and verify operators can distinguish an intentional skip from a missing write.",
    ),
    "concurrency-review": Guidance(
        "prevent",
        "Overlapping executions can race when they update the same logical record or depend on event order.",
        "Identify the natural business key and decide whether per-key serialization, sequential processing, optimistic checks, or idempotent writes are required.",
        "Submit two safe synthetic events for the same business key concurrently and verify the final state is deterministic.",
    ),
    "incomplete-executions-disabled-review": Guidance(
        "recover",
        "External writes exist while stored incomplete-execution recovery is exported as disabled, reducing one recovery path after failures.",
        "Confirm the recovery strategy explicitly and enable incomplete executions when appropriate for the scenario's failure model.",
        "Trigger a safe synthetic failure after input acceptance and verify the work can be located and resumed/replayed according to policy.",
    ),
    "confidential-observability-review": Guidance(
        "detect",
        "Confidential execution settings reduce payload visibility in platform logs, which can make incident diagnosis harder.",
        "Keep confidentiality if required, but define privacy-safe correlation IDs, counters and failure metadata outside sensitive payloads.",
        "Run a synthetic failure and confirm an operator can identify the affected business event without exposing sensitive content.",
    ),
    "exported-designer-message": Guidance(
        "detect",
        "Make exported a designer warning/error that may indicate an incomplete or suspicious module configuration.",
        "Resolve or explicitly accept the exported warning before treating the scenario as production-ready.",
        "Re-export the blueprint and confirm the warning is gone or documented as intentionally accepted.",
    ),
    "empty-flow": Guidance(
        "prevent",
        "There is no executable flow to review.",
        "Export the intended scenario rather than an empty shell.",
        "Confirm the next export contains the expected modules.",
    ),
    "invalid-blueprint": Guidance(
        "prevent",
        "The supplied JSON is not in a supported Make blueprint shape, so reliability conclusions would be unreliable.",
        "Export the scenario blueprint again or provide a supported API wrapper/module export.",
        "Re-run the preflight and confirm the blueprint structure is recognized.",
    ),
}

SEVERITY_WEIGHT = {"critical": 5000, "high": 4000, "medium": 3000, "low": 2000, "info": 1000}
PILLAR_ORDER = {"prevent": 0, "detect": 1, "recover": 2}
ALLOWED_CONTEXT = {
    "scenario_name",
    "business_goal",
    "critical_side_effects",
    "duplicate_tolerance",
    "ordering_required",
    "recovery_expectation",
}


def sanitize_context(raw: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return {}
    clean: dict[str, Any] = {}
    for key in ALLOWED_CONTEXT:
        value = raw.get(key)
        if isinstance(value, str):
            clean[key] = value.strip()[:500]
        elif key == "critical_side_effects" and isinstance(value, list):
            clean[key] = [str(v).strip()[:160] for v in value[:10] if str(v).strip()]
        elif key == "ordering_required" and isinstance(value, bool):
            clean[key] = value
    return clean


def priority_score(finding: audit_make.Finding, context: dict[str, Any]) -> int:
    score = SEVERITY_WEIGHT.get(finding.severity, 0)
    if finding.rule in {"retrying-write-idempotency-review", "http-write-idempotency-review", "concurrency-review"}:
        if str(context.get("duplicate_tolerance", "")).lower() in {"none", "zero", "not allowed"}:
            score += 8
    if finding.rule == "concurrency-review" and context.get("ordering_required") is True:
        score += 8
    if finding.rule in {"write-without-error-handler", "incomplete-executions-disabled-review", "data-loss-enabled"}:
        if context.get("recovery_expectation"):
            score += 4
    return score


def enriched_findings(findings: list[audit_make.Finding], context: dict[str, Any]) -> list[dict[str, Any]]:
    enriched = []
    for f in findings:
        guidance = GUIDANCE.get(f.rule, Guidance(
            "detect",
            "Static analysis found a condition that requires scenario-owner review.",
            "Review the finding against the intended business behavior and document the decision.",
            "Re-run a sanitized synthetic test that exercises the affected path.",
        ))
        enriched.append({
            "finding": f,
            "guidance": guidance,
            "priority": priority_score(f, context),
        })
    return sorted(
        enriched,
        key=lambda item: (-item["priority"], PILLAR_ORDER.get(item["guidance"].pillar, 9), item["finding"].rule),
    )


def render_report(source: str, findings: list[audit_make.Finding], context: dict[str, Any]) -> str:
    rows = enriched_findings(findings, context)
    counts = audit_make.summary(findings)
    scenario_name = context.get("scenario_name") or source

    lines = [
        "# Northstar Make Data Integrity Audit",
        "",
        f"Scenario: **{scenario_name}**",
        "",
        "## Executive summary",
        "",
        f"Static preflight found **{counts['critical']} critical, {counts['high']} high, {counts['medium']} medium and {counts['low']} low** findings.",
        "",
    ]

    if context.get("business_goal"):
        lines += [f"Business goal: {context['business_goal']}", ""]
    if context.get("critical_side_effects"):
        lines += ["Critical side effects: " + "; ".join(context["critical_side_effects"]), ""]

    pillar_counts = {"prevent": 0, "detect": 0, "recover": 0}
    for row in rows:
        pillar_counts[row["guidance"].pillar] = pillar_counts.get(row["guidance"].pillar, 0) + 1
    lines += [
        "Reliability lens: " + ", ".join(f"{name} {pillar_counts.get(name, 0)}" for name in ("prevent", "detect", "recover")) + ".",
        "",
        "## Prioritized remediation",
        "",
    ]

    if not rows:
        lines += ["No static findings were detected by the current rules. Runtime testing is still required.", ""]
    for index, row in enumerate(rows, 1):
        f = row["finding"]
        g = row["guidance"]
        where = f" — `{f.module}` id `{f.module_id}`" if f.module else ""
        lines += [
            f"### {index}. {f.severity.upper()} · {g.pillar.upper()} · {f.rule}{where}",
            "",
            f"**Evidence:** {f.message}",
            "",
            f"**Why it matters:** {g.impact}",
            "",
            f"**Recommended next step:** {g.action}",
            "",
            f"**Verification:** {g.verify}",
            "",
        ]

    lines += [
        "## Verification checklist",
        "",
        "- Use only sanitized/synthetic test events.",
        "- Exercise each affected write path at least once.",
        "- Replay duplicate business events where duplicate protection matters.",
        "- Exercise transient and permanent downstream failures separately.",
        "- Confirm skips, retries and recovery events are observable without exposing sensitive payloads.",
        "- Re-export and re-run the static scan after remediation.",
        "",
        "## Scope and limitations",
        "",
        "This report is deterministic static analysis of a sanitized blueprint plus optional non-sensitive context. It does not access production systems and cannot prove runtime correctness, authorization, third-party availability, business semantics, or the absence of defects.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("blueprint", type=Path)
    parser.add_argument("--context", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    try:
        document = json.loads(args.blueprint.read_text(encoding="utf-8"))
        if not isinstance(document, dict):
            raise ValueError("Blueprint root must be a JSON object")
        raw_context = json.loads(args.context.read_text(encoding="utf-8")) if args.context else {}
        if not isinstance(raw_context, dict):
            raise ValueError("Context root must be a JSON object")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 2

    context = sanitize_context(raw_context)
    findings = audit_make.scan_blueprint(document)
    report = render_report(args.blueprint.name, findings, context)
    if args.out:
        args.out.write_text(report, encoding="utf-8")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
