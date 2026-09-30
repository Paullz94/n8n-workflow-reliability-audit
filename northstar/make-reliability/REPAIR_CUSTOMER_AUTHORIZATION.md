# Verified Repair Customer Authorization Contract — Internal

Updated: 2026-09-25
Public status: disabled until Verified Repair launches.

A production write must never happen solely because an AI decided it would help.

## Required authorization record

Before any production blueprint update, PCFlows needs a case-bound authorization record containing:

- `repair_case_id`;
- `customer_authorization_id`;
- customer/account identity linked to the paid order;
- Make organization/team identifier;
- exact production scenario ID;
- exact accepted issue description;
- authorization timestamp;
- authorization scope: backup, update target scenario, execute production-safe synthetic acceptance tests, rollback if verification fails;
- expiry/revocation rule.

## What authorization does NOT include

It does not authorize:
- unrelated scenarios;
- new paid third-party services;
- customer financial transactions;
- unrestricted production-data browsing;
- exporting credentials;
- changing billing/account/security settings;
- expanding the repair into unrelated development.

## Runtime enforcement

`make_runtime_client.py` additionally requires environment-backed values:
- `PCFLOWS_MAKE_PRODUCTION_WRITE_ENABLED=true`;
- target in `PCFLOWS_MAKE_PRODUCTION_SCENARIO_IDS`;
- `PCFLOWS_REPAIR_CASE_ID`;
- `PCFLOWS_CUSTOMER_AUTHORIZATION_ID`.

`production_deploy_runner.py` requires the exact sandbox-certified revised-blueprint hash before deployment.

## Customer-facing authorization concept

When Verified Repair launches, the customer should explicitly approve wording equivalent to:

> I authorize PCFlows to modify the specified Make.com scenario only for the accepted repair scope, to run the documented production-safe synthetic verification checks, and to automatically restore the previous blueprint if verification fails.

Do not use vague "access to my account" consent.

## Revocation

If authorization is revoked before deployment:
- production write gate closes;
- case becomes blocked, not complete.

If revocation happens after a production update but before verification:
- safest feasible state must be determined from already authorized rollback scope;
- do not perform unrelated work.

## Audit trail

Authorization IDs and technical hashes belong in the private order/case record, not the public GitHub repository.
