# Qualification Gate

Updated: 2026-09-25

PCFlows should not try to sell the EUR 149 audit to every free-scanner user.

`qualify_audit.py` routes a sanitized blueprint/context into one of four outcomes:

1. **resanitize_required**
   - possible secret-like literal found;
   - do not continue with paid analysis.

2. **invalid_input**
   - not a supported usable Make blueprint;
   - request a fresh export.

3. **context_required**
   - blueprint is analyzable but paid prioritization lacks the minimum non-sensitive business context.

4. **paid_audit_candidate**
   - meaningful reliability/data-integrity signals exist, or the customer identifies business-critical side effects.

5. **free_preflight_sufficient**
   - static evidence does not currently justify a deeper paid review.

## Commercial principle

Do not force conversion.

If the free preflight is sufficient, say so. This improves trust and keeps the paid pilot focused on situations where contextual reliability analysis has a plausible business value.

## What qualification does not do

- It does not estimate customer budget.
- It does not infer willingness to pay.
- It does not make a legal/compliance determination.
- It does not prove a workflow is defective.
- It does not replace runtime evidence.

The first paid customers remain willingness-to-pay experiments; qualification only protects scope and fit.
