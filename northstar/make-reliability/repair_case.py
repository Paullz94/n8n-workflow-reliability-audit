#!/usr/bin/env python3
"""Lifecycle for a future PCFlows Verified Repair case."""
from __future__ import annotations

from typing import Any

import resolution_contract


class RepairCaseError(ValueError):
    pass


def evaluate_case(contracts:list[dict[str,Any]])->dict[str,Any]:
    if not contracts:
        raise RepairCaseError("repair case requires at least one issue contract")

    open_items=[x for x in contracts if x.get("customer_status")!="closed_verified"]
    return {
        "issue_count":len(contracts),
        "closed_verified_count":len(contracts)-len(open_items),
        "open_count":len(open_items),
        "case_status":"closed_verified" if resolution_contract.all_closed_verified(contracts) else "open",
        "can_tell_customer_complete":resolution_contract.all_closed_verified(contracts),
        "open_rules":[x.get("rule") for x in open_items],
    }
