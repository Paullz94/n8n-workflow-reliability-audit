# Zero-Capital Willingness-to-Pay Pilot

Updated: 2026-09-25

This pilot exists only to validate willingness to pay and product scope. It is **not** the desired permanent operating model.

## Offer ladder

### EUR 49 — Reliability Preflight+
- 1 sanitized Make blueprint;
- automated static reliability scan;
- prioritized findings;
- downloadable report;
- no production credentials;
- asynchronous delivery.

Target state: fully automated.

### EUR 149 — Data Integrity Audit — primary pilot
- 1 sanitized Make blueprint;
- automated scan plus bounded interpretation of the highest-risk findings;
- focus on duplicate writes, retry/idempotency, concurrency, silent skips and recovery;
- up to 2 redacted or synthetic input examples;
- one asynchronous re-scan after remediation;
- no live production access.

Manual component during pilot: review of the top findings and remediation ordering only. Codex/software should do the repeatable analysis.

### EUR 299 — Small Portfolio Audit
- up to 3 related sanitized blueprints;
- cross-scenario write/retry/recovery review;
- prioritized portfolio report;
- one asynchronous re-scan per blueprint.

Do not offer this tier until the EUR 149 pilot is operationally bounded.

## Revenue math

The EUR 1,000 verified-gross target can be crossed by, for example:
- 7 × EUR 149 = EUR 1,043;
- 4 × EUR 299 = EUR 1,196;
- mixed tiers are permitted.

These are scenarios, not forecasts or booked revenue.

## Pilot capacity and human pace

To avoid turning Northstar into a hidden consulting job:
- accept at most a small number of active pilot audits at once;
- do not promise instant turnaround merely because automation is available;
- keep delivery windows realistic for a solo operator;
- do not manufacture urgency, fake scarcity or fake customer counts;
- pause acquisition if support/review load would exceed the bounded pilot design.

## Qualification

A pilot customer is qualified only if:
- they control or are authorized to share the blueprint;
- the blueprint is sanitized;
- the scenario performs meaningful business work;
- the stated problem involves reliability, recovery, duplicate writes, silent skips, ordering, or data integrity;
- they accept the static-analysis limitations.

Reject or redirect:
- requests requiring production credentials;
- requests to bypass platform security or access controls;
- open-ended implementation retainers;
- projects that require Paul to become the daily operator.

## Success gate

The pilot is successful when genuine external customers pay through an approved payment provider and the majority of delivery can be reduced to a deterministic self-service workflow.

Do not count invoices, promises, test purchases, owner purchases, pending payments or refunded transactions as verified gross revenue.
