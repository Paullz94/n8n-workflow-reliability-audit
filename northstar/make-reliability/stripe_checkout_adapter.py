#!/usr/bin/env python3
"""Normalize authenticated Stripe Checkout data into the PCFlows order contract."""
from __future__ import annotations

from typing import Any

import order_contract


class CheckoutAdapterError(ValueError):
    pass


def _truthy(value: Any) -> bool:
    if value is True or value == 1:
        return True
    return isinstance(value,str) and value.strip().lower() in {"1","true","yes","test","owner"}


def _metadata(obj: Any) -> dict[str,Any]:
    if isinstance(obj,dict) and isinstance(obj.get("metadata"),dict):
        return obj["metadata"]
    return {}


def _package_from(
    session:dict[str,Any],
    payment_intent:dict[str,Any]|None,
    line_items:list[dict[str,Any]]|None,
)->str|None:
    candidates=[]

    for source in (_metadata(session),_metadata(payment_intent or {})):
        value=source.get("pcflows_package")
        if value:
            candidates.append(str(value))

    for item in line_items or []:
        if not isinstance(item,dict):
            continue
        price=item.get("price")
        if isinstance(price,dict):
            value=_metadata(price).get("pcflows_package")
            if value:
                candidates.append(str(value))
            product=price.get("product")
            if isinstance(product,dict):
                value=_metadata(product).get("pcflows_package")
                if value:
                    candidates.append(str(value))

    unique={x.strip() for x in candidates if x and x.strip()}
    if len(unique)>1:
        raise CheckoutAdapterError(f"conflicting pcflows_package metadata: {sorted(unique)}")
    return next(iter(unique)) if unique else None


def normalize_checkout_session(
    session:dict[str,Any],
    *,
    payment_intent:dict[str,Any]|None=None,
    line_items:list[dict[str,Any]]|None=None,
    provider_verified:bool,
)->dict[str,Any]:
    if not isinstance(session,dict):
        raise CheckoutAdapterError("session must be an object")
    if provider_verified is not True:
        raise CheckoutAdapterError("provider_verified must be true only for authenticated Stripe data")

    package_id=_package_from(session,payment_intent,line_items)
    if not package_id:
        raise CheckoutAdapterError("pcflows_package metadata not found in trusted Stripe objects")

    session_metadata=_metadata(session)
    pi_metadata=_metadata(payment_intent or {})
    owner_or_test=any(_truthy(source.get(key)) for source in (session_metadata,pi_metadata) for key in ("owner_or_test","test_payment","owner_payment"))

    snapshot={
        "provider_verified":True,
        "livemode":session.get("livemode") is True,
        "session_id":session.get("id"),
        "payment_status":session.get("payment_status"),
        "currency":session.get("currency"),
        "amount_total":session.get("amount_total"),
        "metadata":{"pcflows_package":package_id},
        "owner_or_test":owner_or_test,
    }

    try:
        return order_contract.validate_paid_order(snapshot)
    except order_contract.OrderContractError as exc:
        raise CheckoutAdapterError(str(exc)) from exc
