# 🪝 Hooks — Chạy Shell Tự Động Tại Các Điểm Mấu Chốt Của Phiên Claude

Tài liệu này trình bày **Hooks**: cơ chế để chạy lệnh shell (hoặc model LLM, hoặc agent) tự động tại các điểm trong vòng đời phiên Claude Code — trước/sau tool call, khi nhận prompt, khi session kết thúc... Có thể dùng để format code tự động, gửi notification, **chặn push khi lộ credential**, audit, v.v. Tài liệu chính thức: [code.claude.com/docs/en/hooks-guide](https://code.claude.com/docs/en/hooks-guide) và [Hooks reference](https://code.claude.com/docs/en/hooks).

> Repo này đã cài sẵn hook `pre-push-credentials-check` (xem [§ 5](#5-ví-dụ-trong-repo-này--hook-chặn-push-khi-lộ-credential)) — bạn có thể thử bằng cách commit một thay đổi có chứa API key rồi gõ `git push` — Claude sẽ từ chối thực thi.

---

## 1. Hook Là Gì?

Hook là **lệnh shell** (hoặc `prompt` LLM, hoặc `agent` subagent) mà Claude Code chạy **tại các điểm cố định trong vòng đời** — không phải vì LLM *muốn* chạy, mà vì *engine* quyết định chạy. Đây là cách bạn áp đặt **quy tắc deterministic** lên một hệ thống vốn probabilistic.

**Khi nào cần hook** (thay vì chỉ viết CLAUDE.md / Skill):
- Quy tắc **phải** được áp dụng, không phải "nên" — Claude có thể quên rule trong CLAUDE.md khi context dài.
- Cần **chặn hành động** (block tool call) chứ không chỉ cảnh báo.
- Cần **bơm context động** (vd trạng thái git, danh sách test fail) trước khi Claude xử lý.

**Khi KHÔNG cần hook**:
- Hướng dẫn kiểu "nhớ làm X" → CLAUDE.md đủ.
- Quy trình nhiều bước cần LLM suy luận → Skill đỡ tốn hơn.

---

## 2. Cấu Hình

Hook được khai trong `settings.json` ở 1 trong 4 scope:

| Vị trí | Phạm vi | Chia sẻ |
| :--- | :--- | :--- |
| `~/.claude/settings.json` | Tất cả project của bạn | Chỉ máy bạn |
| `.claude/settings.json` | 1 project | Qua git |
| `.claude/settings.local.json` | 1 project, cá nhân | Gitignored |
| Managed policy | Toàn tổ chức | Admin quản lý |

Cấu trúc khối `hooks`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write" }
        ]
      }
    ]
  }
}
```

- **Event name** (`PreToolUse`, `PostToolUse`, ...) — top-level key.
- **Matcher** — lọc theo tool name / nguồn sự kiện; rỗng = match tất cả.
- **`hooks` array** — danh sách hook con, chạy song song, kết quả gộp lại (lấy quyết định hạn chế nhất).

> `matcher` v2.1.191+ chấp nhận `,` thay cho `|` làm dấu phân cách (`"Edit,Write"` tương đương `"Edit|Write"`).

### Đặt matcher càng hẹp càng tốt

`matcher: ""` = match tất cả — chỉ dùng khi thật sự cần. Matcher rộng dễ chặn nhầm hành động vô hại.

---

## 3. Các Event Hay Dùng

| Event | Khi nào chạy | Có thể chặn? |
| :--- | :--- | :--- |
| `SessionStart` | Phiên bắt đầu / resume / compact | ❌ (chỉ bơm context) |
| `UserPromptSubmit` | Trước khi Claude xử lý prompt | ✅ qua `permissionDecision` |
| `PreToolUse` | **Trước khi tool chạy** | ✅ qua `permissionDecision: deny` |
| `PostToolUse` | Sau khi tool chạy thành công | ❌ (đã chạy rồi) |
| `PostToolUseFailure` | Tool fail | ❌ |
| `PermissionRequest` | Khi hộp thoại permission hiện | ✅ qua `behavior: allow` (không được deny để đè deny rules) |
| `Notification` | Permission prompt / idle / auth_success... | ❌ |
| `Stop` | Claude xong response | ✅ qua `decision: block` |
| `StopFailure` | Lỗi API | ❌ |
| `SessionEnd` | Phiên kết thúc | ❌ |
| `PreCompact` / `PostCompact` | Trước/sau nén context | ❌ |
| `ConfigChange` | Settings/skills file đổi | ✅ |
| `CwdChanged` / `FileChanged` | `cd` / file watch thay đổi | ❌ (chỉ bơm context) |

Đầy đủ: xem [Hooks reference](https://code.claude.com/docs/en/hooks#hook-lifecycle).

---

## 4. 4 Loại Hook (`type`)

| `type` | Cơ chế | Khi nào dùng |
| :--- | :--- | :--- |
| `"command"` | Shell command. Đọc JSON trên stdin, exit code + stdout/stderr quyết định | Rule deterministic, nhanh, free |
| `"http"` | POST JSON tới URL, response body quyết định | Gọi dịch vụ bên ngoài (audit, notification) |
| `"prompt"` | 1-turn LLM (Haiku mặc định), trả `{"ok": bool, "reason": "..."}` | Cần suy luận nhẹ, rule mơ hồ — **không có tool access, không thấy file/diff** |
| `"agent"` | Subagent đa-turn, có quyền chạy tool (`Bash`/`Read`/`Grep`/`Glob`) | Cần đọc file, search code, verify trạng thái |

> `agent` hook còn **experimental** — docs chính thức khuyến nghị production dùng `command` hoặc `prompt`.

**Điểm khác biệt quan trọng giữa `prompt` và `agent`**:
- `prompt` chỉ thấy `$ARGUMENTS` (event JSON: tool name, tool input, cwd, ...) — không có tool, không có file, không có diff.
- `agent` được spawn thành subagent riêng, có quyền `Bash` / `Read` / `Grep` / `Glob`. Có thể tự fetch diff rồi mới quyết định.

Nếu cần kiểm tra nội dung file hoặc git diff, **phải dùng `agent`** — `prompt` không có khả năng đó.

---

## 5. Ví Dụ Trong Repo Này — Hook Chặn Push Khi Lộ Credential

> Đây là hook **thực tế đang chạy** trong `.claude/settings.json` của repo này. Thử bằng cách commit một thay đổi có chứa credential rồi gõ `git push` — Claude sẽ từ chối thực thi.

### 5.1. Bài toán và kiến trúc 2 lớp

Trước mỗi `git push`, cần đảm bảo không có secret lọt vào diff. Vấn đề: regex tự viết không đủ (key tự đặt, base64 dài, biến môi trường inject động). Repo này dùng **2 lớp song song**, mỗi lớp bắt một loại rủi ro khác nhau:

| Lớp | Loại hook | Vai trò | Catch được gì? |
| :--- | :--- | :--- | :--- |
| **1. Scanner pattern** | `command` (Python + gitleaks — chạy được trên Windows/macOS/Linux) | Fast-fail, deterministic, chạy cả khi gọi `git push` ngoài Claude Code | AWS key (`AKIA…`), GitHub PAT (`ghp_…`), Stripe, OpenAI, DB connection string có password, generic password=…, PEM key, JWT, và mọi rule có sẵn trong `.gitleaks.toml` |
| **2. Reviewer context** | `agent` (Haiku subagent, có Bash tool) | Đọc diff thật bằng `git log -p @{u}..HEAD`, hiểu ngữ nghĩa (test fixture vs secret thật, nội dung thay đổi, push intent) | Secret đặt trong field không chuẩn (vd `auth_string` thay vì `password`); host nội bộ (`*.internal`, `10.0.0.0/8`); credential trong file `config/prod*`; push force sang nhánh shared; thiếu cập nhật docs khi API đổi |

Cả 2 chạy **song song** trong cùng 1 PreToolUse event. Quyết định hạn chế nhất thắng: chỉ cần 1 trong 2 block là push bị huỷ.

### 5.2. Cấu hình thực tế trong `.claude/settings.json`

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "agent",
            "prompt": "You are the last-line reviewer before a `git push` to a (potentially public) GitHub repo. The proposed Bash command: $ARGUMENTS\n\nA separate `gitleaks` scan already passed for pattern-based secrets. Your job is the *contextual* review gitleaks can't do.\n\n# Step 1 — Inspect the diff\nUse the Bash tool to fetch the actual diff that would be pushed:\n  - If `git rev-parse --verify '@{u}'` succeeds: `git log -p @{u}..HEAD`\n  - Otherwise (initial push): `git diff $(git hash-object -t tree /dev/null) HEAD`\n\n# Step 2 — Review for these categories\nA. Security beyond patterns: risky ops (eval, exec of user input, pickle), disabled safety (verify_ssl=False, JWT verify_signature:false), crypto mistakes, internal hosts (10/8, 192.168/16, *.internal), weakened auth.\nB. Documentation drift: code changed but no docs/README touched.\nC. Sensitive files: real env files (*.env, NOT .env.example), *.pem/*.key, service-account*.json, *.sqlite/*.db, dump.sql, prod-looking config with hardcoded credentials.\nD. Risky push intent: --force to main/master/release/prod, --no-verify, push to non-origin remote, --mirror, filter-branch/filter-repo.\n\n# Step 3 — Decision\nTest fixtures pass: AKIAIOSFODNN7EXAMPLE, sk-test-xxxx, fc-00000000000000000000000000000000, ghp_0000000000000000000000000000000000.\n\nReturn {\"ok\":false,\"reason\":\"<category>: <file>:<what>\"} to block, otherwise {\"ok\":true}.\nDo not block on minor style issues.",
            "model": "haiku",
            "timeout": 60
          },
          {
            "type": "command",
            "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/pre-push-secret-scan.py\""
          }
        ]
      }
    ]
  }
}
```

**Giải thích cấu trúc**:
- `matcher: "Bash"` — PreToolUse hook kích hoạt cho **mọi** Bash tool call. Agent subagent sẽ tự quyết định command này có phải `git push` hay không dựa trên `$ARGUMENTS`.
- 2 hook con chạy **song song** — Claude không có cú pháp "chỉ chạy hook 2 khi hook 1 fail". Cả 2 luôn chạy.
- Agent hook dùng `model: "haiku"` — nhanh nhất, rẻ nhất trong các alias.
- Command hook gọi script Python `.claude/hooks/pre-push-secret-scan.py` qua biến `$CLAUDE_PROJECT_DIR` (đường dẫn tuyệt đối, không phụ thuộc cwd). Script viết bằng Python (không phải shell script/PowerShell) chính vì lý do cross-platform: `python` đã là dependency bắt buộc của repo (khai trong `mise.toml`, dùng chung với skill `read-doc`), nên hook chạy giống hệt nhau trên Windows, macOS và Linux mà không cần script riêng cho từng OS.

### 5.3. Script Python (lớp 1)

`.claude/hooks/pre-push-secret-scan.py`:

```python
# Đọc payload PreToolUse từ stdin (Claude Code pipe JSON vào đây)
payload = json.load(sys.stdin)
command = payload.get("tool_input", {}).get("command", "")

# Không phải git push → pass-through (exit 0)
if not re.search(r"git\s+push", command):
    sys.exit(0)

# Setup PATH để gitleaks do mise quản lý có thể resolve được.
# `mise bin-paths` trả về nhiều đường dẫn phân cách bằng space; os.pathsep
# tự chọn đúng ký tự nối PATH cho từng OS (";" trên Windows, ":" trên Unix).
bin_paths = subprocess.run(["mise", "bin-paths"], capture_output=True, text=True).stdout.split()
env["PATH"] = os.pathsep.join(bin_paths) + os.pathsep + env.get("PATH", "")

# Tính range sẽ push:
#   - Có upstream (@{u} tồn tại) → scan các commit kể từ lần push gần nhất
#   - Initial push (không upstream) → scan toàn bộ tree
has_upstream = subprocess.run(["git", "rev-parse", "--verify", "@{u}"], ...).returncode == 0
log_range = "@{u}..HEAD" if has_upstream else "--all"

# Chạy gitleaks. --exit-code 2 → nếu có leak, exit code 2 (block).
# --redact ẩn giá trị thật trong output. --no-banner bỏ header info.
proc = subprocess.run(["gitleaks", "git", ".", "--log-opts", log_range,
                        "--config", ".gitleaks.toml", "--redact", "--no-banner",
                        "--exit-code", "2"], env=env)
sys.exit(proc.returncode)
```

Xem toàn bộ script tại [`.claude/hooks/pre-push-secret-scan.py`](../../.claude/hooks/pre-push-secret-scan.py).

### 5.4. Custom rules trong `.gitleaks.toml`

Repo mở rộng rule set mặc định của gitleaks (~150 rule cho AWS/GCP/GitHub/Stripe/OpenAI/...) với các rule cho dịch vụ/thực thể riêng:

```toml
title = "claude-code-setup gitleaks config"

[extend]
useDefault = true  # dùng rule set mặc định, không phải tự viết lại từ đầu

# Firecrawl API key — không có sẵn trong default
[[rules]]
id = "firecrawl-api-key"
description = "Firecrawl API Key"
regex = '''\bfc-[a-f0-9]{32}\b'''

# Anthropic-compatible router token (sk-..., sk-cp-...)
[[rules]]
id = "anthropic-compatible-token"
description = "Anthropic-compatible provider token"
regex = '''\bsk-(?:cp-)?[A-Za-z0-9_-]{20,}\b'''

# Database connection string có password nhúng
[[rules]]
id = "db-connection-string-with-password"
description = "Database connection string with embedded password"
regex = '''\b(?:postgres(?:ql)?|mysql|mariadb|mongodb(?:\+srv)?|redis|amqp|amqps):\/\/[^\s:@\/]+:([^@\s\/]+)@[^\s\/]+'''

# Generic password assignment (rộng hơn default)
[[rules]]
id = "generic-password-assignment"
description = "Generic password / secret assignment"
regex = '''(?i)\b(?:[a-z_][a-z0-9_]*?)?(?:password|passwd|pwd|secret|token|apikey|api[_-]?key|access[_-]?key|private[_-]?key|client[_-]?secret|auth(?:_token)?)\s*[:=]\s*["']([^"'\s]{8,})["']'''
entropy = 2.5

# PEM private key block — bất kể extension nào
[[rules]]
id = "pem-private-key"
description = "PEM private key block"
regex = '''-----BEGIN (?:RSA |DSA |EC |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY-----'''

# JWT (header.payload.signature dạng eyJ...eyJ...)
[[rules]]
id = "jwt-token"
description = "JSON Web Token (JWT)"
regex = '''\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b'''

# Allowlist: prompt hook trong settings.json có ví dụ fixture (fc-0000…, AKIAIOSFODNN7EXAMPLE)
# nếu không allowlist thì tự nó sẽ match rule của chính nó → false positive
[allowlist]
paths = [
  '''\.claude/settings\.json$''',
  '''\.claude/hooks/.*\.py$'''
]
```

### 5.5. Cơ chế deny (fail-closed)

Cả 2 lớp đều fail-closed:
- **gitleaks**: không match → exit 0; có match → exit 2 + stderr (chi tiết), Claude Code huỷ tool call, đẩy stderr cho Claude thấy để tự điều chỉnh.
- **agent**: trả `{"ok":false,"reason":"..."}` → Claude Code đọc JSON, huỷ tool call, hiển thị `reason` cho Claude trong transcript.

### 5.6. Vì sao dùng `agent` thay vì `prompt`?

`prompt` hook **chỉ thấy `$ARGUMENTS`** (event JSON: tool name, tool input, cwd, session id, ...) — không có tool access, không đọc được file, không xem được `git diff`. Trong lần đầu triển khai repo này, prompt hook cứ block vì "không thấy diff được show" — đó là vì nó **không có khả năng** tự fetch diff.

`agent` hook khắc phục bằng cách spawn **subagent** có quyền `Bash` / `Read` / `Grep` / `Glob`. Subagent sẽ tự chạy `git log -p @{u}..HEAD` để lấy diff, sau đó mới quyết định. Đổi từ `prompt` sang `agent` là bước quan trọng nhất để review pre-push thực sự hoạt động.

### 5.7. Test thực tế — 2 scenario

Repo đã được verify với 2 fixture:

**Scenario A — pattern rõ ràng (gitleaks block, agent pass):**
```
File: .test-secret-fixture.txt
Nội dung: aws_access_key_id = "AKIA1234567890ABCDEF"
```
- **gitleaks**: match rule AWS mặc định → exit 2 → block
- **agent**: đọc diff, thấy tên file `.test-secret-fixture.txt` + comment "Test fixture" → suy luận đây là test, không phải secret thật → pass
- **Kết quả**: push bị block (bởi gitleaks, không phải agent). Đúng kỳ vọng — dù agent pass, lớp 1 vẫn block.

**Scenario B — non-standard naming (gitleaks miss, agent block):**
```python
# config/database.py
PROD_DB = {
    "host": "prod-db.acme-internal.io",
    "auth_string": "Bk7$mPq2!vN9zX4jR8wQ",  # không có keyword "password"
    "database": "payments_prod",
}
```
- **gitleaks**: `auth_string` không match bất kỳ keyword nào trong rule → không match → pass
- **agent**: đọc diff, thấy đường dẫn `config/database.py` + host `*.acme-internal.io` + giá trị entropy cao + biến `auth_string` → suy luận đây là production DB credential → block với reason: *"Security beyond patterns: config/database.py: hardcoded production database passwords (auth_string) committed to a public-eligible repo, plus internal prod hostnames; gitleaks pattern scan missed them because the keys are non-standard 'auth_string'"*
- **Kết quả**: push bị block (bởi agent — chính xác cái mà gitleaks miss).

Hai lớp bổ sung cho nhau: gitleaks chặt, deterministic, fast. Agent hiểu context, bắt được phần còn lại.

### 5.8. Vì sao không tự viết regex?

Bạn có thể nghĩ "tôi tự viết regex AWS key được mà". Đúng, nhưng:

| Regex tự viết | Scanner chuyên dụng (gitleaks) |
| :--- | :--- |
| Vài pattern phổ biến | Hàng trăm provider, cập nhật mỗi release |
| Dễ false-positive (chuỗi ngẫu nhiên dài) | Có entropy-based detection, allowlist linh hoạt |
| Không phân biệt test fixture vs secret thật | Cho phép baseline + ignore file theo context |
| Bạn phải tự bảo trì khi key format thay đổi | Maintainer theo dõi thay đổi format của từng nhà cung cấp |

**Nguyên tắc**: không tự viết những thứ đã có giải pháp chuẩn ngành. Dùng công cụ, viết hook **bao quanh** nó.

---

## 6. Một Số Mẫu Khác Hay Dùng

### 6.1. Auto-format sau khi sửa file (PostToolUse)

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write" }
        ]
      }
    ]
  }
}
```

### 6.2. Chặn sửa file nhạy cảm (PreToolUse, exit 2)

```bash
#!/bin/bash
# .claude/hooks/protect-files.sh
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

for pattern in ".env" "package-lock.json" ".git/"; do
  if [[ "$FILE_PATH" == *"$pattern"* ]]; then
    echo "Blocked: $FILE_PATH matches '$pattern'" >&2
    exit 2
  fi
done
```

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/protect-files.sh" }
        ]
      }
    ]
  }
}
```

### 6.3. Bơm context khi session bắt đầu (SessionStart)

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          { "type": "command", "command": "echo 'Reminder: use Bun, not npm. Run bun test before committing.'" }
        ]
      }
    ]
  }
}
```

### 6.4. Notification khi Claude chờ input

> Ví dụ dưới đây gọi API GUI native của từng OS nên **không cross-platform** — chọn đúng bản cho hệ điều hành bạn dùng (khác với hook `pre-push-credentials-check` ở § 5, vốn dùng Python để chạy giống nhau trên mọi OS).

**Windows (PowerShell):**
```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "idle_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "powershell.exe -Command \"[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms'); [System.Windows.Forms.MessageBox]::Show('Claude chờ bạn', 'Claude Code')\""
          }
        ]
      }
    ]
  }
}
```

**macOS:**
```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "idle_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude chờ bạn\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}
```

**Linux (cần `libnotify`/`notify-send`):**
```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "idle_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "notify-send 'Claude Code' 'Claude chờ bạn'"
          }
        ]
      }
    ]
  }
}
```

### 6.5. Audit log mọi Bash command (PostToolUse)

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "jq -r '.tool_input.command' >> ~/.claude/bash.log" }
        ]
      }
    ]
  }
}
```

---

## 7. Best Practice — Checklist

### ✅ Khi viết hook

- [ ] **Matcher càng hẹp càng tốt**. `matcher: ""` chỉ dùng khi thật sự cần.
- [ ] **Dùng tool chuẩn ngành** cho rule phức tạp (gitleaks, prettier, eslint, shellcheck) thay vì tự viết.
- [ ] **`if` field** (chỉ áp dụng cho tool events) để lọc theo command argument, vd `Bash(git push*)`.
- [ ] **Đường dẫn tuyệt đối** hoặc dùng biến `$CLAUDE_PROJECT_DIR` — không phụ thuộc cwd.
- [ ] **Script phải executable** (`chmod +x`). Trên Windows không cần nhưng nên có shebang `#!/usr/bin/env python3` (hoặc `bash`) để chạy được cả Git Bash lẫn shell tích hợp.
- [ ] **Không in ra stdout thừa** nếu hook dùng `type:"prompt"` hoặc return JSON — Claude Code sẽ parse và fail. In log ra stderr.
- [ ] **Wrap echo trong `~/.bashrc`** kiểm tra `$-` có `i` (interactive) — tránh hook bị nhiễm text từ shell profile.

### ✅ Khi dùng hook

- [ ] **Test với `/hooks`**: menu read-only, chỉ để xem. Sửa file settings.json trực tiếp.
- [ ] **Debug bằng `claude --debug-file /tmp/claude.log`**: thấy hook nào match, exit code, stdout/stderr.
- [ ] **Kiểm tra `matcher` case-sensitive**: `Edit` ≠ `edit`.
- [ ] **Stop hook không quá nhiều block liên tiếp**: Claude Code có **cap 8 lần** liên tiếp. Parse `stop_hook_active` từ stdin để thoát sớm nếu cần.
- [ ] **JSON hợp lệ**: trailing comma và comment là JSON không hợp lệ. Dùng `jq` validate: `cat .claude/settings.json | jq`.

### ❌ Tránh

- ❌ Hook `matcher: ""` cho `PreToolUse` — chặn nhầm nhiều thao tác vô hại.
- ❌ Auto-approve toàn bộ qua hook — `behavior: "allow"` không đè được deny rule từ settings.
- ❌ Hook phụ thuộc `jq` / `curl` mà repo chưa khai trong `mise.toml` — người khác clone về không chạy được.
- ❌ In thông tin nhạy cảm ra log/stdout (gồm cả path chứa secret).
- ❌ **Dùng `prompt` hook để review nội dung file** — nó không có tool access, không thấy diff. Dùng `agent` cho mọi thứ cần đọc/git diff/state.

---

## 8. Các Cạm Bẫy Thường Gặp

| Triệu chứng | Nguyên nhân | Cách xử lý |
| :--- | :--- | :--- |
| `/hooks` hiện 0 hook dù đã thêm vào settings.json | File watcher bỏ sót | Restart session, hoặc validate JSON |
| "PreToolUse hook error" trong transcript | Script exit non-zero ngoài dự kiến | Test thủ công: `echo '{...}' \| ./script.sh; echo $?` |
| "command not found" dù tool đã cài | PATH chưa có khi Claude Code spawn | Dùng đường dẫn tuyệt đối hoặc `$CLAUDE_PROJECT_DIR` |
| "jq: command not found" | jq chưa cài | Cài qua mise, hoặc viết hook bằng Python |
| Hook chạy nhưng JSON bị prepend text rác | `~/.bashrc` có `echo` không điều kiện | Wrap: `if [[ $- == *i* ]]; then echo ...; fi` |
| Stop hook liên tục block | Claude không "tiến triển" | Parse `stop_hook_active` từ stdin, exit 0 nếu đã loop |
| Claude "quên" hook giữa phiên dài | Context compaction | Tăng độ rõ của rule, hoặc bơm lại qua `SessionStart` matcher `compact` |
| `prompt` hook cứ block dù không có lỗi | Model không thấy được diff vì **không có tool** | Đổi sang `type: "agent"` để subagent tự `git log -p` |

---

## 9. Bảo Mật Khi Triển Khai

- **Hook chạy với quyền của bạn** — script độc hại có thể làm bất cứ gì user hiện tại làm được. Không copy hook từ nguồng không tin cậy.
- **Tổ chức có thể tắt hoàn toàn**: `"disableAllHooks": true` trong managed settings.
- **`disableSkillShellExecution`** không liên quan đến hook (chỉ liên quan đến dynamic context injection trong skill).
- **HTTP hook** có thể gửi dữ liệu tool call ra ngoài — cân nhắc policy.
- **Headers** trong HTTP hook hỗ trợ `$VAR` interpolation nhưng chỉ biến trong `allowedEnvVars` mới được thay.

---

## 🔗 Tài Liệu Tham Khảo

| Tài nguyên | URL |
| :--- | :--- |
| 🪝 **Hooks Guide (chính thức, bắt đầu ở đây)** | [code.claude.com/docs/en/hooks-guide](https://code.claude.com/docs/en/hooks-guide) |
| 📖 **Hooks Reference (schema, JSON output)** | [code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks) |
| 🛡️ **Security considerations cho hooks** | [code.claude.com/docs/en/hooks#security-considerations](https://code.claude.com/docs/en/hooks#security-considerations) |
| 🐙 **gitleaks (scanner secret dùng trong ví dụ)** | [github.com/gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) |
| 🐶 **trufflehog (scanner thay thế)** | [github.com/trufflesecurity/trufflehog](https://github.com/trufflesecurity/trufflehog) |
| 🐙 **Ví dụ bash command validator** | [github.com/anthropics/claude-code/blob/main/examples/hooks/bash_command_validator_example.py](https://github.com/anthropics/claude-code/blob/main/examples/hooks/bash_command_validator_example.py) |