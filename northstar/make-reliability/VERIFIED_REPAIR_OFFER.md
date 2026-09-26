# Verified Repair Offer — Internal Plan

Research date: 2026-09-25
Public status: **DISABLED**

## Goal

PCFlows should eventually be able to sell a repair outcome, not only an audit.

Paul's requirement:
> Do not close a customer issue until the accepted issue is actually verified against its definition of done.

This does not mean claiming that every possible future defect in a customer's automation is impossible. It means every issue PCFlows accepts into the repair scope remains open until **100% of its agreed acceptance criteria pass**.

## Market evidence

Current public Make.com repair services commonly sell:
- quick fixes around USD 39–150;
- one-scenario repair tiers around USD 129–349;
- more complete one-scenario repair/hardening around USD 300–600;
- audit/repair engagements can rise to USD 900+.

Observed examples:
- https://www.upwork.com/services/product/development-it-fix-your-make-com-scenario-and-automation-errors-2098810513774900173
- https://www.upwork.com/services/product/development-it-i-will-fix-your-broken-make-com-or-zapier-automation-2099125554841972408
- https://www.upwork.com/services/product/development-it-your-broken-make-com-n8n-or-zapier-automation-diagnosed-and-fixed-2083886588020708136
- https://www.upwork.com/services/product/development-it-an-audit-and-repair-of-your-broken-make-n8n-or-zapier-workflows-2061305568623649179

## Planned package

### PCFlows Verified Repair — price hypothesis EUR299

Strict scope:
- 1 Make.com scenario;
- 1 accepted root-cause issue;
- issue must pass `fix_eligibility.py`;
- explicit resolution contract created before changes;
- safe backup/rollback path available;
- repair applied through an authorized connected environment;
- all rule-specific acceptance criteria executed;
- remediation proof report delivered;
- issue is not complete until `closed_verified`.

Not included:
- unlimited bug fixing;
- feature development;
- multiple unrelated root causes;
- production incident response;
- unverifiable third-party behavior;
- changes requiring credentials sent over email.

## Failure policy hypothesis

If the issue was accepted as eligible for Verified Repair but PCFlows cannot make all agreed acceptance criteria pass within the bounded repair scope:
- do not call the job complete;
- do not issue a “verified fixed” result;
- follow the documented repair-failure/refund policy.

This policy must be finalized before the offer becomes public.

## Why EUR299

It is deliberately above the EUR149 audit:
- implementation/change risk is higher;
- connected runtime testing is required;
- rollback/backup obligations are higher;
- customer expectation is an outcome, not just diagnosis.

It remains within the visible current market band for one-scenario repair/hardening.

## Activation gates

Verified Repair stays disabled until all are true:
- [x] rule-specific proof registry exists;
- [x] resolution contract exists;
- [x] fix eligibility gate exists;
- [x] Make API run/replay client exists;
- [x] unsupported fix-claim guard exists;
- [ ] secure Make connector/runtime authorization exists;
- [ ] scenario backup retrieval is verified;
- [ ] safe scenario update/deployment path is verified;
- [ ] rollback after failed verification is tested;
- [ ] at least one end-to-end synthetic repair case passes in a real Make sandbox;
- [ ] refund/failure policy finalized;
- [ ] Stripe product/price created only after all technical gates pass.

## No premature launch

Do not add Verified Repair to the public pricing page while any activation gate is unchecked.
