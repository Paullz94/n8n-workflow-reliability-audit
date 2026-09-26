#!/usr/bin/env python3
"""Validate that PCFlows package catalog and paid order contract stay aligned."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import order_contract


class PackageConsistencyError(ValueError):
    pass


def validate_catalog(catalog:dict[str,Any])->dict[str,Any]:
    packages=catalog.get("packages")
    if not isinstance(packages,list):
        raise PackageConsistencyError("package catalog needs a packages array")

    by_id={}
    for item in packages:
        if not isinstance(item,dict) or not item.get("id"):
            raise PackageConsistencyError("every package needs an id")
        if item["id"] in by_id:
            raise PackageConsistencyError(f"duplicate package id: {item['id']}")
        by_id[item["id"]]=item

    expected_paid=set(order_contract.PACKAGE_AMOUNTS_CENTS)
    catalog_paid={pid for pid,item in by_id.items() if int(item.get("price_eur",0))>0}
    if catalog_paid != expected_paid:
        raise PackageConsistencyError(
            f"paid package mismatch: catalog={sorted(catalog_paid)} contract={sorted(expected_paid)}"
        )

    for pid,cents in order_contract.PACKAGE_AMOUNTS_CENTS.items():
        euros=by_id[pid].get("price_eur")
        if euros is None or int(euros)*100 != cents:
            raise PackageConsistencyError(
                f"price mismatch for {pid}: catalog={euros} EUR contract={cents} cents"
            )

    if "preflight_free" not in by_id or int(by_id["preflight_free"].get("price_eur",-1))!=0:
        raise PackageConsistencyError("preflight_free must exist at EUR0")

    return {
        "package_count":len(packages),
        "paid_package_ids":sorted(expected_paid),
        "prices_eur":{pid:order_contract.PACKAGE_AMOUNTS_CENTS[pid]//100 for pid in sorted(expected_paid)},
        "free_package_id":"preflight_free",
    }


def main()->int:
    path=Path(__file__).with_name("package_catalog.json")
    try:
        catalog=json.loads(path.read_text(encoding="utf-8"))
        result=validate_catalog(catalog)
    except (OSError,json.JSONDecodeError,PackageConsistencyError) as exc:
        print(json.dumps({"error":str(exc)}))
        return 2
    print(json.dumps(result,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
