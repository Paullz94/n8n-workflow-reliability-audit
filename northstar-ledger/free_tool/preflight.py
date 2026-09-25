#!/usr/bin/env python3
"""Northstar Preflight Lite: local deterministic checks for AI-built web apps."""
from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path

VERSION = "0.1.0"
IGNORE = {".git", "node_modules", "vendor", "dist", "build", ".next", ".venv", "venv", "__pycache__"}
TEXT = {".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".yml", ".yaml", ".toml", ".sql", ".md", ".txt", ".env", ".rules"}
ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}

@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    path: str
    line: int
    message: str
    evidence: str = ""

def _redact(value: str) -> str:
    value = value.strip()
    return "[redacted]" if len(value) < 12 else value[:6] + "…" + value[-4:]

def _files(root: Path):
    for base, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORE and (not d.startswith(".") or d == ".github")]
        for name in names:
            p = Path(base) / name
            if p.is_symlink():
                continue
            try:
                if p.stat().st_size > 1_000_000:
                    continue
            except OSError:
                continue
            if name.startswith(".env") or p.suffix.lower() in TEXT or name in {"package.json", "Dockerfile"}:
                yield p

def _read(path: Path) -> str | None:
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    if b"\0" in raw[:4096]:
        return None
    return raw.decode("utf-8", errors="replace")

def scan(root: Path) -> tuple[list[Finding], int]:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")
    findings: list[Finding] = []
    texts: dict[Path, str] = {}

    patterns = [
        ("SECRET-OPENAI", "critical", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"), "Possible OpenAI secret committed", True),
        ("SECRET-STRIPE", "critical", re.compile(r"\bsk_(?:live|test)_[A-Za-z0-9]{16,}\b"), "Possible Stripe secret key committed", True),
        ("CLIENT-PRIVILEGED-KEY", "critical", re.compile(r"\b(?:NEXT_PUBLIC|VITE|REACT_APP)_[A-Z0-9_]*(?:SERVICE_ROLE|STRIPE_SECRET|PRIVATE_KEY|ADMIN_KEY)[A-Z0-9_]*\b"), "Privileged key appears exposed to client code", False),
        ("DEBUG-ENABLED", "high", re.compile(r"\b(?:DEBUG\s*=\s*True|debug\s*=\s*true|app\.run\([^\n]*debug\s*=\s*True)", re.I), "Debug mode appears enabled", False),
        ("CORS-WILDCARD", "medium", re.compile(r"(?:Access-Control-Allow-Origin[^\n]{0,30}\*|allow_origins\s*=\s*\[?['\"]\*['\"]|origin\s*:\s*['\"]\*['\"])", re.I), "Wildcard CORS signal detected", False),
        ("FIREBASE-OPEN", "critical", re.compile(r"allow\s+(?:read|write|read,\s*write)\s*:\s*if\s+true", re.I), "Firebase rule appears broadly open", False),
    ]

    for path in _files(root):
        text = _read(path)
        if text is None:
            continue
        texts[path] = text
        rel = path.relative_to(root).as_posix()
        for rule, sev, rx, msg, redact in patterns:
            for m in rx.finditer(text):
                ev = _redact(m.group(0)) if redact else m.group(0)[:100]
                findings.append(Finding(rule, sev, rel, text.count("\n", 0, m.start()) + 1, msg, ev))

    envs = [p for p in texts if p.name.startswith(".env") and p.name not in {".env.example", ".env.sample", ".env.template"}]
    for p in envs:
        findings.append(Finding("ENV-PRESENT", "high", p.relative_to(root).as_posix(), 1, "Environment file is present in the scanned tree"))

    joined = "\n".join(texts.values()).lower()
    if "stripe" in joined and not any(x in joined for x in ("construct_event", "constructevent", "stripe-signature", "webhooks.construct")):
        findings.append(Finding("STRIPE-WEBHOOK-VERIFY", "high", ".", 1, "Stripe usage found without obvious webhook signature verification"))

    names = {p.relative_to(root).as_posix() for p in texts}
    if not any(n.startswith(".github/workflows/") for n in names):
        findings.append(Finding("CI-MISSING", "low", ".", 1, "No GitHub Actions workflow detected"))
    if not any("test" in Path(n).name.lower() or "/tests/" in n.lower() for n in names):
        findings.append(Finding("TESTS-MISSING", "low", ".", 1, "No obvious automated tests detected"))

    unique = {(f.rule, f.path, f.line, f.message): f for f in findings}
    ordered = sorted(unique.values(), key=lambda f: (ORDER[f.severity], f.path, f.line, f.rule))
    return ordered, len(texts)

def report(findings: list[Finding], count: int) -> str:
    totals = {k: 0 for k in ORDER}
    for f in findings:
        totals[f.severity] += 1
    out = [
        "# Northstar Preflight Lite Report", "",
        f"Version: {VERSION}", f"Files scanned: {count}",
        f"Findings: {len(findings)} (critical {totals['critical']}, high {totals['high']}, medium {totals['medium']}, low {totals['low']})", "",
        "Heuristic preflight only; not a penetration test, security audit, compliance check, or production certification.", ""
    ]
    for f in findings:
        out += [f"## [{f.severity.upper()}] {f.message}", f"- Rule: {f.rule}", f"- Location: {f.path}:{f.line}"]
        if f.evidence:
            out.append(f"- Evidence: {f.evidence}")
        out.append("")
    return "\n".join(out) + "\n"

def main() -> int:
    p = argparse.ArgumentParser(description="Local deterministic preflight for AI-built web app repositories")
    p.add_argument("path", nargs="?", default=".")
    p.add_argument("--json")
    p.add_argument("--markdown")
    p.add_argument("--fail-on", choices=["critical", "high", "medium", "low", "none"], default="critical")
    args = p.parse_args()
    findings, count = scan(Path(args.path))
    text = report(findings, count)
    print(text, end="")
    if args.markdown:
        Path(args.markdown).write_text(text, encoding="utf-8")
    if args.json:
        Path(args.json).write_text(json.dumps({"version": VERSION, "files_scanned": count, "findings": [asdict(f) for f in findings]}, indent=2), encoding="utf-8")
    if args.fail_on != "none" and any(ORDER[f.severity] <= ORDER[args.fail_on] for f in findings):
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
