# Workflow Reliability Audit — Unsafe Scheduled CRM Sync

- Active: True
- Nodes: 3
- Input SHA-256: `70c8746c487454b1905b28d55a7b045a4b4a106b6fe636f5d3f8548e0333d731`
- Scope: Static export review only; execution, credentials, instance configuration, and business correctness remain unverified.
- Secrets: values are never printed in this report

## Summary

| Critical | High | Medium | Low | Info |
|---:|---:|---:|---:|---:|
| 0 | 2 | 3 | 1 | 0 |

## Findings

### HIGH DATA-001: No visible duplicate-prevention step

Evidence: An active trigger reaches side-effect-capable nodes, but no node name/type signals deduplication or idempotency.

Recommendation: Define an idempotency key, persist processed-event state, and test repeated delivery. This heuristic requires human confirmation.

### HIGH RECOVERY-001: No workflow-level error workflow

Evidence: The workflow is active but `settings.errorWorkflow` is not configured.

Recommendation: Attach an error workflow that records context and alerts an operator without exposing payload secrets.

### MEDIUM RECOVERY-002: HTTP call has no node retry policy — `Fetch Records`

Evidence: `retryOnFail` is not enabled.

Recommendation: Add bounded retries with backoff only for retry-safe failures; protect writes with idempotency.

### MEDIUM RECOVERY-003: HTTP call has no explicit timeout — `Fetch Records`

Evidence: No `parameters.options.timeout` value is present.

Recommendation: Set a finite timeout and route exhausted failures to an observable recovery path.

### MEDIUM RECOVERY-004: Node may convert a failure into a successful execution — `Fetch Records`

Evidence: The node uses `onError=continueRegularOutput`.

Recommendation: Confirm the continuation branch handles and surfaces the failure. A workflow-level Error Trigger runs only when the execution actually ends in error.

### LOW OPS-001: No exported version identifier

Evidence: The active workflow has no `versionId` in this export.

Recommendation: Record the exact source version and keep before/after exports for rollback.

## Required dynamic evidence before release

- Re-run defined synthetic happy-path, malformed-input, duplicate-delivery, timeout, rate-limit, and partial-failure cases.
- Independently verify outputs and side effects, not only successful execution status.
- Confirm credential scopes, webhook authentication, instance security audit, logging redaction, and rollback.
- Do not use production personal data or plaintext credentials in the review package.
