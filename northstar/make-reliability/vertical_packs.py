#!/usr/bin/env python3
"""Problem-specific PCFlows audit packs layered on the deterministic core.

A pack does not invent new runtime evidence. It translates existing findings
and allowlisted business context into buyer-specific priorities and synthetic
acceptance tests.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import audit_make
import report_builder


@dataclass(frozen=True)
class Pack:
    id: str
    name: str
    buyer_problem: str
    priority_rules: tuple[str, ...]
    acceptance_tests: tuple[dict[str, str], ...]
    context_prompts: tuple[str, ...]


PACKS: dict[str, Pack] = {
    "lead_flow": Pack(
        id="lead_flow",
        name="Lead Flow Reliability Audit",
        buyer_problem="Leads can disappear, duplicate, route to the wrong owner, or receive follow-ups after a human/reply should have stopped automation.",
        priority_rules=(
            "retrying-write-idempotency-review",
            "http-write-idempotency-review",
            "concurrency-review",
            "filtered-write-silent-skip-review",
            "write-without-error-handler",
            "write-skip-handler-data-loss-review",
            "write-resume-handler-silent-success-review",
        ),
        acceptance_tests=(
            {
                "id":"lead_duplicate_replay",
                "problem":"Duplicate lead/contact creation",
                "test":"Submit the same synthetic lead twice with the same stable business key.",
                "pass":"Only one intended CRM lead/contact exists and downstream outreach is not duplicated.",
            },
            {
                "id":"lead_route_race",
                "problem":"Two owners or routes claim the same lead",
                "test":"Submit two near-simultaneous synthetic events for the same lead.",
                "pass":"Ownership/routing is deterministic and only the intended route performs state-changing actions.",
            },
            {
                "id":"lead_downstream_failure",
                "problem":"Lead accepted but downstream action silently fails",
                "test":"Force a safe synthetic CRM/SMS/email failure after lead intake.",
                "pass":"The failed lead remains observable/recoverable and is not falsely marked complete.",
            },
            {
                "id":"lead_followup_stop",
                "problem":"Automation keeps following up after reply/booking/human takeover",
                "test":"Use a synthetic lead that transitions to a stop/handoff state during the sequence.",
                "pass":"No later automated follow-up is emitted after the stop/handoff condition.",
            },
        ),
        context_prompts=(
            "What is the stable lead identity (email, CRM id, form submission id, etc.)?",
            "What event must stop automated follow-up?",
            "Can two sales owners ever legitimately receive the same lead?",
            "Which lead actions must happen exactly once?",
        ),
    ),
    "invoice_payment": Pack(
        id="invoice_payment",
        name="Invoice & Payment Sync Audit",
        buyer_problem="CRM, invoicing and payment systems can disagree, duplicate invoices, mis-match customers, or treat partial payment as fully paid.",
        priority_rules=(
            "retrying-write-idempotency-review",
            "http-write-idempotency-review",
            "concurrency-review",
            "write-without-error-handler",
            "write-commit-partial-state-review",
            "rollback-limited-by-autocommit-review",
            "incomplete-executions-disabled-review",
            "data-loss-enabled",
        ),
        acceptance_tests=(
            {
                "id":"invoice_duplicate_replay",
                "problem":"Duplicate invoice creation after retry/replay",
                "test":"Replay the same synthetic invoice request with the same source document/business key.",
                "pass":"Exactly one invoice is created or the existing invoice is deterministically reused.",
            },
            {
                "id":"payment_partial",
                "problem":"Partial payment incorrectly closes the invoice/deal",
                "test":"Apply a synthetic payment lower than the invoice total.",
                "pass":"Outstanding balance remains visible and the business state is not marked fully paid.",
            },
            {
                "id":"customer_match_collision",
                "problem":"Payment/invoice is attached to the wrong customer",
                "test":"Use two synthetic customers with similar names but distinct stable ids.",
                "pass":"Matching uses the intended stable key and cannot resolve to the wrong customer by name alone.",
            },
            {
                "id":"finance_half_failure",
                "problem":"One system updates while the other fails",
                "test":"Force a failure after the first state-changing system update.",
                "pass":"Partial state is detectable and there is an explicit reconciliation/recovery route.",
            },
        ),
        context_prompts=(
            "Which system is authoritative for customer identity?",
            "Which system is authoritative for invoice/payment status?",
            "What stable key links CRM, invoice and payment records?",
            "How should partial payments, refunds and cancellations change status?",
        ),
    ),
    "ai_guardrails": Pack(
        id="ai_guardrails",
        name="AI Workflow Guardrails Audit",
        buyer_problem="LLM output can be malformed, uncertain or simply wrong while downstream automation still writes to CRM, finance, email or customer-facing systems.",
        priority_rules=(
            "filtered-write-silent-skip-review",
            "write-resume-handler-silent-success-review",
            "write-without-error-handler",
            "retrying-write-idempotency-review",
            "http-write-idempotency-review",
            "concurrency-review",
        ),
        acceptance_tests=(
            {
                "id":"ai_malformed_output",
                "problem":"AI returns malformed/unexpected structured output",
                "test":"Feed a synthetic AI response with missing/null/wrong-type required fields.",
                "pass":"The workflow rejects or quarantines the result before any high-impact write.",
            },
            {
                "id":"ai_low_confidence",
                "problem":"Uncertain AI result is treated as fact",
                "test":"Use a synthetic ambiguous input that should require review.",
                "pass":"The automation routes to explicit review/fallback rather than silently committing the uncertain result.",
            },
            {
                "id":"ai_human_handoff",
                "problem":"Automation continues after a human takes ownership",
                "test":"Switch a synthetic case into a human-owned/approved state mid-flow.",
                "pass":"Automated customer-facing or state-changing actions stop at the documented handoff boundary.",
            },
            {
                "id":"ai_retry_effect",
                "problem":"Retry duplicates an AI-triggered external action",
                "test":"Replay the same validated AI decision/event twice.",
                "pass":"Only one intended external side effect is created.",
            },
        ),
        context_prompts=(
            "Which downstream actions can materially affect a customer, payment, CRM state or document?",
            "Which AI fields are required and what types/formats are valid?",
            "Which decisions require human approval?",
            "What event freezes automation after human takeover?",
        ),
    ),
}


def get_pack(pack_id: str) -> Pack:
    try:
        return PACKS[pack_id]
    except KeyError as exc:
        raise ValueError(f"Unknown PCFlows pack: {pack_id}") from exc


def build_pack_plan(
    pack_id: str,
    findings: list[audit_make.Finding],
    raw_context: dict[str, Any] | None,
) -> dict[str, Any]:
    pack = get_pack(pack_id)
    context = report_builder.sanitize_context(raw_context or {})
    priority = {rule: idx for idx, rule in enumerate(pack.priority_rules)}
    matching = [f for f in findings if f.rule in priority]
    matching.sort(key=lambda f: (priority[f.rule], -audit_make.SEVERITY_ORDER[f.severity], f.path or ""))

    return {
        "pack_id": pack.id,
        "pack_name": pack.name,
        "buyer_problem": pack.buyer_problem,
        "context": context,
        "prioritized_findings": [
            {
                "rule": f.rule,
                "severity": f.severity,
                "module": f.module,
                "module_id": f.module_id,
                "path": f.path,
                "evidence": f.message,
            }
            for f in matching
        ],
        "acceptance_tests": list(pack.acceptance_tests),
        "context_prompts": list(pack.context_prompts),
        "static_limit": "Pack priorities and tests do not prove a live defect; use sanitized/synthetic execution evidence to verify.",
    }
