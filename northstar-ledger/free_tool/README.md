# Northstar Preflight Lite

A dependency-free local preflight scanner for AI/vibe-coded web app repositories.

## Run

python preflight.py /path/to/project

Optional outputs:

python preflight.py . --markdown preflight.md --json preflight.json

Choose a CI threshold:

python preflight.py . --fail-on high

Exit code 2 means a finding met or exceeded the chosen threshold.

## Lite checks

The free scanner includes bounded checks for:
- likely committed OpenAI and Stripe secrets;
- privileged backend keys exposed through public client environment variables;
- debug mode;
- wildcard CORS signals;
- broadly open Firebase rules;
- committed environment files;
- Stripe usage without obvious webhook signature verification;
- missing GitHub Actions and missing obvious automated tests.

## Privacy

The scanner uses the Python standard library and contains no network calls.

## Boundary

This is a heuristic release preflight, not a penetration test, security audit, compliance check, or production certification. False positives and false negatives are possible. Review findings in context and independently verify important fixes.
