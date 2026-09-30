#!/usr/bin/env python3
"""Gate any future PCFlows done-for-you repair promise on verifiability."""
from __future__ import annotations

from typing import Any

import fix_verification


class FixEligibilityError(ValueError):
    pass


def assess_fix_eligibility(
    *,
    rule:str,
    safe_test_environment:bool,
    pcflows_can_observe_runtime:bool,
    external_side_effect_observable:bool,
    acceptance_criteria_defined:bool,
)->dict[str,Any]:
    if rule not in fix_verification.RULE_VERIFICATION_SPECS:
        raise FixEligibilityError(f"unknown rule: {rule}")

    spec=fix_verification.RULE_VERIFICATION_SPECS[rule]
    if spec.mode=="static_only":
        return {
            "eligible_for_verified_repair":True,
            "reason":"This rule can be conclusively verified from a newly sanitized artifact.",
            "required_assertions":[],
        }

    missing=[]
    if not safe_test_environment:
        missing.append("safe_test_environment")
    if not pcflows_can_observe_runtime:
        missing.append("pcflows_can_observe_runtime")
    if not external_side_effect_observable:
        missing.append("external_side_effect_observable")
    if not acceptance_criteria_defined:
        missing.append("acceptance_criteria_defined")

    return {
        "eligible_for_verified_repair":not missing,
        "reason":(
            "All prerequisites exist for a bounded verified-repair commitment."
            if not missing else
            "Do not sell or promise a verified repair for this issue until every prerequisite exists."
        ),
        "missing":missing,
        "required_assertions":list(spec.required_assertions),
        "verification_goal":spec.verification_goal,
    }
