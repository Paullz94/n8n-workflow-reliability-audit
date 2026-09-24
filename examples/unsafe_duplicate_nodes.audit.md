# Workflow Reliability Audit — Ambiguous Notification Demo

- Active: False
- Nodes: 3
- Input SHA-256: `f64f30f5d8939828334b9e43fbcd8c706e589afdb55a01be7bcd47541ed844b6`
- Scope: Static export review only; execution, credentials, instance configuration, and business correctness remain unverified.
- Secrets: values are never printed in this report

## Summary

| Critical | High | Medium | Low | Info |
|---:|---:|---:|---:|---:|
| 0 | 1 | 1 | 0 | 0 |

## Findings

### HIGH STRUCT-002: Duplicate node names

Evidence: Duplicate names: Notify.

Recommendation: Use unique node names so expressions, connections, and incident reports are unambiguous.

### MEDIUM SEC-002: Powerful node requires manual review — `Notify`

Evidence: Node type `n8n-nodes-base.executeCommand` can execute code, commands, SSH, or file operations.

Recommendation: Review inputs, escaping, permissions, network/file access, and secret exposure; sandbox where possible.

## Required dynamic evidence before release

- Re-run defined synthetic happy-path, malformed-input, duplicate-delivery, timeout, rate-limit, and partial-failure cases.
- Independently verify outputs and side effects, not only successful execution status.
- Confirm credential scopes, webhook authentication, instance security audit, logging redaction, and rollback.
- Do not use production personal data or plaintext credentials in the review package.
