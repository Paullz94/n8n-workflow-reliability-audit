# PCFlows Outbound Direct-Marketing Gate

Research date: 2026-09-25
Status: outbound cold-email sending remains disabled.

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
