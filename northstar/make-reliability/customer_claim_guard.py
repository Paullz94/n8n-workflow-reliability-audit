#!/usr/bin/env python3
"""Block unsupported success/fix claims from ordinary PCFlows customer reports."""
from __future__ import annotations

import re


class ClaimGuardError(ValueError):
    pass


UNSUPPORTED_PATTERNS = (
    re.compile(r"\b100%\s+(?:fixed|safe|reliable|correct)\b", re.I),
    re.compile(r"\b(?:issue|problem|bug)\s+(?:is|has been)\s+(?:fully\s+)?fixed\b", re.I),
    re.compile(r"\bguaranteed\s+(?:fix|fixed|safe|correct|reliable)\b", re.I),
    re.compile(r"\bproduction[- ]ready\s+(?:and\s+)?(?:safe|verified|guaranteed)?\b", re.I),
    re.compile(r"\bno\s+(?:remaining\s+)?(?:defects|bugs|risk)\b", re.I),
)


def find_unsupported_claims(text: str) -> list[str]:
    hits=[]
    for pattern in UNSUPPORTED_PATTERNS:
        match=pattern.search(text or "")
        if match:
            hits.append(match.group(0))
    return hits


def assert_safe_report(text: str) -> None:
    hits=find_unsupported_claims(text)
    if hits:
        raise ClaimGuardError(
            "unsupported customer-facing success claim(s): " + ", ".join(sorted(set(hits)))
        )
