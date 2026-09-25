#!/usr/bin/env python3
"""Deploy only a sandbox-verified PCFlows repair revision to an authorized production scenario.

Production deployment is disabled by default at the MakeRuntimeClient layer.
This orchestrator additionally requires:
- exact revised-blueprint hash match with prior sandbox verification;
- all sandbox tests passed;
- explicit production-safe post-deploy test specifications;
- automatic rollback on any deployment/test failure.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

import audit_make
import make_runtime_client
import sandbox_repair_runner


class ProductionDeployError(RuntimeError):
    pass


def _sha(value:dict[str,Any])->str:
    raw=json.dumps(value,sort_keys=True,separators=(",",":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def validate_sandbox_certificate(
    revised_blueprint:dict[str,Any],
    sandbox_verification:dict[str,Any],
)->None:
    if not isinstance(sandbox_verification,dict):
        raise ProductionDeployError("sandbox verification certificate is required")
    if sandbox_verification.get("status")!="verified_in_sandbox":
        raise ProductionDeployError("sandbox repair is not verified_in_sandbox")
    if sandbox_verification.get("all_tests_passed") is not True:
        raise ProductionDeployError("sandbox verification did not pass all tests")
    expected=str(sandbox_verification.get("requested_revised_sha256") or "")
    actual=_sha(revised_blueprint)
    if not expected or expected!=actual:
        raise ProductionDeployError("production revision does not match the sandbox-verified revision")


def validate_production_test_plan(test_plan:list[dict[str,Any]])->None:
    if not test_plan:
        raise ProductionDeployError("at least one production-safe post-deploy test is required")
    for spec in test_plan:
        if not isinstance(spec,dict):
            raise ProductionDeployError("production test plan entries must be objects")
        if spec.get("production_safe") is not True:
            raise ProductionDeployError(
                f"test {spec.get('test_id')!r} is not explicitly marked production_safe"
            )


def deploy_verified_repair(
    *,
    client:make_runtime_client.MakeRuntimeClient,
    production_scenario_id:int,
    revised_blueprint:dict[str,Any],
    sandbox_verification:dict[str,Any],
    production_test_plan:list[dict[str,Any]],
)->dict[str,Any]:
    if not isinstance(revised_blueprint,dict):
        raise ProductionDeployError("revised_blueprint must be an object")
    if any(f.rule=="possible-secret-in-blueprint" for f in audit_make.scan_blueprint(revised_blueprint)):
        raise ProductionDeployError("revised blueprint contains possible secret-like input")

    validate_sandbox_certificate(revised_blueprint,sandbox_verification)
    validate_production_test_plan(production_test_plan)

    backup=None
    rollback_attempted=False
    try:
        backup=client.update_production_blueprint(production_scenario_id,revised_blueprint)
        original=backup.get("original_blueprint")
        if not isinstance(original,dict):
            raise ProductionDeployError("production update did not return original blueprint backup")

        deployed=client.get_blueprint(production_scenario_id)
        if any(f.rule=="possible-secret-in-blueprint" for f in audit_make.scan_blueprint(deployed)):
            raise ProductionDeployError("deployed production blueprint contains possible secret-like input")

        tests=[]
        for spec in production_test_plan:
            tests.append(
                sandbox_repair_runner._run_test(
                    client,
                    production_scenario_id,
                    spec,
                )
            )

        return {
            "production_scenario_id":int(production_scenario_id),
            "status":"verified_in_production",
            "all_tests_passed":True,
            "repair_case_id":backup.get("repair_case_id"),
            "customer_authorization_id":backup.get("customer_authorization_id"),
            "sandbox_revision_sha256":sandbox_verification.get("requested_revised_sha256"),
            "production_requested_revision_sha256":_sha(revised_blueprint),
            "production_deployed_sha256":_sha(deployed),
            "original_production_sha256":backup.get("original_sha256") or _sha(original),
            "tests":tests,
            "rollback_performed":False,
            "customer_claim":"The authorized production revision passed every supplied production-safe acceptance test. Close only the issue contracts whose required assertions are satisfied by this evidence.",
        }
    except Exception as exc:
        rollback_error=None
        if isinstance(backup,dict) and isinstance(backup.get("original_blueprint"),dict):
            rollback_attempted=True
            try:
                client.rollback_production_blueprint(
                    production_scenario_id,
                    backup["original_blueprint"],
                )
            except Exception as rollback_exc:
                rollback_error=str(rollback_exc)
        message=f"production repair deployment failed: {exc}"
        if rollback_error:
            message+=f"; automatic production rollback also failed: {rollback_error}"
        elif rollback_attempted:
            message+="; original production blueprint was restored"
        raise ProductionDeployError(message) from exc
