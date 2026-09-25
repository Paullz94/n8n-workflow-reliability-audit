#!/usr/bin/env python3
"""Minimal Make API runtime client for future PCFlows connected verification.

Security model:
- token is read only from an environment variable;
- token is never accepted via CLI, JSON, email or report input;
- responses are returned to the caller but the token is never logged;
- intended for a dedicated sandbox/test organization or explicitly authorized
  connected environment, not blind production mutation.
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


ZONE_RE=re.compile(r"^https://(?:eu|us)\d+\.make(?:\.celonis)?\.com$",re.I)


class MakeRuntimeError(RuntimeError):
    pass


@dataclass(frozen=True)
class MakeRuntimeConfig:
    zone_url:str
    token_env:str="PCFLOWS_MAKE_API_TOKEN"
    timeout_seconds:int=45

    def base_url(self)->str:
        value=self.zone_url.rstrip("/")
        if not ZONE_RE.fullmatch(value):
            raise MakeRuntimeError("unsupported Make zone URL")
        return value + "/api/v2"

    def token(self)->str:
        value=os.environ.get(self.token_env,"").strip()
        if not value:
            raise MakeRuntimeError(
                f"missing Make API token in environment variable {self.token_env}"
            )
        return value


class MakeRuntimeClient:
    def __init__(self, config:MakeRuntimeConfig):
        self.config=config

    def _request(self, method:str, path:str, body:dict[str,Any]|None=None)->Any:
        url=self.config.base_url()+path
        data=None
        headers={
            "Authorization":"Token "+self.config.token(),
            "Accept":"application/json",
        }
        if body is not None:
            data=json.dumps(body).encode("utf-8")
            headers["Content-Type"]="application/json"
        req=urllib.request.Request(url,data=data,headers=headers,method=method)
        try:
            with urllib.request.urlopen(req,timeout=self.config.timeout_seconds) as resp:
                raw=resp.read()
        except urllib.error.HTTPError as exc:
            detail=exc.read().decode("utf-8","replace")
            raise MakeRuntimeError(
                f"Make API HTTP {exc.code} for {method} {path}: {detail[:500]}"
            ) from exc
        except urllib.error.URLError as exc:
            raise MakeRuntimeError(f"Make API request failed for {method} {path}: {exc.reason}") from exc

        if not raw:
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return raw.decode("utf-8","replace")

    def get_scenario(self, scenario_id:int)->dict[str,Any]:
        result=self._request("GET",f"/scenarios/{int(scenario_id)}")
        if not isinstance(result,dict):
            raise MakeRuntimeError("unexpected scenario response")
        return result

    def run_scenario(
        self,
        scenario_id:int,
        *,
        data:dict[str,Any]|None=None,
        responsive:bool=True,
    )->dict[str,Any]:
        payload={"responsive":bool(responsive)}
        if data is not None:
            payload["data"]=data
        result=self._request("POST",f"/scenarios/{int(scenario_id)}/run",payload)
        if not isinstance(result,dict):
            raise MakeRuntimeError("unexpected run response")
        execution_id=result.get("executionId")
        if not execution_id:
            raise MakeRuntimeError("Make run response did not include executionId")
        return result

    def replay_execution(self, scenario_id:int, execution_id:str)->None:
        value=str(execution_id).strip()
        if not value:
            raise MakeRuntimeError("execution_id is required")
        self._request(
            "POST",
            f"/scenarios/{int(scenario_id)}/replay",
            {"executionIds":[value]},
        )
