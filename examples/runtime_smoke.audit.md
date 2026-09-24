# Workflow Reliability Audit — Runtime Smoke Demo

- Active: False
- Nodes: 2
- Input SHA-256: `c0c3fc5d1e7e84e16f82861017f9432094714515c2a78ca3cd4079f45d2101b5`
- Scope: Static export review only; execution, credentials, instance configuration, and business correctness remain unverified.
- Secrets: values are never printed in this report

## Summary

| Critical | High | Medium | Low | Info |
|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | 0 |

## Findings

No static findings. This does not prove production readiness.

## Required dynamic evidence before release

- Re-run defined synthetic happy-path, malformed-input, duplicate-delivery, timeout, rate-limit, and partial-failure cases.
- Independently verify outputs and side effects, not only successful execution status.
- Confirm credential scopes, webhook authentication, instance security audit, logging redaction, and rollback.
- Do not use production personal data or plaintext credentials in the review package.
