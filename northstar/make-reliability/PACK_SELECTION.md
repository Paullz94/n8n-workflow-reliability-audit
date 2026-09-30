# Automatic Pack Selection

Updated: 2026-09-25

`pack_selector.py` selects a problem-specific audit pack only from the small allowlisted business context.

It can route to:
- Lead Flow Reliability;
- Invoice & Payment Sync;
- AI Workflow Guardrails;
- generic Data Integrity Audit.

Safety:
- it never reads credentials/customer payloads;
- it does not infer live failures;
- if no pack has evidence, use generic;
- if two packs tie, use generic rather than guessing.

This means ordinary customers do not need Paul to decide which product/report template applies.
