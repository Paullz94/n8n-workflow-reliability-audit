# Workflow Reliability Audit — Hardened Order Intake Demo

- Active: True
- Nodes: 5
- Input SHA-256: `354f058fe967ba3e9259b4d30720d592f4e9cd46340ac4a359614ef2bded6564`
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
