#!/usr/bin/env python3
"""Per-case namespace and cross-customer isolation helpers for PCFlows."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any


CASE_RE=re.compile(r"^pcfcase_[a-f0-9]{20}$")


class CaseIsolationError(ValueError):
    pass


def case_scope_id(order_ref:str)->str:
    value=(order_ref or "").strip()
    if not value:
        raise CaseIsolationError("order_ref is required")
    digest=hashlib.sha256(("pcflows-case:"+value).encode("utf-8")).hexdigest()[:20]
    return "pcfcase_"+digest


def assert_case_scope_id(value:str)->str:
    if not CASE_RE.fullmatch(value or ""):
        raise CaseIsolationError("invalid PCFlows case scope id")
    return value


def assert_document_bound_to_case(document:dict[str,Any],expected_case_id:str)->None:
    assert_case_scope_id(expected_case_id)
    if not isinstance(document,dict):
        raise CaseIsolationError("case-bound document must be an object")
    actual=str(document.get("case_scope_id") or "")
    if actual != expected_case_id:
        raise CaseIsolationError("cross-case document binding rejected")


def safe_case_dir(root:Path,case_id:str)->Path:
    assert_case_scope_id(case_id)
    root_resolved=root.resolve()
    target=(root_resolved/case_id).resolve()
    if target.parent != root_resolved:
        raise CaseIsolationError("case directory escaped configured root")
    return target
