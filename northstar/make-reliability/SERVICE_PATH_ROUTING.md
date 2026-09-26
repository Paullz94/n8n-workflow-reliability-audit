# Service Path Routing — Help the Customer Without Over-Rejecting

Updated: 2026-09-25

## Core distinction

PCFlows has two different questions:

1. **Can PCFlows help this customer?**
2. **Can PCFlows promise an independently verified done-for-you repair?**

The second question is intentionally stricter.

Failing the Verified Repair gate must **not** automatically reject the customer.

## Default routing

### Root cause unclear
Route:
**Audit -> identify root cause -> re-qualify automatically**

Do not reject.

### Root cause known, but no safe connected runtime proof
Route:
**Guided remediation + verification plan**

PCFlows can still:
- explain the exact issue;
- identify the likely root cause;
- specify the change;
- provide a safe implementation/remediation plan;
- provide synthetic acceptance tests;
- re-scan the revised blueprint;
- evaluate customer-supplied sanitized evidence.

The only thing PCFlows withholds is the strongest claim:
**independently verified fixed**.

### Full proof prerequisites available
Route:
**Verified Repair candidate**

Only here does the no-close-until-100%-of-accepted-criteria-pass contract apply.

### Unsafe blueprint / secret-like input
Route:
**Re-sanitize and continue**

Do not reject the customer unless they refuse to provide a safe artifact/access path.

### Missing authorization
Route:
**Request authorization and continue**

Do not reject the customer.

## True decline cases should be rare

A real decline should be reserved for situations such as:
- customer is not authorized to have the workflow reviewed/changed;
- requested work is illegal or abusive;
- requested outcome is outside PCFlows's technical domain;
- customer refuses necessary sanitization/safety requirements;
- customer insists on a guarantee for something that cannot be meaningfully tested and refuses the audit/guided-remediation alternative.

## Commercial principle

Be strict about **claims**, not about **helpfulness**.

PCFlows should accept a broad range of Make.com reliability problems while being precise about whether the outcome is:
- diagnosis;
- remediation guidance;
- evidence-supported;
- independently verified repair.
