#!/usr/bin/env python3
"""Conservative feasibility gate for future PCFlows Verified Repair requests.

The gate protects customers from AI accepting vague, impossible, unsafe, or
unverifiable repair promises.
"""
from __future__ import annotations

from typing import Any


class RepairScopeError(ValueError):
    pass


ABSOLUTE_OUTCOMES={
    "guarantee_no_future_bugs",
    "guarantee_third_party_uptime",
    "guarantee_security_compliance",
    "guarantee_legal_compliance",
    "unlimited_fix_everything",
}


def qualify_repair_request(request:dict[str,Any])->dict[str,Any]:
    if not isinstance(request,dict):
        raise RepairScopeError("request must be an object")

    outcome=str(request.get("requested_outcome") or "").strip()
    if outcome in ABSOLUTE_OUTCOMES:
        return {
            "route":"decline_absolute_promise",
            "verified_repair_eligible":False,
            "reason":"The requested outcome cannot be bounded and independently proven by PCFlows.",
        }

    if request.get("requires_third_party_vendor_change") is True:
        return {
            "route":"diagnosis_only_external_dependency",
            "verified_repair_eligible":False,
            "reason":"PCFlows cannot promise to repair behavior controlled by a third-party vendor outside the customer's automation.",
        }

    if request.get("requires_destructive_real_data_test") is True:
        return {
            "route":"decline_unsafe_test",
            "verified_repair_eligible":False,
            "reason":"The issue cannot be accepted for Verified Repair when proof requires destructive real-customer data operations.",
        }

    if request.get("safe_test_environment") is not True:
        return {
            "route":"audit_or_prepare_test_environment",
            "verified_repair_eligible":False,
            "reason":"A safe test/sandbox path is required before PCFlows can promise a verified repair.",
        }

    if request.get("reproducible_or_observable") is not True:
        return {
            "route":"diagnostic_first",
            "verified_repair_eligible":False,
            "reason":"The symptom is not yet reproducible or independently observable; diagnose before accepting a repair outcome.",
        }

    if request.get("acceptance_criteria_defined") is not True:
        return {
            "route":"define_acceptance_criteria",
            "verified_repair_eligible":False,
            "reason":"The issue needs an explicit definition of done before repair acceptance.",
        }

    root_causes=int(request.get("accepted_root_cause_count") or 0)
    if root_causes != 1:
        return {
            "route":"split_or_requalify_scope",
            "verified_repair_eligible":False,
            "reason":"Verified Repair is intentionally bounded to one accepted root-cause issue per repair scope.",
        }

    if request.get("customer_authorized_target") is not True:
        return {
            "route":"await_customer_authorization",
            "verified_repair_eligible":False,
            "reason":"PCFlows cannot modify or test a target scenario without explicit case-bound customer authorization.",
        }

    return {
        "route":"verified_repair_candidate",
        "verified_repair_eligible":True,
        "reason":"The issue is bounded, observable, testable, authorized, and has an explicit definition of done.",
    }
