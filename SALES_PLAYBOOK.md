# PCFlows Sales Playbook

Target: EUR 5,000 in settled external-customer revenue.

## Launch state

Pre-launch. Do not activate paid checkout or start outbound selling until the Belgian seller-registration/tax gate documented in BUSINESS_ENGINE.md is cleared.

The owner-capital budget remains EUR 0 for optional tools. Only already-settled PCFlows revenue may be reinvested.

## Ideal customer profile

Prioritize organizations that:
- already use n8n;
- have roughly 10-200 staff;
- run workflows with irreversible or externally visible side effects;
- depend on APIs, webhooks, CRM, billing, email, databases, support systems, or scheduled syncs;
- have a clear operational owner and a measurable acceptance condition.

Strong signals:
- duplicate records, duplicate messages, duplicate charges, or double-processing;
- unreliable webhook handling;
- manual replay after partial failure;
- unclear retry behavior;
- missing error workflow or recovery path;
- production automation with little test evidence or handoff documentation.

Deprioritize:
- hobby workflows;
- pure prototyping;
- buyers asking for unlimited production support inside the fixed-scope price;
- requests requiring unrestricted production credentials;
- regulated or safety-critical work that cannot be safely bounded.

## Offer ladder

### Free local quick scan

Purpose: reduce friction and prove useful capability before asking for a sale.

CTA:
- run the scanner locally;
- review obvious reliability flags;
- request a fit check if the workflow is business-critical.

### n8n Reliability Audit — EUR 249

For one sanitized workflow export, up to 30 nodes.

The deliverable should contain:
- prioritized findings;
- evidence vs hypothesis clearly separated;
- remediation guidance;
- synthetic verification plan;
- one re-scan after remediation.

### n8n Reliability Retrofit — EUR 890

For one accepted failure/risk and bounded remediation.

The deliverable should contain:
- reproduced or clearly documented before-state;
- bounded changes;
- synthetic before/after evidence;
- rollback notes;
- handoff;
- one revision against written acceptance criteria.

## Qualification

Accept only when all are clear:
1. business outcome;
2. connected systems by name;
3. current symptom/risk;
4. n8n version and hosting type;
5. approximate node count;
6. acceptance condition;
7. confirmation that supplied material can be sanitized.

Reject or rescope if the buyer expects:
- credentials in public channels;
- customer/personal data unnecessarily;
- a guarantee of uninterrupted operation;
- certification or regulatory sign-off;
- unlimited revisions;
- broad production access without a separate agreement.

## Outreach rules

Inbound is preferred.

After the launch gate is cleared, outbound may target relevant legal-entity addresses such as info@, contact@, sales@, or similar generic company addresses where allowed. Do not treat firstname.lastname@company addresses as generic company addresses.

For Belgian electronic advertising:
- identify the sender clearly;
- make the commercial nature clear;
- include a simple opt-out route;
- do not continue after an opt-out;
- keep evidence supporting why the address is a legal-entity address.

Default cadence:
- one relevant initial message;
- at most one follow-up after 5-7 business days;
- stop after no response.

Never use bulk scraped personal addresses, fake personalization, fake case studies, fabricated urgency, or misleading claims.

## Outbound message framework

Subject: Advertising — n8n reliability fit check

Body structure:
1. one sentence showing why the company is relevant;
2. one concrete failure mode PCFlows checks;
3. one proof link to the public analyzer / free local scanner;
4. one low-friction question: whether a fixed-scope review is relevant;
5. sender identity and opt-out line.

Keep the first message under 120 words.

## Revenue tracking

Count only settled Stripe payments from unrelated external customers toward the EUR 5,000 target.

Do not count:
- test payments;
- owner-funded payments;
- refunds;
- unpaid requests;
- GitHub stars;
- repository traffic;
- compliments;
- leads without payment.

## Reinvestment

After settled revenue exists:
1. reserve required tax/compliance money;
2. preserve a cash buffer;
3. spend only on a measured bottleneck;
4. prefer one-off/reversible spend before recurring subscriptions.

Examples of acceptable later spend:
- a domain if it materially improves trust/conversion;
- email infrastructure if free delivery becomes a bottleneck;
- a paid data source only after free prospecting is exhausted and conversion evidence exists;
- monitoring/hosting only when the zero-cost stack becomes the bottleneck.

## Operator behavior

The autonomous operator should:
- monitor PCFlows inbox, GitHub audit requests, and Stripe;
- qualify inbound leads;
- prepare scoped replies;
- keep secrets and customer data out of public GitHub;
- escalate only legal identity, registration, KYC, credential entry, irreversible spend, or other owner-only actions;
- remain silent when nothing material changed.
