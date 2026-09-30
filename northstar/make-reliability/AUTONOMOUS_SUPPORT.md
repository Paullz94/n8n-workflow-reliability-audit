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

## Support mailbox state — connected

The public PCFlows support mailbox **PCMotionstudios@gmail.com** is connected and verified through the Gmail connector.

Operational labels created:
- `PCFlows/Customer`
- `PCFlows/Order`
- `PCFlows/Needs Review`
- `PCFlows/Closed`

An hourly condition-watch automation (`PCFlows Inbox Operator`) is enabled to process new routine PCFlows customer/support/order messages autonomously. During the registration pause it must not solicit payment or claim checkout is open. Owner escalation remains limited to the explicit exception classes above.
