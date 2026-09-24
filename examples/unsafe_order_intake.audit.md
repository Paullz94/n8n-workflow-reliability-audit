# Workflow Reliability Audit — Unsafe Order Intake Demo

- Active: True
- Nodes: 4
- Input SHA-256: `9c5a9e2ac934dcb6c318ff7cd901135f5eb25fc806a75b1e23b4d27992c106d5`
- Scope: Static export review only; execution, credentials, instance configuration, and business correctness remain unverified.
- Secrets: values are never printed in this report

## Summary

| Critical | High | Medium | Low | Info |
|---:|---:|---:|---:|---:|
| 1 | 4 | 3 | 1 | 0 |

## Findings

### CRITICAL SEC-003: Possible hard-coded secret — `Create ERP Order`

Evidence: A credential-like value is present at `parameters.authorization` (value redacted).

Recommendation: Remove it from node parameters, rotate if real, and use n8n credentials or an external secret store.

### HIGH DATA-001: No visible duplicate-prevention step

Evidence: An active trigger reaches side-effect-capable nodes, but no node name/type signals deduplication or idempotency.

Recommendation: Define an idempotency key, persist processed-event state, and test repeated delivery. This heuristic requires human confirmation.

### HIGH GRAPH-001: Unreachable nodes

Evidence: Not reachable from a trigger/root: Old Debug Node.

Recommendation: Remove stale nodes or connect them deliberately, then exercise every branch.

### HIGH RECOVERY-001: No workflow-level error workflow

Evidence: The workflow is active but `settings.errorWorkflow` is not configured.

Recommendation: Attach an error workflow that records context and alerts an operator without exposing payload secrets.

### HIGH SEC-001: Unauthenticated webhook — `Order Webhook`

Evidence: Webhook authentication is absent or set to none.

Recommendation: Require an appropriate authentication/signature check, rate limit the endpoint, and reject replayed requests.

### MEDIUM RECOVERY-002: HTTP call has no node retry policy — `Create ERP Order`

Evidence: `retryOnFail` is not enabled.

Recommendation: Add bounded retries with backoff only for retry-safe failures; protect writes with idempotency.

### MEDIUM RECOVERY-003: HTTP call has no explicit timeout — `Create ERP Order`

Evidence: No `parameters.options.timeout` value is present.

Recommendation: Set a finite timeout and route exhausted failures to an observable recovery path.

### MEDIUM SEC-002: Powerful node requires manual review — `Normalize Order`

Evidence: Node type `n8n-nodes-base.code` can execute code, commands, SSH, or file operations.

Recommendation: Review inputs, escaping, permissions, network/file access, and secret exposure; sandbox where possible.

### LOW OPS-001: No exported version identifier

Evidence: The active workflow has no `versionId` in this export.

Recommendation: Record the exact source version and keep before/after exports for rollback.

## Required dynamic evidence before release

- Re-run defined synthetic happy-path, malformed-input, duplicate-delivery, timeout, rate-limit, and partial-failure cases.
- Independently verify outputs and side effects, not only successful execution status.
- Confirm credential scopes, webhook authentication, instance security audit, logging redaction, and rollback.
- Do not use production personal data or plaintext credentials in the review package.
