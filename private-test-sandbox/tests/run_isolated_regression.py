#!/usr/bin/env python3
"""One isolated handoff. No browser. Does not listen on 0.0.0.0.

Passing this command does not approve hosted access. The hosted candidate
stays FAIL until a real provider, TLS name, device check, and off-service
restore are signed by a separate reviewer.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    env = os.environ.copy()
    for key in (
        "SANDBOX_INGRESS",
        "SANDBOX_PUBLIC_ORIGIN",
        "SANDBOX_PROXY_SHARED_SECRET",
        "SANDBOX_HOSTED",
        "SANDBOX_BIND",
        "SANDBOX_TOKEN",
        "SANDBOX_PORT",
        "PORT",
        "CLOUD_DEV_CAPTURE",
    ):
        env.pop(key, None)
    commands = [
        [
            sys.executable,
            str(ROOT / "tests" / "shared_e2e_scenario.py"),
            "--execution-environment",
            "cloud_vm_loopback",
        ],
        [sys.executable, str(ROOT / "tests" / "test_guest_isolation.py")],
        [sys.executable, str(ROOT / "tests" / "test_trusted_proxy.py")],
    ]
    for command in commands:
        print("RUN " + Path(command[1]).name, flush=True)
        result = subprocess.run(command, cwd=str(ROOT), env=env)
        if result.returncode != 0:
            print("FAIL " + Path(command[1]).name)
            return result.returncode
    print("ISOLATED_REGRESSION_PASS")
    print("hosted_candidate=FAIL")
    print("independent.review=PENDING")
    print("parent.local_run=NOT_RUN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
