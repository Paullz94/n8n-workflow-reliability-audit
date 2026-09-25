#!/usr/bin/env python3
"""Standard PCFlows synthetic runtime result contract.

A connected Make test scenario can expose a small non-sensitive result object so
PCFlows can independently evaluate acceptance criteria without reading customer
production payloads.
"""
from __future__ import annotations

from typing import Any


class RuntimeContractError(ValueError):
    pass


ALLOWED_RESULT_KEYS={
    "test_id",
    "business_key",
    "status",
    "side_effect_ids",
    "side_effect_count",
    "duplicate_side_effect_count",
    "failure_injected",
    "failure_observable",
    "recovery_succeeded",
    "missing_action_observable",
    "silent_success_prevented",
    "fallback_used",
    "fallback_distinguishable",
    "false_success_prevented",
    "partial_state_identified",
    "committed_state_identified",
    "reconciliation_succeeded",
    "compensation_or_reconciliation_succeeded",
    "rollback_boundary_observed",
    "remaining_state_matches_design",
    "nonmatching_event_tested",
    "skip_observable",
    "missing_work_not_misreported_complete",
    "concurrent_test_executed",
    "final_state_deterministic",
    "failed_work_locatable",
    "resume_or_replay_succeeded",
    "failed_work_recoverable",
    "unintended_data_loss_count",
    "correlation_available",
    "affected_event_identifiable",
    "sensitive_payload_exposed",
    "human_handoff",
    "automated_actions_after_handoff",
    "final_state",
    "required_resources",
    "missing_required_resources",
    "invoice_total",
    "paid_amount",
    "marked_fully_paid",
    "write_performed",
    "invalid_input_rejected",
}


def sanitize_result(raw:dict[str,Any])->dict[str,Any]:
    if not isinstance(raw,dict):
        raise RuntimeContractError("runtime result must be an object")
    clean={}
    for key in ALLOWED_RESULT_KEYS:
        if key not in raw:
            continue
        value=raw[key]
        if isinstance(value,(str,int,float,bool)) or value is None:
            clean[key]=value
        elif key in {"side_effect_ids","required_resources","missing_required_resources"} and isinstance(value,list):
            clean[key]=[str(x)[:160] for x in value[:50]]
    return clean


def assert_duplicate_replay(first:dict[str,Any],second:dict[str,Any])->dict[str,Any]:
    a=sanitize_result(first); b=sanitize_result(second)
    ids1=[x for x in a.get("side_effect_ids",[]) if x]
    ids2=[x for x in b.get("side_effect_ids",[]) if x]
    same_key=bool(a.get("business_key")) and a.get("business_key")==b.get("business_key")
    combined=set(ids1+ids2)
    explicit_counts=[x for x in (a.get("side_effect_count"),b.get("side_effect_count")) if isinstance(x,int)]
    count_ok=(len(combined)==1 and bool(combined))
    if explicit_counts:
        count_ok=count_ok and all(x==1 for x in explicit_counts)
    return {
        "duplicate_replay_executed":True,
        "same_business_key":same_key,
        "intended_side_effect_count_one":same_key and count_ok,
    }


def assert_failure_recovery(result:dict[str,Any])->dict[str,bool]:
    r=sanitize_result(result)
    return {
        "failure_injected":r.get("failure_injected") is True,
        "failure_observable":r.get("failure_observable") is True,
        "recovery_path_succeeds":r.get("recovery_succeeded") is True,
        "duplicate_side_effects_zero":r.get("duplicate_side_effect_count")==0,
    }


def assert_human_handoff(result:dict[str,Any])->dict[str,bool]:
    r=sanitize_result(result)
    return {
        "human_handoff_tested":r.get("human_handoff") is True,
        "automated_actions_after_handoff_zero":r.get("automated_actions_after_handoff")==0,
    }


def assert_partial_payment(result:dict[str,Any])->dict[str,bool]:
    r=sanitize_result(result)
    total=r.get("invoice_total")
    paid=r.get("paid_amount")
    valid_amounts=isinstance(total,(int,float)) and isinstance(paid,(int,float)) and paid < total
    return {
        "partial_payment_tested":valid_amounts,
        "not_marked_fully_paid":valid_amounts and r.get("marked_fully_paid") is False,
    }


def assert_invalid_ai_output(result:dict[str,Any])->dict[str,bool]:
    r=sanitize_result(result)
    return {
        "malformed_output_tested":True,
        "invalid_input_rejected":r.get("invalid_input_rejected") is True,
        "unsafe_write_prevented":r.get("write_performed") is False,
    }


def assert_required_onboarding_resources(result:dict[str,Any])->dict[str,bool]:
    r=sanitize_result(result)
    required=r.get("required_resources")
    missing=r.get("missing_required_resources")
    return {
        "required_resources_tested":isinstance(required,list) and bool(required),
        "missing_required_resources_zero":isinstance(missing,list) and len(missing)==0,
    }


def assert_skip_visibility(result:dict[str,Any])->dict[str,bool]:
    r=sanitize_result(result)
    return {
        "failure_injected":r.get("failure_injected") is True,
        "missing_action_observable":r.get("missing_action_observable") is True,
        "silent_success_prevented":r.get("silent_success_prevented") is True,
    }


def assert_resume_fallback(result:dict[str,Any])->dict[str,bool]:
    r=sanitize_result(result)
    return {
        "failure_injected":r.get("failure_injected") is True,
        "fallback_distinguishable":r.get("fallback_distinguishable") is True,
        "false_success_prevented":r.get("false_success_prevented") is True,
    }


def assert_partial_state_reconciliation(result:dict[str,Any])->dict[str,bool]:
    r=sanitize_result(result)
    return {
        "failure_injected":r.get("failure_injected") is True,
        "partial_state_identified":r.get("partial_state_identified") is True,
        "reconciliation_path_succeeds":r.get("reconciliation_succeeded") is True,
    }


def assert_committed_state_reconciliation(result:dict[str,Any])->dict[str,bool]:
    r=sanitize_result(result)
    return {
        "failure_injected":r.get("failure_injected") is True,
        "committed_state_identified":r.get("committed_state_identified") is True,
        "compensation_or_reconciliation_succeeds":r.get("compensation_or_reconciliation_succeeded") is True,
    }


def assert_rollback_boundary(result:dict[str,Any])->dict[str,bool]:
    r=sanitize_result(result)
    return {
        "failure_injected":r.get("failure_injected") is True,
        "rollback_boundary_observed":r.get("rollback_boundary_observed") is True,
        "remaining_state_matches_design":r.get("remaining_state_matches_design") is True,
    }


def assert_filter_skip(result:dict[str,Any])->dict[str,bool]:
    r=sanitize_result(result)
    return {
        "nonmatching_event_tested":r.get("nonmatching_event_tested") is True,
        "skip_observable":r.get("skip_observable") is True,
        "missing_work_not_misreported_complete":r.get("missing_work_not_misreported_complete") is True,
    }


def assert_concurrency(result:dict[str,Any])->dict[str,bool]:
    r=sanitize_result(result)
    return {
        "concurrent_test_executed":r.get("concurrent_test_executed") is True,
        "final_state_deterministic":r.get("final_state_deterministic") is True,
        "duplicate_side_effects_zero":r.get("duplicate_side_effect_count")==0,
    }


def assert_failed_work_replay(result:dict[str,Any])->dict[str,bool]:
    r=sanitize_result(result)
    return {
        "failure_injected":r.get("failure_injected") is True,
        "failed_work_locatable":r.get("failed_work_locatable") is True,
        "resume_or_replay_succeeds":r.get("resume_or_replay_succeeded") is True,
        "duplicate_side_effects_zero":r.get("duplicate_side_effect_count")==0,
    }


def assert_data_loss_recovery(result:dict[str,Any])->dict[str,bool]:
    r=sanitize_result(result)
    return {
        "failure_injected":r.get("failure_injected") is True,
        "failed_work_recoverable":r.get("failed_work_recoverable") is True,
        "unintended_data_loss_zero":r.get("unintended_data_loss_count")==0,
    }


def assert_privacy_safe_observability(result:dict[str,Any])->dict[str,bool]:
    r=sanitize_result(result)
    return {
        "failure_injected":r.get("failure_injected") is True,
        "correlation_available":r.get("correlation_available") is True,
        "affected_event_identifiable":r.get("affected_event_identifiable") is True,
        "sensitive_payload_not_exposed":r.get("sensitive_payload_exposed") is False,
    }
