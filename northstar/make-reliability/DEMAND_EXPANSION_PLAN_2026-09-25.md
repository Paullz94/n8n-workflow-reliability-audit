# PCFlows Demand Expansion Plan

Research date: 2026-09-25
Status: pre-launch planning only; no new paid offer is public until the Belgian registration/VAT gate is complete.

## Strategy

Do not turn PCFlows into a generic "we automate anything" agency.

Keep one core competence:
**reliable business automation.**

Expand by wrapping the same reliability engine around common, expensive business problems that buyers already describe in plain language.

The recurring demand patterns found in current public jobs are:
1. lead capture / CRM / speed-to-lead;
2. client onboarding;
3. CRM <-> accounting / invoice / payment sync;
4. AI document extraction with human approval;
5. AI lead qualification / email/support automation with human handoff;
6. e-commerce order/inventory/backend sync;
7. pre-handoff QA for agencies/reusable automation templates.

---

## Priority 1 — Lead Flow Reliability

### Plain-English customer problem
"A lead filled in our form but nobody got notified."
"We have the same contact twice in HubSpot."
"The lead replied but the automation kept sending follow-ups."
"Facebook leads sometimes never arrive in the CRM."
"Two sales people get assigned the same lead."

### Typical flow
Facebook/website form -> Make -> CRM -> SMS/email -> sales notification -> appointment booking.

### Reliability risks PCFlows can inspect
- duplicate contact/deal creation;
- retry creating duplicate SMS/email;
- lead routing races;
- missing exit trigger after reply/booking;
- incorrect source/status field mapping;
- failed webhook with no recovery;
- slow/missing response notification;
- failure alert missing.

### Productized offer
**Lead Flow Reliability Audit**

Deliverable:
- current blueprint audit;
- duplicate/routing/follow-up risk map;
- exactly-once lead handling recommendations;
- synthetic acceptance tests;
- one remediation re-scan.

### Demand evidence
Current public Upwork jobs repeatedly request lead capture, duplicate prevention, CRM routing, instant response, follow-up, error handling and monitoring.

### Price hypothesis
Keep the current EUR 149 audit as the entry product.
Only add implementation pricing after real demand proves customers want PCFlows to perform the fixes.

---

## Priority 2 — Invoice & Payment Sync Reliability

### Plain-English customer problem
"A customer paid, but the CRM still says unpaid."
"The workflow created the invoice twice."
"The wrong QuickBooks customer was matched."
"A partial payment moved the deal to Paid too early."
"Stripe and QuickBooks disagree."
"Our team still copies invoice/payment data manually because the sync cannot be trusted."

### Typical flow
CRM/deal -> invoice -> QuickBooks/Xero -> Stripe/payment -> CRM status/project setup.

### Reliability risks PCFlows can inspect
- unstable customer matching keys;
- duplicate invoice creation;
- retry/idempotency;
- partial-payment handling;
- two-way sync loops;
- conflicting sources of truth;
- payment-status ordering;
- reconciliation gaps;
- auto-posting without human approval.

### Productized offer
**Invoice & Payment Sync Audit**

Deliverable:
- source-of-truth map;
- invoice/payment idempotency review;
- matching/conflict review;
- partial-payment test cases;
- recovery/reconciliation checklist;
- one re-scan.

### Demand evidence
Current public jobs include real-time CRM-accounting sync, QuickBooks invoice automation and an USD 1,800 Make.com invoice-to-QuickBooks AI agent.

### Important boundary
PCFlows should prefer draft/stage + human approval for high-impact accounting actions during the pilot rather than promising autonomous posting/payment.

---

## Priority 3 — AI Workflow Guardrails

### Plain-English customer problem
"AI sometimes returns text instead of the JSON the next step expects."
"The bot sends a confident answer even when it is wrong."
"One weird PDF breaks the whole scenario."
"The automation keeps messaging after a human took over."
"AI classifies a good lead as bad and nobody notices."

### Typical flow
Input -> LLM -> structured output -> CRM/document/accounting/customer message -> human handoff.

### Reliability risks PCFlows can inspect/verify
- no structured-output/schema enforcement;
- malformed/null fields reaching downstream writes;
- no validation before state-changing action;
- no human approval for high-impact writes;
- no confidence/exception path;
- retries causing duplicate external effects;
- no freeze/exit when a human takes ownership;
- LLM output treated as fact without deterministic checks.

### Productized offer
**AI Workflow Guardrails Audit**

Deliverable:
- AI-to-business-action boundary map;
- schema/validation checks;
- human-approval recommendations;
- failure/fallback path review;
- duplicate/retry review;
- synthetic malformed-output tests.

### Demand evidence
Current jobs request structured LLM outputs, human review, lead qualification, AI email drafting, AI agents, retries/validation/guardrails and production-grade logging.

### Future product
This is the best candidate for a later "runtime evidence" layer because AI failures often require comparing actual sanitized outputs, not only the blueprint.

---

## Priority 4 — Client Onboarding Reliability

### Plain-English customer problem
"The customer filled in the form but the project was never created."
"They got the welcome email twice."
"CRM says onboarding complete but the task list/folder is missing."
"One API failed halfway through and nobody knows what was already created."
"New customers are still manually copied between five tools."

### Typical flow
Intake form -> CRM -> project/task system -> folder/docs -> welcome email/SMS -> internal notification.

### Productized offer
**Client Onboarding Reliability Audit**

Checks:
- exactly-once client/project creation;
- required-step completeness;
- duplicate email/task/folder creation;
- failure visibility;
- partial-state recovery;
- handoff/ownership transitions;
- acceptance checklist.

### Demand evidence
Recent public jobs ask specifically for end-to-end onboarding automation and USD 600 standardized lead/onboarding builds with testing.

---

## Priority 5 — Agency Handover / Release QA

### Plain-English customer problem
"We paid someone to build this automation. How do we know it is safe to hand to the client?"
"We reuse this Make template for every customer; one bug could be copied 20 times."
"The scenario works in the demo, but nobody tested retries or failures."

### Buyer
- automation agencies;
- freelancers;
- consultants;
- internal automation teams.

### Productized offer
**Automation Release QA**

Deliverable:
- independent blueprint audit;
- synthetic failure/retry test plan;
- handover checklist;
- documentation gaps;
- before/after re-scan;
- optional client-facing report.

### Why strategically attractive
One agency can create repeat business without PCFlows needing thousands of end customers.

### Demand evidence
Current jobs include reusable automation templates, agency fulfillment partners and explicit requirements for testing, documentation, error handling and handover.

---

## Priority 6 — E-commerce Operations Integrity

### Plain-English customer problem
"Shopify says refunded but our CRM/accounting/inventory still says sold."
"We notified the warehouse twice."
"Inventory changes in one system but not the other."
"A cancelled order still triggered production."

### Typical flow
Shopify/order -> CRM -> inventory/supplier -> fulfillment -> email -> finance.

### Productized offer
**Order & Inventory Sync Audit**

Checks:
- order-id idempotency;
- refund/cancel ordering;
- fulfillment duplicate prevention;
- inventory race/conflict handling;
- source-of-truth rules;
- recovery and reconciliation.

### Demand evidence
Current e-commerce automation jobs ask for Shopify, CRM, order management, supplier/production tracking, inventory and finance to be connected via Make/n8n.

### Launch priority
Later than lead/accounting/AI guardrails because the current PCFlows rule set needs more vertical-specific fixtures before this should be marketed confidently.

---

## Product structure

Avoid seven unrelated products.

Public structure after validation:

### Core
**PCFlows Reliability Preflight — Free**

### Paid core
**PCFlows Data Integrity Audit — EUR 149**

### Problem-specific audit packs
- Lead Flow Reliability
- Invoice & Payment Sync
- AI Workflow Guardrails
- Client Onboarding Reliability
- Automation Release QA

Each pack should reuse:
- deterministic scanner;
- secret gate;
- business-context intake;
- evidence-first report;
- verification checklist;
- one re-scan.

The pack changes:
- intake questions;
- prioritized rules;
- synthetic test cases;
- report language;
- buyer-specific landing page.

---

## What to build now, before registration

1. Build synthetic fixtures for the top 5 problem packs.
2. Add vertical-specific intake schemas/questions.
3. Add rule priorities for lead, finance, AI, onboarding and agency QA.
4. Add deterministic acceptance-test generators.
5. Create private draft landing pages, not public paid offers yet.
6. Add prospect tags to the acquisition queue by problem pack.
7. Prepare one sample report per top vertical.
8. Do not build live Make API integrations or monitoring infrastructure yet.

---

## Recommended build order

### Wave A — strongest demand + closest to current engine
1. Lead Flow Reliability
2. Invoice & Payment Sync
3. AI Workflow Guardrails
4. Client Onboarding Reliability
5. Automation Release QA

### Wave B — after first customer evidence
6. E-commerce Operations Integrity
7. Runtime Evidence Diagnostic
8. Continuous monitoring / anomaly detection

---

## Validation rule

A vertical becomes a public paid offer only when all are true:
- at least several independent public buyer signals exist;
- PCFlows has a synthetic fixture covering its core failure cases;
- the report can be delivered without pretending to know live state;
- the scope is understandable in one sentence;
- the work can be delivered without requiring Paul as a daily operator.

Do not publish new offers only because they sound interesting.
