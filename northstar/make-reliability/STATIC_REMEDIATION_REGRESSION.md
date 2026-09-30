# Static Remediation Regression Matrix

Updated: 2026-09-25

PCFlows now carries a synthetic before/after regression test for every current deterministic rule.

The matrix proves two things about the **static engine**:
1. the known problematic blueprint condition is detected;
2. a blueprint where that structural condition is changed no longer triggers the same rule.

Covered:
- invalid/empty blueprint;
- missing error handler;
- retrying write;
- Ignore/Skip;
- Resume;
- Commit;
- mutating HTTP method;
- filtered write;
- designer warning/error;
- concurrent write scenario;
- auto-commit;
- rollback + auto-commit;
- incomplete executions disabled;
- data-loss setting;
- confidential-observability signal;
- secret-like literals.

## Important interpretation

This matrix is **not** runtime proof.

Example:
Changing an HTTP POST to GET clears the static mutating-HTTP rule, but that is not automatically the correct business remediation. A real solution must preserve intended business behavior and pass the rule-specific synthetic/runtime test.

The matrix exists to prevent scanner regressions and to prove that PCFlows can observe structural before/after changes consistently.
