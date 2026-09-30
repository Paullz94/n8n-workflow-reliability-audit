# Sandbox Repair Runner

Updated: 2026-09-25

`sandbox_repair_runner.py` is the future connected repair verification orchestrator.

## Safety sequence

1. Reject revised blueprints with secret-like literals.
2. Require at least one explicit acceptance test.
3. Update only an allowlisted scenario while Make write mode is explicitly `sandbox`.
4. Fetch/store the original blueprint before the PATCH.
5. Re-read the deployed sandbox blueprint.
6. Execute the synthetic acceptance plan.
7. Accept only a small structured proof object from the responsive run.
8. If **any** assertion fails or any runtime error occurs, restore the original sandbox blueprint automatically.
9. If rollback itself fails, surface that failure rather than hiding it.
10. Only when every supplied acceptance test passes return `verified_in_sandbox`.

## Important boundary

`verified_in_sandbox` is not the same as production deployment.

Production deployment remains a separate future gate:
- explicit validated source and target;
- backup;
- deployment;
- post-deploy smoke/acceptance checks;
- rollback if post-deploy verification fails.

## Test evaluators currently prepared

- duplicate replay;
- failure/recovery;
- human handoff;
- partial payment;
- invalid AI output;
- onboarding required resources.

The proof outputs are privacy-bounded through `runtime_test_contract.py`.

## Current blocker

The orchestrator can be tested with mocks and is coded against Make's official scenario run/update APIs, but it cannot be exercised end-to-end until a secure PCFlows Make service identity/API authorization and an allowlisted Make sandbox scenario exist.
