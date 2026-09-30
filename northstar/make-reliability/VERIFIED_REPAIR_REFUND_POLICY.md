# Verified Repair Failure & Refund Policy — Internal

Updated: 2026-09-25
Public status: disabled until Verified Repair launches.

## Principle

PCFlows may only accept a Verified Repair case when `fix_eligibility.py` says the issue is independently testable.

If PCFlows accepts that case, the commercial promise is:

> The accepted issue is complete only when its explicit definition of done reaches `closed_verified`.

## Full repair-fee refund

Refund the Verified Repair fee in full when all are true:
- PCFlows accepted the issue as eligible for Verified Repair;
- the customer supplied the required delegated access/test prerequisites on time;
- the customer did not materially change the target/scope;
- PCFlows reaches the agreed bounded delivery-window end without getting every accepted issue to `closed_verified`.

Also refund the repair fee when:
- PCFlows causes a critical production deployment incident and automatic rollback fails;
- PCFlows materially fails to provide the contracted repair attempt/service.

A refund does **not** convert an unverified repair into a successful repair. The issue remains explicitly not verified fixed.

## No automatic refund while blocked by customer prerequisite

Do not automatically refund merely because work cannot proceed while:
- customer revoked required Make access;
- customer did not provide the agreed sandbox/test resources;
- customer changed the target scenario or root-cause scope after acceptance;
- customer prevents the synthetic acceptance tests from being executed.

In those cases:
- case remains open/blocked;
- explain exactly which prerequisite is missing;
- restart the bounded delivery window only according to the final public terms.

## No silent scope expansion

One Verified Repair purchase is for the accepted issue contract(s) explicitly included in the order.

If testing reveals a separate unrelated defect:
- record it as a new finding;
- do not hide it;
- do not silently add unlimited extra repair work;
- finish/verify the accepted issue if possible;
- route the new issue through qualification.

## Duplicate charge

A verified duplicate Stripe charge is refunded independently of technical repair outcome.

## Customer cancellation

Final consumer/business cancellation rights must follow applicable Belgian/EU law and the final public service terms at launch. This internal technical refund policy does not override statutory rights.

## Automation

`repair_outcome_policy.py` already encodes:
- verified success -> no refund;
- accepted but not verified by bounded deadline -> refund required;
- critical rollback failure -> refund required;
- customer access blocker -> not complete, no automatic technical-policy refund;
- changed target/scope -> re-qualify, no fake completion.

Stripe refund execution must use the connected provider object and then reconcile the event into the strict Northstar ledger.

## Public launch requirement

Before Verified Repair becomes purchasable:
- insert the final bounded delivery-window wording;
- reconcile this policy with the official Belgian/EU consumer/business terms;
- test one real sandbox repair end-to-end;
- test the provider refund path with a non-revenue test transaction that is excluded from the EUR1,000 target.
