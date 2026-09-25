# Market Evidence — 2026-09-25

## Problem signal

Recent public discussions repeatedly describe AI/vibe-coded apps shipping with missing authorization boundaries, incomplete payment lifecycle handling, and release-readiness gaps.

Reviewed demand signals:
- Reddit r/nocode, “I rescue vibe coded apps for a living…” — 2026-05-21
  https://www.reddit.com/r/nocode/comments/1tjayir/
- Reddit r/vibecoding, “I’ve been auditing vibe-coded apps…” — 2026-06-20
  https://www.reddit.com/r/vibecoding/comments/1ub3yag/
- Reddit r/buildinpublic pre-launch checklist discussion — 2026-09-13
  https://www.reddit.com/r/buildinpublic/comments/1wf412u/

These are directional demand signals, not proof of willingness to pay.

## Competitive evidence

The niche is already monetized and increasingly crowded:
- VibeZero: free scans plus paid plans from USD 15/month — https://vibezero.io/
- VibeCheck: one-time scans at USD 9.99 / 49 / 99 — https://getvibescan.com/
- Etherlabz: fixed audit advertised at EUR 299 — https://etherlabz.com/audit
- boxed-dev/vibe-coding-security: public pre-launch security checklist plus paid product — https://github.com/boxed-dev/vibe-coding-security
- Gumroad contains low-priced vibe-coding checklists with verified sales — https://valeriemur.gumroad.com/l/vibecodingcheck

Conclusion: generic “vibe security” is too broad. Northstar must compete on a narrower release-operations job: local/offline deterministic preflight, failure-path testing, payment lifecycle checks, rollback discipline, and bounded AI-remediation tasks. It must not present itself as a security certification.

## Checkout evidence

### Phase 1: Payhip + Stripe

Published properties reviewed:
- Payhip Free Forever: zero monthly platform fee, 5% Payhip transaction fee.
- Automatic delivery of purchased digital files.
- Stripe can be connected as a payment processor.
- Payhip webhooks include paid and refunded events.
- Payhip Marketplace store eligibility: at least USD 10 in genuine sales plus account review; self-purchases do not count.
- Payhip states it handles EU and UK digital VAT by default.

References:
- https://payhip.com/pricing
- https://help.payhip.com/article/59-adding-a-digital-product
- https://help.payhip.com/article/65-connecting-your-stripe-account
- https://help.payhip.com/article/115-webhooks
- https://help.payhip.com/article/307-marketplace
- https://help.payhip.com/article/127-digital-eu-vat

### Fallback: Lemon Squeezy

Published properties reviewed:
- standard transaction fee 5% + 50 cents with possible additional fees;
- Merchant-of-Record tax handling;
- digital downloads and hosted checkout;
- store activation and identity verification required for live sales;
- marketplace eligibility after at least 3 sales or USD 50 in sales.

References:
- https://www.lemonsqueezy.com/pricing
- https://docs.lemonsqueezy.com/help/getting-started/activate-your-store
- https://docs.lemonsqueezy.com/help/getting-started/verify-your-identity
- https://docs.lemonsqueezy.com/help/marketplace

## Strategic implication

The first genuine sale remains the acquisition bottleneck. After one EUR 39 Payhip sale, the published USD 10 marketplace sales threshold is crossed, though listing still requires platform review. The free local scanner is the lead magnet. Initial acquisition must be organic, platform-compliant, and aimed at people already asking about launch readiness. No owner-funded spend is justified before genuine willingness-to-pay evidence.
