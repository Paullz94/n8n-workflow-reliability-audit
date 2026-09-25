# Checkout Provider Matrix — 2026-09-25

| Requirement | Payhip + Stripe | Lemon Squeezy | Gumroad |
| --- | --- | --- | --- |
| Monthly platform fee at validation stage | EUR/USD 0 | EUR/USD 0 | EUR/USD 0 |
| Automatic digital delivery | Yes | Yes | Yes |
| Payment-provider verification available | Stripe | Lemon Squeezy records | Gumroad records |
| Marketplace/discovery gate | >= USD 10 genuine sales + review | >= 3 sales or USD 50 + review | separate eligibility/review |
| Self-purchase counts for marketplace gate | No | not used for internal validation | not used for internal validation |
| Webhook/event path | paid/refunded webhooks | API/webhooks | not selected for phase 1 |
| Tax handling noted in current docs | EU/UK digital VAT | Merchant of Record | platform-specific |
| Phase-1 decision | PRIMARY | FALLBACK | NOT SELECTED |

## Decision

Use Payhip + Stripe for the first commercial-validation loop because it preserves EUR 0 owner capital, automates delivery, gives payment-provider evidence, and can unlock platform discovery after a single EUR 39 genuine sale if the account/product passes review.

This is a commercial-operating decision, not tax or legal advice. The owner must complete regulated payment onboarding and choose truthful tax/business settings.
