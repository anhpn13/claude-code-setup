#!/usr/bin/env python3
"""askpass_empty.py — SSH_ASKPASS helper, in ra password trống.

Được `ssh` gọi khi cần nhập password mà stdin không phải terminal.
Trả về chuỗi rỗng + thoát 0. Cross-platform.
"""

import sys


def main() -> int:
    sys.stdout.write("\n")
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
