#!/usr/bin/env python3
"""Per-finding definition-of-done contract for PCFlows remediation."""
from __future__ import annotations

from typing import Any

import fix_verification


class ResolutionContractError(ValueError):
    pass


def build_resolution_contract(
    *,
    rule:str,
    module_id:int|str|None,
    business_description:str,
)->dict[str,Any]:
    if rule not in fix_verification.RULE_VERIFICATION_SPECS:
        raise ResolutionContractError(f"unknown rule: {rule}")
    description=(business_description or "").strip()
    if not description:
        raise ResolutionContractError("business_description is required")

    spec=fix_verification.RULE_VERIFICATION_SPECS[rule]
    return {
        "rule":rule,
        "module_id":module_id,
        "business_description":description[:500],
        "verification_mode":spec.mode,
        "verification_goal":spec.verification_goal,
        "required_assertions":list(spec.required_assertions),
        "close_condition":(
            "Revised sanitized artifact clears the structural rule."
            if spec.mode=="static_only"
            else "Structural signal is cleared and every required assertion passes in independently observable synthetic runtime evidence."
        ),
        "customer_status":"open",
    }


def evaluate_resolution_contract(
    contract:dict[str,Any],
    *,
    still_present_after:bool,
    evidence:dict[str,Any]|None=None,
)->dict[str,Any]:
    rule=str(contract.get("rule") or "")
    status=fix_verification.resolution_status(
        rule=rule,
        still_present_after=still_present_after,
        evidence=evidence,
    )
    return {
        **contract,
        "customer_status":"closed_verified" if status["verified_fixed"] else "open",
        "proof_status":status["status"],
        "proof_language":status["customer_language"],
        "evidence":status.get("evidence"),
    }


def all_closed_verified(items:list[dict[str,Any]])->bool:
    return bool(items) and all(item.get("customer_status")=="closed_verified" for item in items)
