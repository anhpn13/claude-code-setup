#!/usr/bin/env python3
"""Pre-push secret scanner hook (cross-platform: Windows/macOS/Linux).

Reads the PreToolUse payload from stdin; only acts when the Bash command is a
`git push`. Sets up mise-managed PATH so `gitleaks` resolves, then runs
`gitleaks git` over the push range. Exit 2 blocks the push (findings found),
exit 0 lets it through (clean scan or non-push command).
"""

import json
import os
import re
import shutil
import subprocess
import sys


def main() -> int:
    payload = json.load(sys.stdin)
    command = payload.get("tool_input", {}).get("command", "")
    if not re.search(r"git\s+push", command):
        return 0

    env = os.environ.copy()

    # `mise bin-paths` prints space-separated dirs on one line. Prepend each
    # to PATH so gitleaks/git installed by mise resolve without needing the
    # shell's own activation hook to have run.
    mise = shutil.which("mise")
    if mise:
        bin_paths = subprocess.run(
            [mise, "bin-paths"], capture_output=True, text=True
        ).stdout.split()
        if bin_paths:
            env["PATH"] = os.pathsep.join(bin_paths) + os.pathsep + env.get("PATH", "")

    gitleaks = shutil.which("gitleaks", path=env.get("PATH"))
    if gitleaks is None:
        print(
            "ERROR: `gitleaks` not found on PATH. Run `mise install` in the "
            "project root, then retry the push.",
            file=sys.stderr,
        )
        return 2

    # Has upstream? Scan only commits since the last push. Otherwise
    # (initial push) scan everything reachable from HEAD.
    has_upstream = (
        subprocess.run(
            ["git", "rev-parse", "--verify", "@{u}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode
        == 0
    )
    log_range = "@{u}..HEAD" if has_upstream else "--all"

    proc = subprocess.run(
        [
            gitleaks, "git", ".",
            "--log-opts", log_range,
            "--config", ".gitleaks.toml",
            "--redact",
            "--no-banner",
            "--exit-code", "2",
        ],
        env=env,
    )
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
