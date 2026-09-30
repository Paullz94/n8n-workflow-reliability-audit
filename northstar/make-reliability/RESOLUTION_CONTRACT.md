# Resolution Contract

Updated: 2026-09-25

PCFlows now treats every accepted issue as an explicit definition-of-done contract.

For each finding:
- rule;
- affected module;
- customer/business description of the problem;
- verification mode;
- verification goal;
- required runtime assertions;
- close condition.

## Closure policy

A customer issue is either:
- **open**
- **closed_verified**

There is deliberately no vague "probably fixed" closure state.

For runtime-dependent findings, the issue remains open until:
1. the revised blueprint clears the relevant static condition where applicable;
2. every rule-specific runtime assertion passes;
3. the runtime result is independently observable by PCFlows through an authorized connected test path.

The entire repair case closes only when **every accepted issue** is closed_verified.

## Important consequence

If PCFlows cannot obtain the necessary proof for an issue:
- the issue remains open;
- PCFlows must not tell the customer the repair is finished;
- a future Verified Repair offer must either continue remediation/testing or follow its documented failure/refund policy.

This is the practical meaning of Paul's requirement that a customer issue should be 100% fixed before PCFlows calls the job complete.
