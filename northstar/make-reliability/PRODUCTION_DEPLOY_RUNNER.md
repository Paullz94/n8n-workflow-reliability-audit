# Production Deploy Runner

Updated: 2026-09-25

This is future Verified Repair infrastructure and is **not active today**.

`production_deploy_runner.py` applies a repair to an authorized production scenario only after the exact same revised blueprint was verified in an allowlisted Make sandbox.

## Gates

Before production update:
- exact revised-blueprint SHA must match the sandbox certificate;
- sandbox status must be `verified_in_sandbox`;
- all sandbox tests must have passed;
- production test plan must exist;
- every production test must be explicitly marked `production_safe`;
- MakeRuntimeClient independently requires:
  - production writes enabled;
  - production scenario allowlisted;
  - repair case ID;
  - customer authorization ID.

## Deployment sequence

1. Fetch and preserve original production blueprint.
2. PATCH the exact sandbox-verified revision.
3. Re-read deployed blueprint.
4. Run production-safe synthetic acceptance tests.
5. If every test passes: return `verified_in_production`.
6. If any test/error occurs: automatically restore the original production blueprint.
7. If rollback itself fails: surface the rollback failure as a critical error.

## Closure

`verified_in_production` does not automatically close unrelated findings.

Only issue contracts whose required assertions are satisfied by the resulting connected evidence can move to `closed_verified`.

The customer case closes only when every accepted issue contract is closed_verified.

## Current status

Prepared and mock-tested in source, but cannot be exercised against real Make until:
- dedicated PCFlows Make service identity;
- secure API authorization;
- real sandbox scenario;
- explicitly authorized production test case.

Therefore the public audit packages remain unchanged and Verified Repair remains disabled.
