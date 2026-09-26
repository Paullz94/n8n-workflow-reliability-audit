# Verified Repair Gate

Updated: 2026-09-25

Paul's requirement is stricter than an ordinary audit product:

> If PCFlows ever claims an issue is fixed for a customer, that issue must actually pass the agreed proof criteria.

PCFlows therefore does **not** use an absolute marketing promise that every imaginable automation defect can be fixed.

Instead:
- an issue is accepted for a future **Verified Repair** only when it is independently testable;
- the issue remains open until every acceptance criterion passes;
- an untestable issue is not sold as a guaranteed repair.

## Runtime prerequisites

For a runtime-dependent issue, all must exist:
1. safe test/sandbox environment;
2. PCFlows can independently observe the execution;
3. the relevant external side effect can be observed/count-checked;
4. deterministic acceptance criteria are defined before repair.

If any is missing:
- audit/remediation guidance may still be delivered;
- Verified Repair must not be promised.

## Make API path

Make's official API supports:
- running an active scenario with `POST /scenarios/{scenarioId}/run`;
- responsive runs that return execution ID/status/output when available;
- replaying an execution with `POST /scenarios/{scenarioId}/replay`.

Official reference:
https://developers.make.com/api-documentation/api-reference/scenarios

`make_runtime_client.py` implements the minimal future client.

Security:
- API token comes only from a runtime environment secret;
- it is never accepted in customer email/intake/blueprint;
- use a dedicated sandbox/test authorization, not an emailed production token.

## Closing rule

A repair is not complete because:
- code changed;
- blueprint changed;
- a static warning disappeared;
- the scenario returned a generic success status.

It closes only when the agreed rule-specific acceptance criteria pass.

For example, an idempotency repair closes only after replaying the same synthetic event and observing exactly one intended external side effect.

## Current state

The Make API path is technically documented and a safe client abstraction exists, but no secure Make runtime connection is currently connected to PCFlows.

Therefore a public paid Verified Repair package remains **disabled**.

The audit products may launch first because they do not depend on this runtime connection.
