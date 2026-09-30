#!/usr/bin/env python3
"""Single entry gate for future PCFlows Verified Repair requests."""
from __future__ import annotations

from typing import Any

import fix_eligibility
import repair_scope_gate


class VerifiedRepairIntakeError(ValueError):
    pass


def qualify(
    *,
    rule:str,
    request:dict[str,Any],
)->dict[str,Any]:
    scope=repair_scope_gate.qualify_repair_request(request)
    if scope["verified_repair_eligible"] is not True:
        return {
            "route":scope["route"],
            "verified_repair_eligible":False,
            "scope":scope,
            "fix_eligibility":None,
        }

    technical=fix_eligibility.assess_fix_eligibility(
        rule=rule,
        safe_test_environment=request.get("safe_test_environment") is True,
        pcflows_can_observe_runtime=request.get("pcflows_can_observe_runtime") is True,
        external_side_effect_observable=request.get("external_side_effect_observable") is True,
        acceptance_criteria_defined=request.get("acceptance_criteria_defined") is True,
    )
    return {
        "route":(
            "verified_repair_candidate"
            if technical["eligible_for_verified_repair"]
            else "audit_or_diagnostic_only"
        ),
        "verified_repair_eligible":technical["eligible_for_verified_repair"],
        "scope":scope,
        "fix_eligibility":technical,
    }
