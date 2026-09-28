# PCFlows Sales Email Standard

Updated: 2026-09-28

Purpose: every PCFlows outbound email should read like a concise, thoughtful business introduction written specifically for the recipient company.

This standard is about relevance and legitimate deliverability. It must never be used to evade spam filters, provider controls, rate limits, suppression, or platform rules.

## Core voice

PCFlows emails should be:
- plain, professional and human-readable;
- specific about what PCFlows actually does;
- concise enough to read in under one minute;
- centered on a real operational problem;
- transparent about the current scope;
- free of fabricated experience, testimonials or certification claims.

Avoid:
- generic AI-sounding openings;
- hype, superlatives and fake urgency;
- "revolutionary", "game-changing", "unlock", "seamless", "leverage", "cutting-edge solution";
- long feature lists;
- excessive punctuation;
- emojis;
- fake reply prefixes;
- invented familiarity;
- claims that PCFlows has customer case studies it does not have.

## What PCFlows says it does

Preferred plain-language description:

PCFlows reviews Make.com automations for reliability and data-integrity risks before those risks turn into duplicate actions, missing work or inconsistent business data.

Typical checks:
- duplicate effects / idempotency;
- retries and repeated webhook events;
- silent skips and missing work;
- partial completion after an API failure;
- concurrency / ordering;
- recovery and observability;
- lead/CRM, invoice/payment, onboarding and AI-action guardrails.

Do not describe PCFlows as a full-service build agency unless that scope actually exists later.

## First-email structure

A normal first message should be roughly 90–150 words and contain:

1. A specific reason the company was selected.
2. One concrete reliability risk that logically follows from the services it publicly offers.
3. A short description of PCFlows.
4. A low-friction next step.
5. A clear opt-out where direct-marketing rules require it.

Do not dump the complete price ladder into the first cold message.
Do not include checkout links in a first unsolicited email.
Do not attach files.
Prefer plain text.
Use at most one normal PCFlows site link when it genuinely helps, and omit it from the first message when deliverability/relevance is better without it.

## Example tone — automation agency

Subject: Independent QA for Make.com handoffs

Hi,

I came across <Company> because you build Make.com / workflow automations for clients.

PCFlows focuses on the part that is easy to miss during a normal build: whether retries can duplicate an external action, whether a failed API call leaves half-completed state behind, and whether a scenario can finish without the expected business result.

For agencies, the useful fit is usually a small independent QA pass before client handoff rather than another implementation layer. We work from a sanitized Make blueprint and return a prioritized reliability/data-integrity review with concrete verification steps.

If that is relevant to the way you deliver automations, I can send a short sample of the review format.

Regards,
PCFlows
PCMotionstudios@gmail.com

If this is not relevant for your organisation, reply STOP and I will not contact this address again.

## Example tone — business with an existing workflow

Subject: Reliability review for your Make.com workflow

Hi,

I saw that <Company> is already using Make.com for <specific public use case>.

PCFlows reviews existing Make scenarios for duplicate actions, unsafe retries, silent skips, partial failures and recovery gaps. The goal is not to rebuild the automation, but to identify where a workflow can look successful while still creating wrong or incomplete business data.

The review works from a sanitized blueprint, so production credentials are not needed for the audit pass.

If reliability QA is useful for that workflow, I can send the audit format and explain what is checked.

Regards,
PCFlows
PCMotionstudios@gmail.com

If this is not relevant for your organisation, reply STOP and I will not contact this address again.

## Personalization requirement

Before sending, the operator must be able to answer:
- Why this exact company?
- What public evidence shows it uses/delivers relevant automation?
- What exact PCFlows risk category maps to that evidence?
- Is the recipient address allowed under the applicable outreach rule?
- Has this company/domain already been contacted, bounced or opted out?

If any answer is missing, do not send.

## Deliverability rules

Legitimate deliverability only:
- tiny batches;
- high relevance;
- one initial message per canonical company/domain;
- plain text;
- no attachments;
- no tracking pixels;
- no shortened URLs;
- no purchased lists;
- no multiple aliases after a bounce;
- no named-person email when the legal route only supports generic legal-entity addresses;
- no repeated chase sequence;
- at most one relevant follow-up when permitted;
- hard suppression after opt-out, clear rejection or hard bounce;
- provider warnings pause outbound rather than trigger evasion.

A message being "less likely to be spam" must come from being wanted/relevant and technically clean, not from tricks intended to bypass spam detection.


## Belgian legal-entity email labelling

For unsolicited Belgian B2B advertising sent under the legal-entity exception:
- the message must be clearly recognizable as advertising immediately on receipt;
- use an explicit label such as `Reclame — ...` in Dutch or `Publicité — ...` in French;
- identify PCFlows clearly;
- include a simple reply-based objection path;
- never send under this route to named-person addresses;
- use only generic legal-entity addresses such as info@, contact@, hello@, sales@ or partnerships@ after verifying that the mailbox belongs to the company/legal entity.

Do not weaken or disguise the advertising label for deliverability. Compliance takes precedence.

## Support wording

PCFlows may truthfully state that routine support questions inside the defined service scope are monitored continuously, including outside office hours, because the PCFlows inbox operator runs around the clock.

Do not promise instant replies or guaranteed 24/7 human support.

Preferred wording:
`Routinevragen binnen onze vaste scope worden doorlopend gemonitord, ook buiten kantooruren; uitzonderingen worden geëscaleerd.`

French:
`Les questions de support routinières dans notre périmètre sont surveillées en continu, y compris hors heures de bureau; les exceptions sont escaladées.`
