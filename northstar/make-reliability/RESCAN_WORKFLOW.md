# Included Re-scan Workflow

Updated: 2026-09-25

The EUR 149 pilot includes one asynchronous re-scan of the same scenario after remediation.

Use compare_rescan.py rather than simply generating a second unrelated report.

## Command

python compare_rescan.py original-sanitized.json revised-sanitized.json --json-out rescan.json --md-out rescan.md

Output categories:
- Resolved — deterministic findings present before but not after.
- Remaining — deterministic findings still present at the same rule/module/path.
- New — findings introduced in the revised blueprint.

## Important limit

"Resolved" means only that the revised blueprint no longer matches the static rule.

It does not prove the runtime business problem is fixed. The customer should still execute the original verification plan with safe synthetic data.

## Privacy

Both versions must be sanitized. Secret detection on either blueprint hard-stops the comparison.

Do not commit real before/after customer blueprints or reports to the public repository.
