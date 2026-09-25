#!/usr/bin/env python3
"""Run Northstar Make reliability validation without external dependencies."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(cmd: list[str], cwd: Path = ROOT) -> int:
    print("+", " ".join(cmd))
    completed = subprocess.run(cmd, cwd=cwd)
    return completed.returncode


def main() -> int:
    if run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]):
        return 1

    node = shutil.which("node")
    web_test = ROOT / "web" / "test-scanner-core.js"
    if node and web_test.exists():
        if run([node, "test-scanner-core.js"], ROOT / "web"):
            return 1
    else:
        print("SKIP browser scanner test: node not available")

    print("Northstar validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
