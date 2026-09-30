# PCFlows Runtime Test Contract

Updated: 2026-09-25

For future connected verification, PCFlows should not need raw production payloads to prove common business outcomes.

A test scenario can expose a small allowlisted result object containing only proof-oriented fields such as:
- synthetic business key;
- external side-effect IDs/count;
- failure injected/observable;
- recovery succeeded;
- final state;
- handoff action count;
- invoice total / synthetic paid amount / paid-state boolean;
- required/missing onboarding resources;
- whether invalid AI output was rejected before a write.

`runtime_test_contract.py` strips unknown fields and evaluates reusable acceptance assertions.

## Examples

### Duplicate invoice/lead
Run the same synthetic business key twice.
Pass only when both runs identify the same single external side effect.

### Partial payment
Use a synthetic invoice total of 2000 and payment of 500.
Pass only when the workflow does **not** mark the item fully paid.

### AI malformed output
Inject invalid structured output.
Pass only when the invalid output is rejected and no protected write occurs.

### Client onboarding
Declare the required synthetic resources.
Pass only when the missing-resource list is empty.

## Privacy

The contract intentionally does not allow:
- customer email;
- full payload;
- credentials;
- API tokens;
- private webhook URLs.

Unknown fields are dropped before PCFlows evaluates/stores the proof object.

## Role in Verified Repair

This result contract can feed:
- rule-specific `fix_verification.py`;
- specialist `pack_acceptance_verification.py`;
- the per-issue `resolution_contract.py`.

It is a future runtime-verification interface, not evidence that a live Make connection already exists.
