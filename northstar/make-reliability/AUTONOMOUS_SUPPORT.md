# Autonomous Customer Communication Policy

Updated: 2026-09-25

Routine PCFlows support should not require Paul.

`support_router.py` handles common intents:
- price;
- scope;
- privacy/sanitization;
- file intake;
- re-scan;
- implementation requests;
- deterministic refund-policy questions;
- certification boundaries;
- legal/tax boundary;
- one bounded clarification for unknown messages.

## Sending policy

Once the public PCFlows support mailbox is connected:
- AI may read and respond to routine product/support messages;
- replies must remain within published price/scope/terms;
- AI must not negotiate custom legal terms, invent discounts, promise unsupported deadlines or claim certification;
- attachments are processed only through the sanitization/secret gate;
- marketplace-originated conversations stay on the marketplace when required by its rules.

## Owner escalation

Do not escalate routine questions.

Escalate only:
- legal/identity attestation requiring the proprietor;
- exceptional dispute outside refund policy;
- explicit new owner-capital spend;
- third-party account authorization/KYC/CAPTCHA;
- a request that materially changes the contract/product beyond published scope.

## Required one-time prerequisite

The Gmail connector currently available to ChatGPT is not connected to the public PCFlows support mailbox.

For customer support to be truly autonomous, Paul must once connect/authorize **PCMotionstudios@gmail.com** (or change the public support address to a mailbox already connected). After that, routine inbox work can be handled by the operating policy without daily owner involvement.
