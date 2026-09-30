#!/usr/bin/env python3
"""Detect literal customer/sensitive data before PCFlows AI or delivery processing.

This is intentionally conservative. It does not try to identify every possible
form of personal data. It blocks several high-risk literal classes and keeps
raw matched values out of returned diagnostics.
"""
from __future__ import annotations

import re
from typing import Any


class SensitiveDataError(ValueError):
    pass


EMAIL_RE=re.compile(r"(?i)(?<![\w.+-])([A-Z0-9._%+-]+)@([A-Z0-9.-]+\.[A-Z]{2,})(?![\w.-])")
E164_RE=re.compile(r"(?<!\d)\+\d{8,15}(?!\d)")
IBAN_RE=re.compile(r"(?i)(?<![A-Z0-9])([A-Z]{2}\d{2}[A-Z0-9]{11,30})(?![A-Z0-9])")
CARD_CANDIDATE_RE=re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")
JWT_RE=re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")

SYNTHETIC_EMAIL_DOMAINS={"example.com","example.org","example.net","example.invalid","test.invalid"}


def _luhn(number:str)->bool:
    digits=[int(x) for x in number if x.isdigit()]
    if not 13 <= len(digits) <= 19:
        return False
    total=0
    parity=len(digits)%2
    for i,digit in enumerate(digits):
        if i%2==parity:
            digit*=2
            if digit>9:
                digit-=9
        total+=digit
    return total%10==0


def _looks_synthetic(value:str)->bool:
    upper=value.upper()
    return (
        "SYN-" in upper
        or "[REDACTED]" in upper
        or "{{" in value and "}}" in value
        or "example.invalid" in value.lower()
    )


def _classify_string(value:str)->set[str]:
    if not value or _looks_synthetic(value):
        return set()
    kinds=set()
    for match in EMAIL_RE.finditer(value):
        domain=match.group(2).lower()
        if domain not in SYNTHETIC_EMAIL_DOMAINS:
            kinds.add("email_literal")
    if E164_RE.search(value):
        kinds.add("phone_literal")
    if IBAN_RE.search(value.replace(" ","")):
        kinds.add("iban_literal")
    for match in CARD_CANDIDATE_RE.finditer(value):
        if _luhn(match.group(0)):
            kinds.add("payment_card_literal")
            break
    if JWT_RE.search(value):
        kinds.add("jwt_literal")
    return kinds


def inspect_sensitive_literals(value:Any)->list[dict[str,str]]:
    findings=[]

    def walk(node:Any,path:str)->None:
        if isinstance(node,str):
            for kind in sorted(_classify_string(node)):
                findings.append({"path":path,"kind":kind})
        elif isinstance(node,dict):
            for key,val in node.items():
                walk(val,f"{path}.{key}" if path else str(key))
        elif isinstance(node,list):
            for index,val in enumerate(node):
                walk(val,f"{path}[{index}]")

    walk(value,"")
    return findings


def assert_no_sensitive_literals(value:Any,label:str)->None:
    findings=inspect_sensitive_literals(value)
    if findings:
        summary=", ".join(f"{f['kind']} at {f['path']}" for f in findings[:8])
        raise SensitiveDataError(
            f"{label} contains literal customer/sensitive data ({summary}). "
            "Replace it with synthetic/abstract data before PCFlows processing."
        )
