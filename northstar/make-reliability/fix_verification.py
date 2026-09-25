#!/usr/bin/env python3
"""PCFlows remediation proof gate.

A finding disappearing from a blueprint is not automatically "fixed".
Customer-facing status is deliberately conservative:
- detected
- statically_cleared
- evidence_supported
- verified_fixed

Only trusted connected runtime evidence may produce verified_fixed for rules
whose real-world behavior depends on execution.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import audit_make


@dataclass(frozen=True)
class VerificationSpec:
    mode: str  # static_only | runtime_required
    required_assertions: tuple[str, ...]
    verification_goal: str


RULE_VERIFICATION_SPECS: dict[str, VerificationSpec] = {
    "invalid-blueprint": VerificationSpec(
        "static_only", (), "A fresh export is structurally recognized by the scanner."
    ),
    "empty-flow": VerificationSpec(
        "static_only", (), "A fresh export contains the intended executable flow."
    ),
    "possible-secret-in-blueprint": VerificationSpec(
        "static_only", (), "A newly sanitized export no longer triggers secret-like detection."
    ),
    "exported-designer-message": VerificationSpec(
        "static_only", (), "The re-export no longer contains the warning/error, or it is explicitly documented as accepted."
    ),
    "write-without-error-handler": VerificationSpec(
        "runtime_required",
        ("failure_injected", "failure_observable", "recovery_path_succeeds", "duplicate_side_effects_zero"),
        "A controlled downstream failure is observable and recoverable without unintended duplicate effects."
    ),
    "retrying-write-idempotency-review": VerificationSpec(
        "runtime_required",
        ("duplicate_replay_executed", "intended_side_effect_count_one"),
        "Replaying the same business event produces only one intended external side effect."
    ),
    "http-write-idempotency-review": VerificationSpec(
        "runtime_required",
        ("duplicate_replay_executed", "intended_side_effect_count_one"),
        "Repeating the same mutating HTTP business request does not create an unintended duplicate."
    ),
    "write-skip-handler-data-loss-review": VerificationSpec(
        "runtime_required",
        ("failure_injected", "missing_action_observable", "silent_success_prevented"),
        "A failed write cannot disappear without an operator-visible signal or explicit acceptable-loss path."
    ),
    "write-resume-handler-silent-success-review": VerificationSpec(
        "runtime_required",
        ("failure_injected", "fallback_distinguishable", "false_success_prevented"),
        "Downstream processing cannot mistake fallback/substitute output for proof that the write succeeded."
    ),
    "write-commit-partial-state-review": VerificationSpec(
        "runtime_required",
        ("failure_injected", "partial_state_identified", "reconciliation_path_succeeds"),
        "Intentional partial state is detectable and reconcilable after a later failure."
    ),
    "auto-commit-recovery-review": VerificationSpec(
        "runtime_required",
        ("failure_injected", "committed_state_identified", "compensation_or_reconciliation_succeeds"),
        "Earlier committed state after a later failure is acceptable or can be reconciled/compensated."
    ),
    "rollback-limited-by-autocommit-review": VerificationSpec(
        "runtime_required",
        ("failure_injected", "rollback_boundary_observed", "remaining_state_matches_design"),
        "The observed rollback boundary matches the documented design and does not leave unexpected state."
    ),
    "filtered-write-silent-skip-review": VerificationSpec(
        "runtime_required",
        ("nonmatching_event_tested", "skip_observable", "missing_work_not_misreported_complete"),
        "An intentionally filtered event is distinguishable from missing business work."
    ),
    "concurrency-review": VerificationSpec(
        "runtime_required",
        ("concurrent_test_executed", "final_state_deterministic", "duplicate_side_effects_zero"),
        "Near-simultaneous events for the same business key produce deterministic final state without duplicates."
    ),
    "incomplete-executions-disabled-review": VerificationSpec(
        "runtime_required",
        ("failure_injected", "failed_work_locatable", "resume_or_replay_succeeds", "duplicate_side_effects_zero"),
        "Failed accepted work can be located and recovered/replayed without duplicate side effects."
    ),
    "data-loss-enabled": VerificationSpec(
        "runtime_required",
        ("failure_injected", "failed_work_recoverable", "unintended_data_loss_zero"),
        "The configured failure path preserves required business work under the tested failure."
    ),
    "confidential-observability-review": VerificationSpec(
        "runtime_required",
        ("failure_injected", "correlation_available", "affected_event_identifiable", "sensitive_payload_not_exposed"),
        "Operators can identify and diagnose the affected business event without retaining sensitive payloads."
    ),
}


TRUSTED_RUNTIME_SOURCES = {
    "connected_test_run",
}
SUPPORTING_RUNTIME_SOURCES = {
    "sanitized_execution_evidence",
    "customer_test_record",
}


class VerificationError(ValueError):
    pass


def validate_registry_coverage() -> None:
    known=set(audit_make.KNOWN_RULES)
    actual=set(RULE_VERIFICATION_SPECS)
    if known != actual:
        raise VerificationError(
            f"verification registry drift: missing={sorted(known-actual)} extra={sorted(actual-known)}"
        )


def validate_runtime_evidence(rule: str, evidence: dict[str, Any] | None) -> dict[str, Any]:
    spec=RULE_VERIFICATION_SPECS[rule]
    if spec.mode!="runtime_required":
        return {"complete":True,"trusted":True,"missing":[],"source":"static_only"}

    if not isinstance(evidence,dict):
        return {"complete":False,"trusted":False,"missing":list(spec.required_assertions),"source":None}

    source=str(evidence.get("source") or "").strip()
    assertions=evidence.get("assertions")
    if not isinstance(assertions,dict):
        assertions={}

    missing=[key for key in spec.required_assertions if assertions.get(key) is not True]
    complete=not missing
    trusted=source in TRUSTED_RUNTIME_SOURCES
    supporting=source in SUPPORTING_RUNTIME_SOURCES

    return {
        "complete":complete,
        "trusted":trusted,
        "supporting":supporting,
        "missing":missing,
        "source":source or None,
    }


def resolution_status(
    *,
    rule: str,
    still_present_after: bool,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if rule not in RULE_VERIFICATION_SPECS:
        raise VerificationError(f"unknown verification rule: {rule}")
    spec=RULE_VERIFICATION_SPECS[rule]

    if still_present_after:
        ev=validate_runtime_evidence(rule,evidence)
        if spec.mode=="runtime_required" and ev["complete"] and (ev["trusted"] or ev.get("supporting")):
            return {
                "status":"verified_mitigated_not_statically_cleared",
                "customer_language":"Runtime evidence supports the mitigation, but the static review signal is still present. Do not call this fixed.",
                "verified_fixed":False,
                "evidence":ev,
            }
        return {
            "status":"still_present",
            "customer_language":"The static review signal is still present.",
            "verified_fixed":False,
            "evidence":ev,
        }

    if spec.mode=="static_only":
        return {
            "status":"verified_static_fix",
            "customer_language":"The revised artifact no longer contains the structural issue detected by this rule.",
            "verified_fixed":True,
            "evidence":{"complete":True,"trusted":True,"source":"static_only","missing":[]},
        }

    ev=validate_runtime_evidence(rule,evidence)
    if ev["complete"] and ev["trusted"]:
        return {
            "status":"verified_fixed",
            "customer_language":"The static signal cleared and the required connected synthetic runtime checks passed.",
            "verified_fixed":True,
            "evidence":ev,
        }
    if ev["complete"] and ev.get("supporting"):
        return {
            "status":"evidence_supported_pending_independent_verification",
            "customer_language":"The static signal cleared and supplied runtime evidence supports the remediation, but PCFlows did not independently execute the test.",
            "verified_fixed":False,
            "evidence":ev,
        }
    return {
        "status":"statically_cleared_runtime_pending",
        "customer_language":"The revised blueprint no longer matches the static rule, but runtime verification is still required before calling the issue fixed.",
        "verified_fixed":False,
        "evidence":ev,
    }


validate_registry_coverage()
