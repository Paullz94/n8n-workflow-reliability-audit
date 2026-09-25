# Stripe Revenue Reconciliation Runbook

Updated: 2026-09-25

Purpose: move only authenticated, finalized Stripe financial events into the strict Northstar revenue journal.

## Safety properties

- Provider data must come from the connected Stripe account or a signature-verified pipeline.
- A JSON file cannot make itself trusted; the operator must know its provenance.
- Reconciliation is dry-run by default.
- Pending refunds are ignored until Stripe marks them successful/final.
- Existing journal events are immutable. A conflicting provider event causes a hard stop for manual reconciliation.
- Owner/test/refunded payments remain excluded under `ledger_engine.py`.

## Offline command

After saving authenticated Stripe objects/events to a local JSON array:

```bash
python reconcile_stripe_snapshot.py stripe-snapshot.json \
  --journal ledger_journal.json \
  --trusted-provider-snapshot
```

This prints the proposed additions and totals without writing the journal.

To produce a candidate updated journal:

```bash
python reconcile_stripe_snapshot.py stripe-snapshot.json \
  --journal ledger_journal.json \
  --trusted-provider-snapshot \
  --out-journal ledger_journal.next.json
```

Review the diff before replacing the canonical local journal.

## Revenue gate

Only `verified_gross_revenue` from `ledger_engine.py` counts toward the EUR 1,000 Northstar target.

A successful refund — including a partial refund — disqualifies the entire associated payment from the target under the intentionally conservative Northstar policy.

## Privacy

Do not commit real Stripe snapshots, customer identifiers, real journal data, or reconciled customer records to the public repository.
