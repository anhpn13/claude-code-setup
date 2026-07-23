# Claude Code — Setup Mẫu Cho Khoá Học

Repo này là **môi trường chuẩn bị sẵn** để học và làm việc với Claude Code — chạy được trên **Windows, macOS và Linux**: mọi tool cần thiết (mise, Python, Node, Docling, Firecrawl MCP, **gitleaks**) đều khai báo trong `mise.toml` — chỉ cần `mise install` là có đủ. Hook bảo mật cũng viết bằng Python (cross-platform) thay vì shell script riêng cho từng OS. Bên trong còn có sẵn:

- **Skill** `read-doc` đọc PDF/Word/Excel bằng Docling (chạy local, có cache).
- **Agent** `researcher` chuyên research chuyên sâu bằng Firecrawl.
- **Hook** `pre-push-credentials-check` chặn `git push` nếu diff có lộ secret — **2 lớp song song**: `gitleaks` (pattern-based, deterministic, chạy qua script Python cross-platform) + agent subagent (Haiku, context-aware, đọc diff bằng Bash). Xem [`docs/2-core/05-HOOKS.md`](docs/2-core/05-HOOKS.md) § 5.
- Tài liệu học tập theo lộ trình: **init → customize → core**.

---

## 🛠️ Chuẩn Bị Môi Trường (Bắt Buộc Trước Khi Bắt Đầu)

> Yêu cầu tối thiểu: **Windows 10/11**, **macOS 13+**, hoặc **Linux** (Ubuntu 20.04+/Debian 10+/Alpine 3.19+), kết nối Internet. Terminal dùng được: PowerShell/CMD (Windows), Terminal.app/iTerm2 (macOS), hoặc Bash/Zsh bất kỳ (Linux).

Học viên cần cài **3 thứ theo thứ tự** trước khi làm bất kỳ bài nào trong repo:

| # | Công cụ | Cần cho | Thời gian | Hướng dẫn cài |
| :---: | :--- | :--- | :---: | :--- |
| 1️⃣ | **Claude Code CLI** | Công cụ chính để chạy agent trong terminal | ~2 phút | [`docs/0-init/00-claude-code.md`](docs/0-init/00-claude-code.md) |
| 2️⃣ | **Mise** | Quản lý mọi runtime (Python, Node, gitleaks, gh, docling…) qua `mise.toml` — chỉ cần `mise install` là đủ | ~3 phút | [`docs/0-init/01-mise.md`](docs/0-init/01-mise.md) |
| 3️⃣ | **API key MiniMax** *(hoặc Anthropic)* | Để Claude Code gọi model — set qua env trong `.claude/settings.json` | ~2 phút | [`docs/0-init/01-claude-code-minimax.md`](docs/0-init/01-claude-code-minimax.md) |

**Sau khi cài xong 3 thứ trên, quay lại đây chạy tiếp 3 bước dưới.**

---

## 🚀 Bắt Đầu Nhanh (3 Bước)

> Yêu cầu: đã hoàn thành 3 mục ở [§ Chuẩn Bị Môi Trường](#️-chuẩn-bị-môi-trường-bắt-buộc-trước-khi-bắt-đầu).

**macOS / Linux (bash, zsh):**
```bash
# 1. Mở terminal tại thư mục repo này
cd claude-code-setup

# 2. Cài đặt mọi tool đã khai báo trong mise.toml
mise install

# 3. (Tuỳ chọn) cài Claude Code CLI nếu máy chưa có
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows (PowerShell):**
```powershell
# 1. Mở terminal tại thư mục repo này
cd claude-code-setup

# 2. Cài đặt mọi tool đã khai báo trong mise.toml
mise install

# 3. (Tuỳ chọn) cài Claude Code CLI nếu máy chưa có
irm https://claude.ai/install.ps1 | iex
```

Sau đó vào từng file tài liệu theo thứ tự dưới đây — mỗi file xong thì quay lại đây đánh dấu ✅.

---

## 🗺 Lộ Trình Học

Repo chia tài liệu thành 3 phần, đọc theo thứ tự:

### Phần 1 — `docs/0-init/` (cài đặt ban đầu)

| File | Nội dung | ✅ |
| :--- | :--- | :--- |
| [`00-claude-code.md`](docs/0-init/00-claude-code.md) | Cài Claude Code CLI (Windows / macOS / Linux) | ☐ |
| [`01-claude-code-minimax.md`](docs/0-init/01-claude-code-minimax.md) | Cấu hình chạy qua MiniMax provider (thay vì Anthropic trực tiếp) | ☐ |
| [`01-mise.md`](docs/0-init/01-mise.md) | Cài mise — quản lý mọi runtime cho repo | ☐ |

### Phần 2 — `docs/1-customize/` (tuỳ biến)

| File | Nội dung | ✅ |
| :--- | :--- | :--- |
| [`00-mise.md`](docs/1-customize/00-mise.md) | Hiểu sâu hơn về mise: backend, env, scoped tools | ☐ |
| [`01-mcp.md`](docs/1-customize/01-mcp.md) | MCP server (Firecrawl) — cổng kết nối AI ↔ dịch vụ ngoài | ☐ |

### Phần 3 — `docs/2-core/` (4 cơ chế lõi của Claude Code)

| File | Nội dung | ✅ |
| :--- | :--- | :--- |
| [`00-CLAUDE.md`](docs/2-core/00-CLAUDE.md) | CLAUDE.md — file quy tắc mặc định cho mọi phiên | ☐ |
| [`01-SKILL.md`](docs/2-core/01-SKILL.md) | Skill — đóng gói quy trình thành lệnh `/tên` | ☐ |
| [`02-MCP.md`](docs/2-core/02-MCP.md) | MCP server — chi tiết kỹ thuật | ☐ |
| [`03-AGENT.md`](docs/2-core/03-AGENT.md) | Subagent — chạy tác vụ tách biệt context | ☐ |
| [`04-CHROME.md`](docs/2-core/04-CHROME.md) | Chrome integration — Claude điều khiển trình duyệt thật | ☐ |
| [`05-HOOKS.md`](docs/2-core/05-HOOKS.md) | Hooks — tự động chạy shell tại các điểm mấu chốt | ☐ |

---

## 📦 Repo Có Gì?

```
claude-code-setup/
├── .claude/                    # cấu hình Claude Code cho project này
│   ├── settings.json           # khai hook (PreToolUse cho git push — agent + gitleaks)
│   ├── settings.local.json     # cá nhân (MCP enabled list, gitignored)
│   ├── agents/researcher.md    # subagent research chuyên sâu
│   ├── hooks/                  # script Python cross-platform cho command hook (pre-push-secret-scan.py)
│   └── skills/read-doc/        # skill đọc PDF/DOCX/PPTX/XLSX bằng Docling
├── docs/                       # tài liệu khoá học (xem lộ trình ở trên)
├── reference-docs/             # file mẫu để test skill read-doc
├── mise.toml                   # khai báo toàn bộ tool (Python, Node, Docling, gitleaks, gh…)
├── .gitleaks.toml              # rule secret scan (extend defaults + Firecrawl/Anthropic/DB/JWT/PEM)
├── .env.example                # template cho .env (gitignored)
├── .mcp.json                   # khai báo MCP server (Firecrawl) — key đọc từ env
└── README.md                   # file này
```

### Tool được mise quản lý (xem `mise.toml`)

| Tool | Vai trò |
| :--- | :--- |
| **Python 3.13** | Runtime cho Docling và các skill Python |
| **Node.js LTS** | Runtime cho Firecrawl MCP |
| **Firecrawl MCP** | Cổng scrape web, search, extract → dùng bởi agent `researcher` |
| **uv** | Package manager Python nhanh (dùng nội bộ bởi mise pipx backend) |
| **Docling** | Parser PDF/DOCX/PPTX/XLSX/ảnh → Markdown, chạy local |
| **gitleaks** | Secret scanner pattern-based — lớp 1 của hook `pre-push-credentials-check` |
| **GitHub CLI (`gh`)** | `gh auth login`, `gh auth setup-git` để git push không cần nhập tay |

---

## 🧪 Thử Nhanh Sau Khi Cài

Sau khi hoàn tất Phần 1 và 2, mở terminal tại repo và chạy `claude`. Trong phiên Claude Code, thử vài câu sau để xác nhận mọi thứ chạy đúng:

```text
Đọc file reference-docs/aws-overview.pdf và tóm tắt phần nói về VPC.
```
→ Test skill `read-doc` (Docling sẽ parse PDF → Markdown).

```text
Dùng agent researcher tìm hiểu về AWS Transit Gateway.
```
→ Test agent `researcher` + Firecrawl MCP.

```text
Sửa README để thêm badge ở đầu file rồi git add và commit.
```
→ Test luồng Claude đọc/sửa/commit file.

```text
git push
```
→ Test **hook `pre-push-credentials-check`** (2 lớp: gitleaks + agent). Để xác nhận cả 2 lớp hoạt động, thử commit 1 file có chứa API key rồi push:
- File có pattern rõ (vd `AKIA1234567890ABCDEF`) → gitleaks block.
- File đặt credential trong field lạ (vd `auth_string = "..."`) với host `*.internal` → agent subagent block vì hiểu context.

---

## ⚠ Lưu Ý Bảo Mật

- `.mcp.json` **tham chiếu** `FIRECRAWL_API_KEY` qua `${FIRECRAWL_API_KEY}` — không hardcode giá trị thật trong file. Giá trị thật đặt trong `.env` (gitignored) và `mise` tự load qua `_.file = ".env"` trong `mise.toml`.
- Nếu muốn rotate key, đổi giá trị trong `.env`, không sửa `.mcp.json`.
- `.env.example` đi kèm liệt kê các biến cần khai báo — copy sang `.env` rồi fill giá trị.
- Hook `pre-push-credentials-check` sẽ **chặn push** cho đến khi diff sạch (cả 2 lớp đều pass). Đây là cố ý.

---

## 📚 Tài Liệu Tham Khảo Chính Thức

| Tài nguyên | URL |
| :--- | :--- |
| Claude Code Docs | https://code.claude.com/docs/ |
| Claude Code trên GitHub | https://github.com/anthropics/claude-code |
| mise — quản lý tool/runtime | https://mise.jdx.dev/ |
| Docling — parser tài liệu | https://github.com/docling-project/docling |
| Firecrawl MCP | https://github.com/firecrawl/firecrawl-mcp-server |
| gitleaks — secret scanner | https://github.com/gitleaks/gitleaks |