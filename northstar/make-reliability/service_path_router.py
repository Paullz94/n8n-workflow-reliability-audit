#!/usr/bin/env python3
"""Route PCFlows cases without over-rejecting useful customer work.

Strict verification gates apply only to the strength of the promise, not to
whether PCFlows can help at all.
"""
from __future__ import annotations

from typing import Any

import fix_eligibility


class ServicePathError(ValueError):
    pass


def route_case(
    *,
    rule:str,
    safe_to_analyze:bool,
    authorized_to_review:bool,
    root_cause_known:bool,
    safe_test_environment:bool,
    pcflows_can_observe_runtime:bool,
    external_side_effect_observable:bool,
    acceptance_criteria_defined:bool,
    customer_wants_done_for_you_fix:bool,
)->dict[str,Any]:
    if not safe_to_analyze:
        return {
            "route":"resanitize_or_scope_correction",
            "declined":False,
            "reason":"The current material is unsafe or unusable, but the customer can continue after sanitization/scope correction.",
        }

    if not authorized_to_review:
        return {
            "route":"authorization_required",
            "declined":False,
            "reason":"PCFlows needs customer authorization before reviewing or changing the workflow.",
        }

    if not root_cause_known:
        return {
            "route":"audit_then_decide",
            "declined":False,
            "recommended_package":"data_integrity_audit",
            "reason":"Do not guess at a repair. Diagnose first, then automatically re-route once the root cause is explicit.",
        }

    eligibility=fix_eligibility.assess_fix_eligibility(
        rule=rule,
        safe_test_environment=safe_test_environment,
        pcflows_can_observe_runtime=pcflows_can_observe_runtime,
        external_side_effect_observable=external_side_effect_observable,
        acceptance_criteria_defined=acceptance_criteria_defined,
    )

    if customer_wants_done_for_you_fix and eligibility["eligible_for_verified_repair"]:
        return {
            "route":"verified_repair_candidate",
            "declined":False,
            "reason":"The issue is bounded and independently testable, so the strongest repair commitment is possible.",
            "eligibility":eligibility,
        }

    if customer_wants_done_for_you_fix:
        return {
            "route":"guided_remediation_then_verify",
            "declined":False,
            "recommended_package":"data_integrity_audit",
            "reason":"PCFlows can still diagnose and prescribe the repair; only the independently verified repair promise is unavailable until the missing proof prerequisites exist.",
            "missing_verified_repair_prerequisites":eligibility.get("missing",[]),
            "eligibility":eligibility,
        }

    return {
        "route":"audit_and_verification_plan",
        "declined":False,
        "recommended_package":"data_integrity_audit",
        "reason":"The customer does not need a done-for-you repair commitment; proceed with audit, remediation guidance and verification plan.",
        "eligibility":eligibility,
    }
