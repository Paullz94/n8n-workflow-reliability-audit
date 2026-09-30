# PCFlows Outbound Direct-Marketing Gate

Research date: 2026-09-25
Status: narrow pre-launch B2B outreach enabled for verified generic legal-entity mailboxes; paid service starts 2026-10-01.

## Why there is a gate

Belgian Data Protection Authority (GBA/APD) guidance treats direct marketing broadly. It covers promotional communications addressed directly to identifiable natural persons in both private and professional contexts when personal data is processed.

The GBA states that direct-marketing processing needs a valid GDPR legal basis. In practice, consent and legitimate interests are common, but neither applies automatically: the controller must document the chosen basis and, for legitimate interests, assess legitimacy, necessity and the balance against the person's rights/reasonable expectations.

People also have an unconditional right to object to processing for direct-marketing purposes; after an objection, processing for that purpose must stop.

Official references:
- https://www.gegevensbeschermingsautoriteit.be/professioneel/thema-s/direct-marketing/toestemming-en-rechtmatige-belangen
- https://www.dataprotectionauthority.be/professionnel/rgpd-/droits-des-citoyens/droit-d-opposition
- https://dataprotectionauthority.be/burger/thema-s/marketing/wat-is-direct-marketing

## PCFlows default

Do not treat "public work email found by Clay" as automatic permission to market.

Until the compliance gate below is documented, Clay may:
- discover companies;
- identify likely business roles;
- enrich public professional data;
- score fit;
- collect company-level buying signals.

It may **not** trigger autonomous cold sales email.

## Gate before autonomous cold email

All must be true:
- [ ] Belgian enterprise/VAT launch gate complete.
- [ ] Processing purpose documented.
- [ ] Legal basis selected and documented for the exact outreach pattern.
- [ ] Legitimate-interest assessment completed when relying on legitimate interests.
- [ ] Privacy information for prospecting is published/available.
- [ ] Data minimization rules documented.
- [ ] Suppression/objection list exists.
- [ ] Every outreach message includes a clear, easy objection/opt-out path.
- [ ] Objections automatically stop future direct-marketing processing.
- [ ] Maximum cadence remains small and human-realistic.
- [ ] No purchased/scraped bulk mailing lists.
- [ ] No sensitive-category targeting.
- [ ] Platform/community rules independently allow the outreach.

## Safer channels first

Before cold email, prefer:
1. inbound PCFlows site;
2. public job posts where the buyer explicitly requests help;
3. marketplace-native proposals;
4. partner/referral opportunities where contact is expected;
5. opt-in/interest replies.

This keeps the first EUR1,000 validation cycle commercially focused while minimizing legal/privacy complexity.

## Automation flag

Current policy:
`autonomous_cold_email_enabled = false`

Do not flip this merely because registration completes. Registration and direct-marketing compliance are separate gates.


## Narrow generic-B2B route prepared

A post-VAT outbound route is prepared for Belgian B2B prospecting, but it is **not active yet**.

The route is deliberately narrower than generic cold email:
- verified business/legal-entity target only;
- generic role/company mailbox only (for example info@, contact@, sales@ or partnerships@);
- no named-person mailbox under this route;
- one initial message per canonical company/domain;
- high-fit automation/reliability context required;
- plain-text, no attachment, no tracking;
- clear STOP / objection instruction;
- company/domain suppression after opt-out, rejection or hard bounce;
- at most one relevant follow-up when legally and operationally permitted;
- tiny batch size and provider-reputation monitoring.

This route is designed around current Belgian e-communications/direct-marketing rules for legal entities and the GDPR objection requirements. It must be re-checked at activation time.

The separate VAT/economic-activity launch gate still applies. Do not use this route to start commercial activity before the required VAT readiness is complete.

Email copy must follow `SALES_EMAIL_STYLE.md`.

## Activation sequence

Before switching `autonomous_cold_email_enabled` to true:
1. VAT/e604 status confirmed and commercial activity legally open;
2. seller identity/privacy information current;
3. suppression state and canonical company-domain dedupe verified;
4. target qualifies as a legal-entity B2B recipient for the selected mailbox route;
5. message passes `SALES_EMAIL_STYLE.md`;
6. first batch limited to two companies;
7. inspect delivery/replies before expanding.


## Pre-launch commercial messaging — 2026-09-28

PCFlows may conduct limited pre-launch B2B advertising before 2026-10-01 when all of the following are true:
- the message clearly says PCFlows officially starts service on 2026-10-01;
- the recipient is a verified generic mailbox belonging to a legal entity;
- the message is relevant to that company's public automation/integration activity;
- the message is clearly labeled as advertising and includes an easy objection/STOP route;
- no paid service is performed before 2026-10-01;
- no payment or invoice is accepted/issued before 2026-10-01;
- the outreach does not imply that PCFlows is already delivering paid services before the registered start date.

This is a pre-launch acquisition activity, not permission to backdate commercial delivery or payment.

The owner confirms VAT readiness is in order. The numeric VAT identifier stays private until a genuine customer requires it for commercial documentation.
