#!/usr/bin/env python3
"""Policy-bound support routing for routine PCFlows customer messages."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SupportRoute:
    intent: str
    autonomous: bool
    response_key: str
    action: str


ROUTES = {
    "price": SupportRoute("price", True, "pricing", "answer_fixed_scope_price"),
    "scope": SupportRoute("scope", True, "scope", "answer_scope"),
    "privacy": SupportRoute("privacy", True, "privacy", "answer_privacy_and_sanitization"),
    "send_files": SupportRoute("send_files", True, "files", "send_intake_instructions"),
    "rescan": SupportRoute("rescan", True, "rescan", "send_rescan_instructions"),
    "implementation": SupportRoute("implementation", True, "implementation", "explain_audit_only_scope"),
    "refund_policy": SupportRoute("refund_policy", True, "refund", "evaluate_deterministic_refund_policy"),
    "security_certification": SupportRoute("security_certification", True, "certification", "decline_certification_claim"),
    "legal_or_tax": SupportRoute("legal_or_tax", True, "legal", "decline_professional_legal_tax_advice"),
    "unknown": SupportRoute("unknown", True, "clarify", "ask_one_bounded_clarifying_question"),
}


KEYWORDS = {
    "price": ("price", "cost", "€149", "149", "how much"),
    "privacy": ("credential", "api key", "secret", "privacy", "webhook url", "data"),
    "send_files": ("send blueprint", "upload blueprint", "where do i send", "intake"),
    "rescan": ("rescan", "re-scan", "after fix", "after remediation"),
    "implementation": ("fix it for me", "implement", "build it", "change my scenario"),
    "refund_policy": ("refund", "money back", "cancel order", "duplicate charge"),
    "security_certification": ("certify", "certification", "security audit", "soc 2", "iso 27001"),
    "legal_or_tax": ("legal advice", "tax advice", "vat advice", "accounting advice"),
    "scope": ("what do i get", "included", "scope", "what is covered"),
}


def route_message(subject: str, body: str) -> SupportRoute:
    text = f"{subject} {body}".lower()
    hits = []
    for intent, words in KEYWORDS.items():
        count = sum(1 for word in words if word in text)
        if count:
            hits.append((count, intent))
    if not hits:
        return ROUTES["unknown"]
    hits.sort(key=lambda x: (-x[0], x[1]))
    return ROUTES[hits[0][1]]


def render_reply(route: SupportRoute) -> str:
    replies = {
        "pricing": (
            "PCFlows uses fixed launch pricing: €0 Reliability Preflight, €79 Focused Risk Check, €149 Data Integrity Audit, "
            "and €399 Portfolio / Release QA for up to three related scenarios. Paid checkout is currently paused until registration is complete."
        ),
        "scope": (
            "PCFlows uses fixed scopes: free local preflight; €79 one-focus check; €149 full one-scenario audit with one re-scan; "
            "and €399 Portfolio / Release QA for up to three related scenarios. Specialist Lead Flow, Invoice/Payment and AI Guardrails "
            "modes are included within the €149 audit when context matches. Production implementation is not silently included."
        ),
        "privacy": (
            "Please do not send production credentials, passwords, API keys, private Make webhook URLs, customer records "
            "or unnecessary personal data. The free preflight runs locally in the browser."
        ),
        "files": (
            "Please send one sanitized Make.com blueprint JSON plus the PCFlows local intake JSON, keeping the Stripe order "
            "reference in the subject. Do not include credentials or customer records."
        ),
        "rescan": (
            "The fixed-scope pilot includes one re-scan of the same scenario after remediation. Send the revised sanitized "
            "blueprint under the same order reference; the comparison reports resolved, remaining and new static findings."
        ),
        "implementation": (
            "The current PCFlows product is an audit and verification service, not an open-ended implementation retainer. "
            "The report identifies what to change and how to verify it; implementation is not silently bundled into the fixed price."
        ),
        "refund": (
            "Refunds follow the published fixed-scope policy. Duplicate charges, out-of-scope cancellation before substantive "
            "delivery and material non-delivery can be handled through the provider; other cases are evaluated against the documented terms."
        ),
        "certification": (
            "PCFlows is not a security/compliance certification service. The audit is technical static reliability/data-integrity analysis "
            "and cannot certify SOC 2, ISO 27001, legal compliance or the absence of defects."
        ),
        "legal": (
            "PCFlows does not provide individualized legal, tax or accounting advice. The reliability audit can explain technical workflow "
            "behavior, but professional legal/tax treatment should be confirmed with the appropriate adviser or authority."
        ),
        "clarify": (
            "I can help with the PCFlows free preflight, fixed-scope audit, sanitization, delivery or re-scan. "
            "Which of those are you trying to do?"
        ),
    }
    return replies[route.response_key]
