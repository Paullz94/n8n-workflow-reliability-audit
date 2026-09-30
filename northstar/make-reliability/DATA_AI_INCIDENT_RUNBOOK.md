# PCFlows Data / AI Incident Containment Runbook

Updated: 2026-09-25

## Assumption

AI output is never trusted enough to override privacy, case-isolation, authorization, verification or rollback gates.

## Suspected sensitive data before delivery

Automatic:
1. stop case processing;
2. do not send the report/package;
3. quarantine the current technical artifacts from AI use;
4. request a newly sanitized input;
5. resume only from the clean replacement.

No Paul input is needed unless the data was actually exposed outside its intended case.

## Cross-case binding mismatch

Automatic:
1. freeze both/all affected case scopes;
2. block outbound delivery;
3. preserve hashes/audit trail;
4. determine whether data was only mismatched internally or actually exposed.

If no exposure occurred:
- fix the isolation defect;
- add a regression test;
- resume only after validation.

If customer A data was actually exposed to customer B:
- keep cases frozen;
- escalate to Paul because privacy/legal notification obligations may apply.

## Unauthorized production write attempt

Automatic:
- deny the write;
- keep production unchanged;
- preserve the attempt in the case audit trail;
- do not let AI retry with broader permissions.

## Production rollback failure

Automatic first:
- stop further writes;
- preserve current/original hashes and execution IDs;
- mark case critical.

Then escalate because the customer's live system may be in uncertain state.

## AI hallucination / unsupported claim

Automatic:
- discard the AI output;
- do not send it;
- regenerate only from the bounded AI packet;
- deterministic findings remain the source of truth.

## Rule

The safest default is **fail closed**:
if PCFlows cannot prove that data/scope/authorization belongs to the active case, it does nothing rather than guessing.
