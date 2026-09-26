#!/usr/bin/env python3
"""Autonomous containment policy for PCFlows data/AI safety incidents."""
from __future__ import annotations

from typing import Any


class IncidentPolicyError(ValueError):
    pass


def decide_incident_action(event:dict[str,Any])->dict[str,Any]:
    if not isinstance(event,dict):
        raise IncidentPolicyError("event must be an object")

    kind=str(event.get("kind") or "").strip()

    if kind=="sensitive_data_detected_pre_delivery":
        return {
            "halt_case":True,
            "quarantine_artifacts":True,
            "outbound_delivery_allowed":False,
            "owner_escalation":False,
            "action":"request_resanitized_input",
            "reason":"Sensitive/customer data was detected before delivery; contain automatically and request a sanitized replacement.",
        }

    if kind=="cross_case_binding_mismatch":
        return {
            "halt_case":True,
            "quarantine_artifacts":True,
            "outbound_delivery_allowed":False,
            "owner_escalation":False,
            "action":"freeze_affected_cases_and_investigate",
            "reason":"A cross-case binding mismatch must stop automation before any customer output is sent.",
        }

    if kind=="confirmed_cross_customer_exposure":
        return {
            "halt_case":True,
            "quarantine_artifacts":True,
            "outbound_delivery_allowed":False,
            "owner_escalation":True,
            "action":"privacy_incident_escalation",
            "reason":"Confirmed cross-customer exposure may create legal/notification obligations and requires proprietor review after automatic containment.",
        }

    if kind=="unauthorized_production_write_attempt":
        return {
            "halt_case":True,
            "quarantine_artifacts":False,
            "outbound_delivery_allowed":False,
            "owner_escalation":False,
            "action":"block_write_and_preserve_audit_trail",
            "reason":"A production write without valid case/customer authorization is blocked; no production change is permitted.",
        }

    if kind=="production_rollback_failed":
        return {
            "halt_case":True,
            "quarantine_artifacts":False,
            "outbound_delivery_allowed":False,
            "owner_escalation":True,
            "action":"critical_repair_incident",
            "reason":"Rollback failure may leave customer production in an uncertain state and requires immediate human escalation.",
        }

    if kind=="ai_output_policy_violation":
        return {
            "halt_case":False,
            "quarantine_artifacts":False,
            "outbound_delivery_allowed":False,
            "owner_escalation":False,
            "action":"discard_ai_output_and_regenerate_from_bounded_packet",
            "reason":"Unsupported AI output is non-authoritative and must be discarded rather than delivered.",
        }

    raise IncidentPolicyError(f"unsupported incident kind: {kind!r}")
