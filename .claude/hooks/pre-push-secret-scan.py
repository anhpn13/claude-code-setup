#!/usr/bin/env python3
"""
Pre-push secret scanner — đọc PreToolUse payload từ stdin (JSON).
Scan secret khi (và chỉ khi) Bash command chứa "git push"; mọi lệnh
khác → exit 0 ngay, không tốn LLM token.
"""

import json
import os
import re
import shutil
import subprocess
import sys


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        # Không phải PreToolUse → skip.
        return 0

    command = payload.get("tool_input", {}).get("command", "")
    if not re.search(r"\bgit\s+push\b", command):
        return 0

    env = os.environ.copy()
    mise = shutil.which("mise")
    if mise:
        out = subprocess.run([mise, "bin-paths"], capture_output=True, text=True)
        bin_paths = out.stdout.split()
        if bin_paths:
            env["PATH"] = os.pathsep.join(bin_paths) + os.pathsep + env.get("PATH", "")

    gitleaks = shutil.which("gitleaks", path=env.get("PATH"))
    if gitleaks is None:
        print(
            "ERROR: `gitleaks` not found on PATH. Run `mise install`.",
            file=sys.stderr,
        )
        return 2

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
