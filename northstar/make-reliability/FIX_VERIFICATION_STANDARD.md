# PCFlows Fix Verification Standard

Updated: 2026-09-25

## Core rule

PCFlows must never tell a customer an issue is **fixed** merely because a static finding disappeared from a revised blueprint.

Customer-facing remediation states are:

1. **Detected**
   - the original artifact matches a deterministic reliability rule.

2. **Statically cleared**
   - the revised blueprint no longer matches that rule.
   - this proves only the structural condition changed.

3. **Evidence supported**
   - supplied sanitized/customer test evidence supports the remediation.
   - PCFlows did not independently execute the test, so this is not called independently verified.

4. **Verified fixed**
   - the static signal is cleared;
   - every rule-specific runtime assertion passes;
   - the runtime evidence comes from a connected test run PCFlows can independently observe.

5. **Verified mitigation, signal still present**
   - runtime evidence supports the design but the static signal remains.
   - this may be an intentional design choice, but PCFlows must not label it fixed.

## Why this matters

A blueprint cannot prove:
- whether a remote API committed before a timeout;
- whether duplicate protection works at the destination;
- whether two real concurrent runs produce deterministic state;
- whether a partial payment is interpreted correctly by every downstream system;
- whether an AI/human handoff actually stops later messages;
- whether operators can locate/replay failed business work.

Those questions require execution evidence.

## Current limitation

PCFlows currently has no direct Make.com connector in the available plugin set.

Therefore today:
- static remediations can be proven structurally;
- customer-supplied sanitized execution evidence can support a remediation;
- **runtime-dependent findings must not be called independently “verified fixed” yet**.

A future connected Make test/sandbox path can unlock the final verification state without changing this standard.

## Rule-specific runtime assertions

Examples:

### Retry / idempotency
- duplicate replay executed;
- exactly one intended external side effect.

### Concurrency
- concurrent test executed;
- deterministic final state;
- zero duplicate side effects.

### Missing recovery
- controlled failure injected;
- failure observable;
- recovery succeeds;
- zero duplicate side effects.

### Resume
- failure injected;
- fallback distinguishable;
- downstream false success prevented.

### Incomplete executions
- failure injected;
- failed work locatable;
- resume/replay succeeds;
- zero duplicate side effects.

## Commercial rule

Until independent runtime verification is available:
- sell **audit + remediation plan + verification plan + re-scan**;
- do not advertise “we guarantee we fix your Make scenario”;
- do not change “statically cleared” into “fixed” in customer-facing language;
- do not launch a done-for-you repair package.

A customer should know exactly which parts PCFlows verified and which parts still require runtime proof.
