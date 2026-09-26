# PCFlows Pricing Architecture

Research date: 2026-09-25

## Decision

PCFlows will use a small fixed package ladder rather than one price or open-ended custom consulting.

### EUR 0 — Reliability Preflight
Self-serve local static scan.

### EUR 79 — Focused Risk Check
For one clearly defined reliability concern in one sanitized scenario.

Examples:
- "Can this create duplicate invoices?"
- "Can leads be sent twice?"
- "What happens if this API write fails?"
- "Can this AI step pass malformed data into CRM?"

No included re-scan.

### EUR 149 — Data Integrity Audit
The core product.

One scenario, broad reliability/data-integrity review, business-context prioritization, remediation/verification plan, one re-scan.

Lead Flow / Invoice & Payment Sync / AI Workflow Guardrails are specialist modes of this same product rather than separate surcharge products.

### EUR 399 — Portfolio / Release QA
Up to three related scenarios, aimed at agencies/freelancers/teams before client handoff or release.

Per-scenario findings + combined release/handover summary + one combined re-scan round.

## Why this ladder

Current visible Upwork service pricing in September 2026 spans:
- quick workflow fixes around USD 39–75;
- common Make.com starter work around USD 100–150;
- mid-tier automation/reliability work around USD 250–349;
- larger tiers around USD 600–699 and above;
- one audit/repair offer lists USD 149 / 900 / 2,500 tiers.

Sources:
- https://www.upwork.com/services/product/development-it-a-fix-for-your-broken-n8n-make-com-or-zapier-workflow-2066514457477908399
- https://www.upwork.com/services/product/development-it-i-will-fix-your-broken-make-com-or-zapier-automation-2099125554841972408
- https://www.upwork.com/services/product/development-it-make-com-automation-expert-scenarios-apis-business-workflows-2039800046419665967
- https://www.upwork.com/services/product/development-it-your-broken-make-com-n8n-or-zapier-automation-diagnosed-and-fixed-2083886588020708136
- https://www.upwork.com/services/product/development-it-an-audit-and-repair-of-your-broken-make-n8n-or-zapier-workflows-2061305568623649179

The PCFlows prices remain hypotheses until real customers buy.

## Guardrails

- Do not create fake crossed-out "was" prices.
- Do not discount before evidence says price is the blocker.
- Do not upsell a Data Integrity Audit when the free scan or EUR79 focused check is sufficient.
- Do not sell Portfolio / Release QA until its automated multi-scenario pipeline passes tests.
- Checkout stays disabled until Belgian registration/VAT launch gate is complete.
- All prices are fixed-scope; no hidden open-ended implementation promise.
