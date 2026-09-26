# PCFlows Fulfillment Runbook

This runbook is for paid B2B orders after checkout is publicly activated.

## 1. Payment event

Source of truth: Stripe.

A customer is considered paid only when Stripe shows a successful settled external-customer payment for the relevant PCFlows offer.

Record the Checkout Session/payment reference, offer, business/customer email, amount/currency, and payment status.

Apply the Gmail label PCFlows/Paid Customer when the corresponding intake email arrives.

## 2. Intake

Stripe redirects the buyer to intake.html, carrying offer and session_id.

The intake page creates a pre-filled email to pcmotionstudios@gmail.com.

Required metadata:
- company;
- business outcome;
- connected systems by name;
- symptom/risk;
- n8n version + hosting type;
- node count;
- acceptance condition.

Required file:
- one sanitized n8n workflow JSON export.

Reject or pause intake when secrets are present, personal/customer data is unnecessarily present, scope exceeds the purchased package, or the supplied export is not a single n8n workflow object.

## 3. Static delivery pack

Run this command:

    python package_audit.py customer-workflow.json --output-dir delivery --order-ref CHECKOUT_SESSION_ID

Expected output:
- 01-audit-report.md
- 02-audit-report.json
- 03-client-summary.md
- 04-synthetic-verification-plan.md
- MANIFEST.json

The manifest cryptographically fingerprints both the supplied export and generated package files.

## 4. Manual review gate

The automated package is not the final paid audit by itself.

Before delivery:
- inspect critical/high findings;
- remove obvious heuristic false positives;
- add concise context specific to the customer's stated business outcome;
- ensure no secret values appear;
- ensure recommendations remain within fixed scope;
- confirm all claims are evidence-backed.

## 5. Delivery

Email the final package to the paying business contact.

The delivery email should include the order reference, package scope, concise top risks, attached/final report files, reminder that static review is not production certification, and the next action for the synthetic verification plan.

## 6. Re-scan

The EUR 249 audit includes one post-remediation re-scan.

Use the new export as a separate input. Preserve both input hashes and never overwrite the original delivery pack.

## 7. Retrofit

The EUR 890 retrofit starts only after one specific accepted failure/risk is written down, the expected result is measurable, a rollback path is defined, and production secrets/access are not required by default.

Create before/after evidence and include the exact export hashes.

## 8. Completion

Mark the engagement complete only when deliverables were sent, the purchased revision/re-scan allowance is either completed or explicitly unused, no customer secrets remain stored in public repositories, and Stripe payment/refund state is reconciled.

Only settled non-refunded revenue counts toward the EUR 5,000 target.
