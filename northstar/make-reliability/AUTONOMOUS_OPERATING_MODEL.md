# PCFlows Autonomous Operating Model

Updated: 2026-09-25

## Prime directive

After one-time legal/account prerequisites are connected and approved, routine PCFlows operation should not depend on Paul as the daily operator.

The intended loop is:

public demand -> qualification -> compliant outreach/listing -> inquiry response -> free preflight -> checkout -> provider-verified payment -> safe intake -> audit -> bounded AI interpretation -> QA -> delivery -> re-scan -> support/refund -> financial reconciliation -> product learning.

## What AI should operate autonomously

### Acquisition
- daily public demand research;
- rank and discard low-fit prospects;
- tailor channel-native outreach on channels where autonomous/AI content is permitted;
- publish/update owned-site content;
- manage connected social publishing tools within channel rules;
- stop outreach where rules prohibit AI-generated content;
- measure replies and conversion.

### Customer communication
- answer standard scope/privacy/pricing questions;
- send free scanner/intake instructions;
- request re-sanitization;
- qualify free vs paid fit;
- match order references;
- send delivery and re-scan messages;
- close bounded support threads.

### Payments
- Stripe hosts checkout and captures payment without manual intervention;
- only provider-verified live external payments enter fulfillment/revenue;
- duplicate-charge / out-of-scope-before-delivery / material-non-delivery refunds can follow deterministic policy;
- every refund is reconciled into the strict Northstar ledger;
- no owner/test payment counts as revenue.

### Fulfillment
- secret gate;
- pack selection;
- deterministic scan;
- vertical-specific prioritization/acceptance tests;
- privacy-bounded AI review;
- unsupported-claim QA;
- delivery package;
- before/after re-scan.

### Bookkeeping evidence
- retain provider/order/invoice evidence;
- classify expenses/refunds;
- reconcile Stripe and business records;
- never publish customer financial data.

## Owner-only prerequisites / exceptions

Paul should only be required for things that cannot legitimately be delegated:
- KBO/VAT/official legal attestations;
- identity/KYC;
- connecting/authorizing new third-party accounts;
- explicit new owner-capital spend approval;
- exceptional legal/payment disputes not resolved by published policy;
- platform CAPTCHA/identity checks or terms that require the human account holder.

These are prerequisites/exceptions, not daily operations.

## Current integration reality

Already connected/available:
- GitHub: code/site/product state.
- Stripe: product, checkout, payments/refunds/provider truth.
- Gmail connector: one Gmail account is connected, but the currently connected mailbox is not the public PCFlows support mailbox.
- Web research: public demand research.
- Scheduled task: daily Make.com opportunity research.

Still needed for fully autonomous launch:
- official Belgian enterprise/VAT completion;
- connect/authorize the **public PCFlows support mailbox** to Gmail so routine customer replies can be performed on the actual support address;
- connect at least one autonomous publishing/prospecting channel if desired.

Current plugin discovery:
- no direct Upwork or Contra action plugin was returned by the plugin directory search;
- Metricool is available for connected social publishing/analytics;
- Clay is available for prospect discovery/engagement;
- channels without a connector still require a supported cloud-browser/Work workflow or platform-native manual account setup before AI can operate them.

## Channel safety

Autonomy never means:
- CAPTCHA bypass;
- fake multiple accounts;
- fabricated testimonials/case studies;
- bulk spam;
- impersonating a human where platform rules prohibit AI content;
- circumventing marketplace payment rules;
- hiding AI-generated participation from communities that forbid it.

If a channel prohibits the autonomous action, the autonomous decision is to **not perform it** and move to another channel.

## Lifecycle engine

`autonomous_lifecycle.py` encodes the default action for routine states and isolates genuine owner-only gates.

The operating target is that ordinary customer cases never require an owner decision.
