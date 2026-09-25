#!/usr/bin/env python3
"""Final PCFlows Verified Repair closure gate."""
from __future__ import annotations

from typing import Any

import audit_make
import compare_rescan
import pack_acceptance_verification
import resolution_contract


class RepairClosureError(ValueError):
    pass


def _finding_present(
    findings:list[audit_make.Finding],
    rule:str,
    module_id:int|str|None,
)->bool:
    for finding in findings:
        if finding.rule!=rule:
            continue
        if module_id is None:
            if finding.module_id is None:
                return True
        elif str(finding.module_id)==str(module_id):
            return True
    return False


def _binding_map(bindings:list[dict[str,Any]])->dict[tuple[str,str],str]:
    out={}
    for item in bindings:
        if not isinstance(item,dict):
            continue
        rule=str(item.get("rule") or "")
        module_id="" if item.get("module_id") is None else str(item.get("module_id"))
        test_id=str(item.get("test_id") or "")
        if rule and test_id:
            out[(rule,module_id)]=test_id
    return out


def close_repair_case(
    *,
    original_blueprint:dict[str,Any],
    revised_blueprint:dict[str,Any],
    contracts:list[dict[str,Any]],
    production_verification:dict[str,Any],
    evidence_bindings:list[dict[str,Any]],
    specialist_pack_id:str|None=None,
)->dict[str,Any]:
    if production_verification.get("status")!="verified_in_production":
        raise RepairClosureError("production verification is not verified_in_production")
    if production_verification.get("all_tests_passed") is not True:
        raise RepairClosureError("production verification did not pass all tests")
    if not contracts:
        raise RepairClosureError("at least one accepted issue contract is required")

    tests=production_verification.get("tests")
    if not isinstance(tests,list):
        raise RepairClosureError("production verification tests are missing")
    tests_by_id={
        str(item.get("test_id")):item
        for item in tests
        if isinstance(item,dict) and item.get("test_id")
    }
    binding_map=_binding_map(evidence_bindings)

    revised_findings=audit_make.scan_blueprint(revised_blueprint)
    comparison=compare_rescan.compare(original_blueprint,revised_blueprint)

    evaluated=[]
    for contract in contracts:
        rule=str(contract.get("rule") or "")
        module_id=contract.get("module_id")
        still_present=_finding_present(revised_findings,rule,module_id)

        test_id=binding_map.get((rule,"" if module_id is None else str(module_id)))
        evidence=tests_by_id.get(test_id) if test_id else None

        evaluated.append(
            resolution_contract.evaluate_resolution_contract(
                contract,
                still_present_after=still_present,
                evidence=evidence,
                trusted_connected_evidence=True,
            )
        )

    issue_contracts_closed=resolution_contract.all_closed_verified(evaluated)
    introduced_findings=comparison["new"]
    no_new_findings=len(introduced_findings)==0

    pack_result=None
    pack_verified=True
    if specialist_pack_id:
        pack_result=pack_acceptance_verification.verify_pack_acceptance(
            specialist_pack_id,
            tests,
            trusted_connected_evidence=True,
        )
        pack_verified=pack_result["all_tests_independently_verified"] is True

    customer_complete=issue_contracts_closed and no_new_findings and pack_verified

    return {
        "case_status":"closed_verified" if customer_complete else "open",
        "customer_complete":customer_complete,
        "issue_contracts_closed":issue_contracts_closed,
        "no_new_static_findings":no_new_findings,
        "introduced_findings":introduced_findings,
        "specialist_pack":pack_result,
        "contracts":evaluated,
        "production_verification_status":production_verification["status"],
        "customer_language":(
            "Every accepted issue definition of done passed, no new static reliability finding was introduced, and all required specialist acceptance tests passed in connected production-safe verification."
            if customer_complete else
            "The repair is not complete. At least one required proof gate remains open; PCFlows must not tell the customer the accepted repair is fixed yet."
        ),
    }
