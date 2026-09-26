#!/usr/bin/env python3
"""Generate fixed synthetic runtime acceptance plans for PCFlows specialist modes."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

import vertical_packs


PLANS: dict[str, list[dict[str, Any]]] = {
    "lead_flow": [
        {
            "test_id":"lead_duplicate_replay",
            "evaluator":"duplicate_replay",
            "input":{"pcflows_case":"SYN-LEAD-001","business_key":"SYN-LEAD-001"},
            "production_safe":True,
        },
        {
            "test_id":"lead_route_race",
            "evaluator":"concurrent_pair",
            "input":{"pcflows_case":"SYN-LEAD-RACE-001","business_key":"SYN-LEAD-RACE-001"},
            "production_safe":True,
        },
        {
            "test_id":"lead_downstream_failure",
            "evaluator":"failure_recovery",
            "input":{"pcflows_case":"SYN-LEAD-FAIL-001","inject_failure":True},
            "production_safe":True,
        },
        {
            "test_id":"lead_followup_stop",
            "evaluator":"human_handoff",
            "input":{"pcflows_case":"SYN-LEAD-HANDOFF-001","human_handoff":True},
            "production_safe":True,
        },
    ],
    "invoice_payment": [
        {
            "test_id":"invoice_duplicate_replay",
            "evaluator":"duplicate_replay",
            "input":{"pcflows_case":"SYN-INV-001","business_key":"SYN-INV-001"},
            "production_safe":True,
        },
        {
            "test_id":"payment_partial",
            "evaluator":"partial_payment",
            "input":{"pcflows_case":"SYN-PAY-001","invoice_total":2000,"paid_amount":500},
            "production_safe":True,
        },
        {
            "test_id":"customer_match_collision",
            "evaluator":"customer_match",
            "input":{"pcflows_case":"SYN-CUST-001","expected_customer_id":"SYN-CUSTOMER-A","similar_customer_id":"SYN-CUSTOMER-B"},
            "production_safe":True,
        },
        {
            "test_id":"finance_half_failure",
            "evaluator":"partial_state_reconciliation",
            "input":{"pcflows_case":"SYN-FIN-FAIL-001","inject_failure_after_first_write":True},
            "production_safe":True,
        },
    ],
    "ai_guardrails": [
        {
            "test_id":"ai_malformed_output",
            "evaluator":"invalid_ai_output",
            "input":{"pcflows_case":"SYN-AI-BAD-001","inject_malformed_ai_output":True},
            "production_safe":True,
        },
        {
            "test_id":"ai_low_confidence",
            "evaluator":"ambiguous_review",
            "input":{"pcflows_case":"SYN-AI-AMB-001","inject_ambiguous_ai_input":True},
            "production_safe":True,
        },
        {
            "test_id":"ai_human_handoff",
            "evaluator":"human_handoff",
            "input":{"pcflows_case":"SYN-AI-HANDOFF-001","human_handoff":True},
            "production_safe":True,
        },
        {
            "test_id":"ai_retry_effect",
            "evaluator":"duplicate_replay",
            "input":{"pcflows_case":"SYN-AI-REPLAY-001","business_key":"SYN-AI-REPLAY-001"},
            "production_safe":True,
        },
    ],
    "client_onboarding": [
        {
            "test_id":"onboarding_duplicate_replay",
            "evaluator":"duplicate_replay",
            "input":{"pcflows_case":"SYN-ONB-001","business_key":"SYN-ONB-001"},
            "production_safe":True,
        },
        {
            "test_id":"onboarding_partial_failure",
            "evaluator":"partial_state_reconciliation",
            "input":{"pcflows_case":"SYN-ONB-FAIL-001","inject_failure_after_first_write":True},
            "production_safe":True,
        },
        {
            "test_id":"onboarding_required_step",
            "evaluator":"onboarding_resources",
            "input":{"pcflows_case":"SYN-ONB-REQ-001","verify_required_resources":True},
            "production_safe":True,
        },
        {
            "test_id":"onboarding_handoff",
            "evaluator":"human_handoff",
            "input":{"pcflows_case":"SYN-ONB-HANDOFF-001","human_handoff":True},
            "production_safe":True,
        },
    ],
}


class RuntimePlanError(ValueError):
    pass


def get_runtime_plan(pack_id:str)->list[dict[str,Any]]:
    if pack_id not in PLANS:
        raise RuntimePlanError(f"no runtime plan for pack: {pack_id}")
    expected={x["id"] for x in vertical_packs.get_pack(pack_id).acceptance_tests}
    actual={x["test_id"] for x in PLANS[pack_id]}
    if expected!=actual:
        raise RuntimePlanError(
            f"runtime plan drift for {pack_id}: missing={sorted(expected-actual)} extra={sorted(actual-expected)}"
        )
    return deepcopy(PLANS[pack_id])


def validate_all_plans()->None:
    expected=set(vertical_packs.PACKS)
    actual=set(PLANS)
    if expected!=actual:
        raise RuntimePlanError(
            f"specialist/runtime-plan drift: missing={sorted(expected-actual)} extra={sorted(actual-expected)}"
        )
    for pack_id in sorted(expected):
        get_runtime_plan(pack_id)


validate_all_plans()
