# Final Repair Closure Gate

Updated: 2026-09-25

The future PCFlows Verified Repair case can only close when **all** of these are true:

1. production deployment already reached `verified_in_production`;
2. every accepted issue has a resolution contract;
3. each runtime-dependent contract is bound to actual connected Make execution evidence;
4. every accepted issue contract becomes `closed_verified`;
5. the repair introduced **zero new static PCFlows findings**;
6. if the case uses a specialist mode, every specialist business acceptance test is independently verified.

If any gate fails:
- `case_status = open`;
- `customer_complete = false`;
- PCFlows must continue repair/testing or follow the repair outcome/refund policy;
- it must not send a “fixed” completion message.

## Why block on new findings

A repair that solves one issue but introduces a new reliability warning is not considered complete.

This avoids cases such as:
- stopping retries but accidentally removing recovery;
- serializing execution but enabling data-loss behavior;
- changing an error handler in a way that creates silent success elsewhere.

## Evidence binding

Each accepted runtime issue explicitly maps to a connected acceptance test ID.

A generic green Make run is not sufficient.

## Customer meaning

A closed Verified Repair case means:

**Every accepted issue's definition of done passed, no new static reliability signal was introduced by the repair, and all applicable specialist acceptance tests passed through independently observed connected execution evidence.**
