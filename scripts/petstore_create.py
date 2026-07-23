#!/usr/bin/env python3
"""
petstore_create.py — POST một Pet lên server demo `ai-course-demo`.

Chạy qua `mise run petstore-create` (xem mise.toml). Không phụ thuộc
hệ thống: chỉ dùng Python stdlib + biến môi trường do mise load.

Khác với `curl`:
  - tự build body JSON (id/name/photoUrls/tags/status);
  - tắt SSL verify vì demo dùng cert tự ký;
  - retry 5 lần exponential backoff (0.5→1→2→4→8s) trên URLError / HTTP 5xx.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import random
import ssl
import sys
import time
import urllib.error
import urllib.request
import uuid


# Cờ Windows default dùng cp1252 cho console — không in được ký tự
# tiếng Việt có dấu. Ép UTF-8 ở cả stdout + stderr để em dùng thoải mái.
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


def env_or_die(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        sys.stderr.write(
            f"LỖI: biến môi trường {name} chưa được set.\n"
            f"→ Đặt vào .env (mise tự load qua `_.file`) hoặc truyền "
            f"--student-id trên dòng lệnh.\n"
        )
        sys.exit(2)
    return value


def build_pet(student_id: str, name: str | None, tag: str | None) -> dict:
    """Body theo schema Swagger Petstore — xem
    https://petstore3.swagger.io/ để tham chiếu."""
    return {
        "id": random.randint(10**9, 10**10 - 1),
        "name": name or f"{student_id}-fluffy-{uuid.uuid4().hex[:6]}",
        "photoUrls": ["https://example.com/pet.jpg"],
        "tags": [{"name": tag or student_id}],
        "status": "available",
    }


def http_post_json(url: str, body: dict, headers: dict) -> tuple[int, str]:
    """POST JSON, trả về (status, body)."""
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={**headers, "Content-Type": "application/json"},
    )
    # Demo server dùng cert tự ký → tắt verify. Không bao giờ làm vậy
    # ngoài server demo.
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:  # 4xx/5xx có body
        return exc.code, exc.read().decode("utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--student-id", help="Ghi đè $PETSTORE_STUDENT_ID")
    parser.add_argument("--name", help="Tên pet (mặc định: <student>-fluffy-<random>)")
    parser.add_argument("--tag", help="Tag pet (mặc định: <student>)")
    args = parser.parse_args()

    student_id = (args.student_id or env_or_die("PETSTORE_STUDENT_ID")).strip()
    base_url = os.environ.get(
        "PETSTORE_BASE_URL",
        "https://petstore-ai-course-demo.sandbox.vnpt-technology.vn:9443/api/v3",
    ).rstrip("/")

    pet = build_pet(student_id, args.name, args.tag)
    headers = {
        "X-Student-Id": student_id,
        "User-Agent": "claude-code-setup/petstore-create",
        "Accept": "application/json",
    }

    delays = [0.5, 1, 2, 4, 8]  # tổng cộng ~15.5s nếu retry hết
    last_status = 0
    last_body = ""
    for attempt, delay in enumerate([0] + delays, start=1):
        if delay:
            time.sleep(delay)
        last_status, last_body = http_post_json(
            f"{base_url}/pet", pet, headers
        )
        if 200 <= last_status < 300:
            print(f"OK  ({last_status}) sau {attempt} lần thử")
            try:
                print(json.dumps(json.loads(last_body), indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                print(last_body)
            return 0
        if last_status < 500 and last_status != 408 and last_status != 429:
            # 4xx (trừ 408/429) là lỗi logic, không retry
            break

    sys.stderr.write(
        f"FAIL: server trả {last_status} sau khi retry hết.\n"
        f"Body: {last_body[:500]}\n"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
