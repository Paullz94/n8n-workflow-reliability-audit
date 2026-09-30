# Customer Data & AI Containment Standard

Updated: 2026-09-25

## Core principle

PCFlows must be designed on the assumption that an AI model can make mistakes.

Safety therefore cannot depend on the model "remembering to be careful".

The system must constrain what the AI can see and what it can do.

## 1. One case, one data boundary

Every paid order gets a pseudonymous `case_scope_id`.

Customer A's artifacts may never be loaded into Customer B's case.

Future storage/database rules:
- partition every artifact by case scope;
- no shared customer-document vector store;
- no model prompt may retrieve another case's files;
- no cross-customer examples from real customer data;
- aggregate product analytics must use non-customer-identifying counters only.

`case_isolation.py` provides the deterministic case namespace/binding guard.

## 2. No raw customer database as AI context

PCFlows does not need a customer's whole CRM/customer database to diagnose the current product scope.

Preferred inputs:
- sanitized blueprint;
- abstract business goal;
- synthetic test records;
- minimal privacy-bounded runtime proof object.

If real production data is required to reproduce a future issue:
- first minimize/redact it;
- use the smallest possible record subset;
- never add it to general AI memory/training examples/product documentation;
- delete according to the case retention policy after the service/legal retention need ends.

## 3. Literal sensitive-data hard stop

`customer_data_guard.py` detects several high-risk literal classes before AI/delivery processing:
- non-synthetic email addresses;
- E.164 phone numbers;
- IBAN-like values;
- valid payment-card numbers;
- JWT-like tokens.

Diagnostics return type/path only, not the raw value.

This is additional to the existing credential/secret detector.

It is intentionally not marketed as a complete PII detector. No detector can infer every real name/address/customer identifier safely.

## 4. AI is advisory; deterministic gates are authoritative

AI may:
- explain;
- prioritize;
- propose a candidate remediation;
- propose test cases.

AI may not decide by itself:
- that a payment is valid;
- that a repair is fixed;
- that a production write is authorized;
- that customer A data belongs to customer B;
- that a risky/destructive test is acceptable;
- that a refund can be ignored;
- that a secret/PII warning can be bypassed.

Those decisions are deterministic policy gates.

## 5. Unrealistic repair requests

Verified Repair must reject or downgrade requests such as:
- "guarantee this automation never has another bug";
- "guarantee the external API never goes down";
- "fix all my workflows for one bounded repair order";
- "prove it using real customer/payment data only";
- "fix behavior that is actually a third-party vendor defect";
- an issue that cannot be reproduced/observed and has no measurable definition of done.

`repair_scope_gate.py` routes these to:
- diagnostic/audit first;
- test-environment preparation;
- scope split;
- decline absolute promise.

## 6. AI glitch containment

A bad AI suggestion should fail harmlessly because:
- production writes require explicit case/customer authorization;
- target scenario must be allowlisted;
- sandbox proof comes first;
- exact revision hash binds sandbox to production;
- every runtime assertion must pass;
- any failed production acceptance test triggers rollback;
- case closure requires all issue contracts + specialist acceptance tests + no new static findings.

## 7. Customer promise

Do not promise "AI never makes mistakes."

Promise the stronger operational property:

> An AI mistake is not enough to authorize, deploy, or certify a customer fix. Deterministic scope, privacy, authorization, test, rollback, and closure gates stand between AI output and customer production state.
