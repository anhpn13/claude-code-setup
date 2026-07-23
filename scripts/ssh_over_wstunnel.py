#!/usr/bin/env python3
"""
ssh_over_wstunnel.py — SSH vào server demo `ai-course-demo` qua `wstunnel`.

Chạy qua `mise run ssh-logs -- <lệnh>` (xem mise.toml).

Khác với `ssh`/ProxyCommand thuần:
  - gọi `wstunnel client` qua subprocess (stdin/stdout pipe cho SSH);
  - retry tối đa 5 lần khi thấy `404` từ server (ALPN ngẫu nhiên);
  - tự feed password trống qua SSH_ASKPASS — không prompt tay.

Lần đầu có thể mất ~15s nếu rơi vào 4 lần ALPN-404 liên tiếp.
"""

from __future__ import annotations

import argparse
import io
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path


# Windows console mặc định cp1252 — in ký tự tiếng Việt có dấu sẽ
# UnicodeEncodeError. Ép UTF-8 cho cả 2 stream.
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


SCRIPT_DIR = Path(__file__).resolve().parent


def env_default(name: str, default: str) -> str:
    return os.environ.get(name, default)


def env_or_die(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        sys.stderr.write(
            f"LỖI: biến môi trường {name} chưa được set.\n"
            f"→ Đặt vào .env hoặc truyền --student-id.\n"
        )
        sys.exit(2)
    return value


def which_or_die(binary: str) -> str:
    path = shutil.which(binary)
    if not path:
        sys.stderr.write(
            f"LỖI: không tìm thấy `{binary}` trên PATH.\n"
            f"→ Chạy `mise install` (mise.toml có khai báo wstunnel) "
            f"và cài OpenSSH client cho hệ điều hành của bạn.\n"
        )
        sys.exit(3)
    return path


def run_once(askpass_path: str, wss_url: str, ssh_host: str,
             ssh_port: str, ssh_user: str, remote_cmd: list[str]) -> int:
    """Một lần thử: spawn ssh, return exit code của nó."""
    proxy = (
        f"wstunnel client --log-lvl=off -L stdio://%h:%p {wss_url}"
    )
    ssh_cmd = [
        "ssh",
        "-tt",
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "LogLevel=ERROR",
        "-o", f"ProxyCommand={proxy}",
        "-p", ssh_port,
        f"{ssh_user}@{ssh_host}",
        "--",
        *remote_cmd,
    ]
    env = os.environ.copy()
    env["SSH_ASKPASS"] = askpass_path
    env["SSH_ASKPASS_REQUIRE"] = "force"
    # DISPLAY cần cho SSH_ASKPASS_REQUIRE=force trên OpenSSH cũ (Linux).
    # Bỏ qua Windows (không có X11) — không hại gì nếu set dummy.
    if sys.platform != "win32":
        env.setdefault("DISPLAY", ":0")

    return subprocess.call(ssh_cmd, env=env)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--student-id", help="Ghi đè $PETSTORE_STUDENT_ID")
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Lệnh chạy trên server (ví dụ: ls /data/petstore-logs). "
             "Dùng '--' trước nếu muốn bắt đầu bằng flag (vd `-- ls`).",
    )
    args = parser.parse_args()

    # Validate trước khi vẽ token URL/wstunnel (fail-fast).
    which_or_die("wstunnel")
    which_or_die("ssh")

    # student_id chỉ dùng để tường thuật log ở doc; không bắt buộc cho SSH.
    # Vẫn env_or_die để bắt user khai báo id (best practice cho multi-tenant).
    student_id = (args.student_id or env_or_die("PETSTORE_STUDENT_ID")).strip()
    del student_id  # không dùng trong SSH flow; giữ khai báo để nhắc doc.

    wss_url = env_default(
        "PETSTORE_WSS_URL",
        "wss://passthrough-ai-course-demo-ssh.sandbox.vnpt-technology.vn:9443",
    )
    ssh_host = env_default("PETSTORE_SSH_HOST", "localhost")
    ssh_port = env_default("PETSTORE_SSH_PORT", "2222")
    ssh_user = env_default("PETSTORE_SSH_USER", "student")

    # argparse.REMAINDER giữ nguyên '--' nếu user gõ `mise run ssh-logs -- -- ls`.
    # Cắt đi leading '--' nếu có; fallback nếu user không truyền lệnh.
    remote_cmd = list(args.command)
    if remote_cmd and remote_cmd[0] == "--":
        remote_cmd = remote_cmd[1:]
    if not remote_cmd:
        remote_cmd = ["echo", "ok"]

    askpass_path = str(SCRIPT_DIR / "askpass_empty.py")

    # Retry loop: bug VM public-proxy 10.15.94.54 (L4 SNI-inspect) thỉnh
    # thoảng RST trên đường internet thật. 5 lần đủ cho >99% trường hợp.
    delays = [0, 0.5, 1, 2, 4]  # 0 = lần đầu; tổng tối đa ~7.5s thêm
    for attempt, delay in enumerate(delays, start=1):
        if delay:
            sys.stderr.write(
                f"[ssh-logs] lần thử {attempt}/{len(delays)} "
                f"(đợi {delay}s cho retry)…\n"
            )
            time.sleep(delay)
        rc = run_once(askpass_path, wss_url, ssh_host, ssh_port, ssh_user, remote_cmd)
        if rc == 0:
            return 0
        # SSH trả 255 cho mọi network/transport lỗi. Nếu vào được shell
        # rồi lệnh thoát mã khác 0 → trả code đó, không retry.
        if rc not in (255,):
            return rc

    sys.stderr.write(
        f"[ssh-logs] đã retry {len(delays)} lần mà ssh vẫn thoát {rc}.\n"
        "→ Có thể server demo tạm thời không khả dụng, "
        "kiểm tra mạng hoặc thử lại sau vài phút.\n"
    )
    return rc if rc else 1


if __name__ == "__main__":
    # Ctrl+C gọn gàng, không để wstunnel treo.
    signal.signal(signal.SIGINT, lambda *_: sys.exit(130))
    raise SystemExit(main())
