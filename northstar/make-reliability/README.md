# Project Northstar Ledger — Make.com Reliability Wedge

Date: 2026-09-25
Status: validation / zero-owner-capital
Isolation: this directory is intentionally separate from the existing n8n product files.

## Why this wedge

The retained n8n buyer research remains valid research, but Northstar needs a second market that does not depend on n8n Community participation.

Make.com is a credible adjacent wedge:
- Make documents first-class error handling, retries, incomplete executions, and recurring manual recovery.
- Its public community has a dedicated Hire Help category with recent requests for Make freelancers and automation specialists.
- The free plan is sufficient for product research/prototyping; no owner capital is required to validate demand.

Sources checked 2026-09-25:
- https://help.make.com/Overview-of-error-handling
- https://help.make.com/Introduction-to-errors-and-warnings
- https://community.make.com/
- https://www.make.com/en/pricing

## Proposed product

**Make Scenario Reliability Audit**

Input: a customer-exported Make scenario blueprint JSON (credentials/secrets must be removed).

Automated output:
1. machine-readable findings;
2. human-readable reliability report;
3. severity and evidence for each finding;
4. remediation checklist;
5. explicit limitations / no guarantee of runtime correctness.

Initial rules to validate:
- missing or weak error-handler coverage around failure-prone modules;
- unsafe retry patterns around write operations;
- duplicate-write / idempotency risks;
- dead or suspicious routes / filters;
- webhook and schedule reliability risks;
- manual-recovery hotspots;
- observability gaps.

## Commercial hypothesis

A narrow, fixed-scope audit is preferable to open-ended consulting because checkout, delivery, support and iteration can become self-service.

Validation ladder:
1. Free: collect public buyer signals and failure vocabulary.
2. Free: build offline blueprint analyzer + fixtures + deterministic tests.
3. Free: publish a sanitized sample report and landing copy.
4. External willingness-to-pay: accept only genuine external customer payment through an approved payment provider.
5. Automate intake -> scan -> report -> delivery before scaling.

No owner/test/pending/refunded/fictitious payment counts toward the EUR 1,000 target.

## Candidate pricing experiments

These are hypotheses, not booked revenue:
- Basic automated audit: EUR 29
- Audit + prioritized remediation report: EUR 59
- Deep audit with one asynchronous re-scan: EUR 99

Do not spend owner capital to test these prices.

## Acquisition constraints

Allowed:
- useful, non-spammy participation where platform rules permit;
- inbound from public repository/docs;
- marketplaces or directories that explicitly permit commercial offers;
- direct outreach only when relevant, individualized, and platform-compliant.

Not allowed:
- duplicate posts;
- second accounts;
- moderation bypass;
- unsolicited bulk outreach;
- pretending to be a customer;
- counting owner/test transactions.

## Autonomy scorecard

The end-state must support:
- acquisition: repeatable channels not requiring Paul daily;
- qualification: structured intake;
- pricing: fixed packages;
- checkout: self-service payment;
- delivery: automated report generation;
- support: bounded async support;
- measurement: provider-verified revenue ledger;
- iteration: rules driven by anonymized failure patterns.

Any model that requires Paul as daily operator fails the end-state gate.

## Ledger baseline

| Metric | EUR |
|---|---:|
| Owner reserve (uninjected) | 500.00 |
| Owner capital injected | 0.00 |
| Business-generated cash | 0.00 |
| Verified gross revenue | 0.00 |
| Revenue reinvested | 0.00 |
| Expenses | 0.00 |
| Refunds | 0.00 |
| Net revenue | 0.00 |
| Net operating result | 0.00 |

Revenue evidence must ultimately be reconciled against the payment provider, not GitHub claims or manually asserted sales.

## Pivot gate

Continue this wedge while at least one of these remains true:
- public buyer signals show paid demand for Make troubleshooting/reliability;
- the blueprint format permits useful static checks;
- a zero-cost acquisition route remains available;
- early external prospects show willingness to pay.

Pivot if the analyzer cannot produce actionable findings from sanitized blueprints, compliant acquisition cannot reach relevant buyers, or qualified prospects repeatedly reject paid fixed-scope audits.
