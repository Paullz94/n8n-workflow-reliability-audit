# Verified Repair Agent Protocol

Updated: 2026-09-25
Public status: DISABLED until Make runtime connection gates pass.

## Objective

For every issue accepted into Verified Repair:

> Do not stop at “I changed the automation.”
> Stop only when the issue's definition of done is independently proven.

## Autonomous loop

### 1. Qualify before taking the repair
- identify one bounded root-cause issue;
- build a `resolution_contract`;
- run `fix_eligibility`;
- reject the repair promise if safe independent proof is impossible;
- define production-safe acceptance criteria before changing anything.

### 2. Obtain delegated access
- never request customer tokens by email;
- use the official Make ChatGPT/MCP connection or delegated team/toolbox access;
- confirm customer authorization and target scenario;
- confirm sandbox/test scenario exists or create the bounded test path.

### 3. Snapshot
- retrieve original blueprint;
- hash it;
- record scenario/case identifiers;
- preserve rollback copy;
- never commit the customer blueprint to public GitHub.

### 4. Diagnose root cause
Use:
- deterministic PCFlows findings;
- Make execution evidence;
- customer-described business symptom;
- official Make semantics.

Do not repair only the visible symptom if evidence points to a deeper root cause.

### 5. Create candidate repair in sandbox
AI may modify the sandbox scenario only within accepted scope.

After each candidate:
- re-export/re-read blueprint;
- run static scanner;
- run the relevant business acceptance tests;
- inspect actual side-effect result contract.

If any acceptance criterion fails:
- issue remains open;
- do not progress to production;
- revise and test again.

### 6. Sandbox certificate
Only produce `verified_in_sandbox` when every supplied sandbox acceptance test passes.

The certificate is bound to the exact revised blueprint hash.

### 7. Production deployment
Only the exact sandbox-certified revision may deploy.

Required:
- explicit customer authorization ID;
- allowlisted production scenario;
- backup before PATCH;
- production-safe synthetic test plan.

### 8. Post-deploy verification
Immediately run the production-safe acceptance plan.

If any test fails:
- restore original production blueprint;
- issue remains open;
- continue diagnosis in sandbox;
- never tell the customer the fix succeeded.

### 9. Close issue contracts
Map connected execution evidence to each resolution contract.

Only:
`customer_status = closed_verified`

counts as fixed.

If one accepted issue remains open:
- the repair case remains open.

### 10. Commercial outcome
If PCFlows accepted the issue as Verified Repair but cannot reach closed_verified inside the agreed bounded service window while the customer supplied the required access:
- do not send a success claim;
- refund the Verified Repair fee under the future repair failure policy.

## Prohibited shortcuts

Never close a repair because:
- the blueprint saved successfully;
- the Make run has a green status;
- a static warning disappeared;
- AI says the new design looks correct;
- one happy-path execution passed;
- the customer says “looks okay” without the agreed acceptance evidence.

## Meaning of “100% fixed”

For PCFlows, this phrase must only mean:

**100% of the explicitly accepted issue's agreed definition-of-done assertions have passed.**

It must never mean:
- the customer's entire automation can never have another bug;
- every third-party API will always work;
- future schema/config changes cannot break the scenario;
- PCFlows guarantees outcomes outside the accepted repair scope.

This definition is both stricter and more defensible than a vague repair guarantee.
