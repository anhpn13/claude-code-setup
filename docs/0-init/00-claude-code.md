# 🚀 Hướng Dẫn Cài Đặt Claude Code CLI

Tài liệu này hướng dẫn chi tiết từng bước để cài đặt công cụ **Claude Code CLI** trên **Windows, macOS và Linux** dành cho người mới bắt đầu.

---

## 1. Claude Code CLI là gì?

**Claude Code** là công cụ AI Agent dạng dòng lệnh (Command Line Interface - CLI) chính thức phát triển bởi Anthropic. Công cụ này hoạt động trực tiếp trong cửa sổ Terminal của bạn để:

- 🤖 **Tự động hóa lập trình**: Viết code mới, refactor code cũ, và sửa lỗi (debug) thông minh.
- 🔍 **Đọc & Hiểu dự án**: Phân tích toàn bộ cấu trúc file, hàm và mã nguồn trong workspace.
- 🛠️ **Chạy câu lệnh hệ thống**: Tự động thực thi lệnh build, test, hoặc git trực tiếp.

---

## 2. Yêu Cầu Tiền Đề

| Yêu cầu | Mô tả |
| :--- | :--- |
| **Hệ điều hành** | Windows 10 1809+ / Windows 11, hoặc macOS 13.0+, hoặc Ubuntu 20.04+ / Debian 10+ / Alpine 3.19+ |
| **Phần cứng** | RAM 4GB+, CPU x64 hoặc ARM64 |
| **Ứng dụng** | Windows: PowerShell hoặc CMD (có sẵn). macOS/Linux: bất kỳ terminal nào với Bash/Zsh + `curl` |
| **Mạng** | Kết nối Internet để tải script cài đặt và gọi API |

---

## 3. Các Bước Cài Đặt Chi Tiết

### macOS / Linux / WSL

#### Bước 1: Mở Terminal
- **macOS**: mở **Terminal.app** (Spotlight → gõ "Terminal") hoặc iTerm2.
- **Linux**: mở terminal mặc định của distro.
- **WSL**: mở cửa sổ WSL (không phải PowerShell/CMD).

#### Bước 2: Chạy lệnh cài đặt

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

> [!NOTE]
> **Giải thích câu lệnh:**
> - `curl -fsSL <url>`: tải script cài đặt, im lặng nếu lỗi (`-f`), không hiện progress bar (`-s`), theo redirect (`-L`).
> - `| bash`: chạy script tải về ngay bằng Bash.
> - Bản cài native tự **auto-update** ở nền — không cần chạy lại lệnh này mỗi lần muốn cập nhật.

**Cách khác (tuỳ chọn):**
- **Homebrew (macOS/Linux)**: `brew install --cask claude-code` — không tự auto-update, cần `brew upgrade claude-code` định kỳ.
- **Debian/Ubuntu qua apt, Fedora/RHEL qua dnf, Alpine qua apk**: xem chi tiết tại trang [Advanced setup](https://code.claude.com/docs/en/setup#install-with-linux-package-managers) chính thức.
- **npm**: `npm install -g @anthropic-ai/claude-code` (yêu cầu Node.js 22+; **không dùng `sudo npm install -g`**).

#### Bước 3: Alpine Linux — cài thêm dependency

Alpine không có sẵn `bash`/`curl`, cần cài trước:

```bash
apk add bash curl libgcc libstdc++ ripgrep
```

### Windows

#### Bước 1: Mở cửa sổ PowerShell
1. Nhấn phím `Windows` trên bàn phím.
2. Gõ từ khóa **PowerShell**.
3. Nhấp chọn **Windows PowerShell** (hoặc Windows Terminal).

#### Bước 2: Thực thi lệnh cài đặt tự động
Copy câu lệnh PowerShell bên dưới, dán vào cửa sổ PowerShell và nhấn **Enter**:

```powershell
irm https://claude.ai/install.ps1 | iex
```

> [!NOTE]
> **Giải thích câu lệnh đơn giản:**
> - `irm` (`Invoke-RestMethod`): Tải script cài đặt an toàn từ trang chủ Anthropic (`claude.ai`).
> - `| iex` (`Invoke-Expression`): Chạy script cài đặt tự động ngay trên máy tính của bạn.

Nếu đang ở **CMD** (không phải PowerShell), dùng lệnh:
```batch
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```
> Cách phân biệt: PowerShell hiện `PS C:\...>`, CMD chỉ hiện `C:\...>` (không có `PS`).

**Cách khác (tuỳ chọn):** `winget install Anthropic.ClaudeCode` — không tự auto-update, cần `winget upgrade Anthropic.ClaudeCode` định kỳ.

> [!TIP]
> Cài thêm [Git for Windows](https://git-scm.com/downloads/win) (tuỳ chọn) để Claude Code dùng được Bash tool qua Git Bash — nếu không có, Claude Code dùng PowerShell tool thay thế. Chạy trong **WSL** thì không cần bước này (chạy thẳng lệnh Linux ở mục trên, bên trong terminal WSL).

---

## 4. Kiểm Tra Kết Quả Cài Đặt

Sau khi lệnh chạy hoàn tất, terminal sẽ hiển thị xác nhận cài đặt thành công (ví dụ trên Windows):

![Cài đặt Claude Code thành công](img/00-claude-code-install.png)

Gõ lệnh sau ở **mọi hệ điều hành** để xác nhận:

```bash
claude --version
```

Kết quả mong đợi: in ra số phiên bản, ví dụ `2.1.211 (Claude Code)`. Để kiểm tra chi tiết hơn (cài đặt, settings, quyền):

```bash
claude doctor
```

Để xem trợ giúp và danh sách câu lệnh:
```bash
claude --help
```

---

## 5. Mẹo & Xử Lý Sự Cố Thường Gặp

> [!IMPORTANT]
> **Lỗi không nhận diện lệnh `claude` (`'claude' is not recognized...` / `command not found`):**
> Sau khi cài xong, nếu gõ `claude` mà gặp lỗi trên, nguyên nhân thường là do cửa sổ terminal cũ chưa cập nhật biến môi trường `PATH`.
> 👉 **Cách xử lý**: **ĐÓNG HẲN** cửa sổ terminal hiện tại và **MỞ LẠI** một cửa sổ mới.

> [!NOTE]
> **Alpine/musl**: nếu vẫn báo thiếu `ripgrep` sau khi cài đặt, thêm repository `community` vào `/etc/apk/repositories`, chạy `apk update` rồi cài lại, và đặt `USE_BUILTIN_RIPGREP=0` trong `env` của `settings.json`. Xem trang tham khảo chính thức bên dưới để biết chi tiết.

> Sau khi cài xong Claude Code CLI, bước tiếp theo là trỏ nó về model provider bạn muốn dùng (MiniMax, Anthropic API, Bedrock, v.v.) — xem [01-claude-code-minimax.md](./01-claude-code-minimax.md) nếu bạn dùng MiniMax của khóa học.

---

## 🔗 6. Tài Liệu Tham Khảo & Đường Dẫn Tải Về (References)

| Tài nguyên | Đường dẫn (URL) |
| :--- | :--- |
| 📖 **Trang tài liệu cài đặt chính thức (system requirements, mọi OS)** | [code.claude.com/docs/en/setup](https://code.claude.com/docs/en/setup) |
| 💻 **Script cài đặt macOS/Linux/WSL** | [claude.ai/install.sh](https://claude.ai/install.sh) |
| 💻 **Script cài đặt Windows (PowerShell)** | [claude.ai/install.ps1](https://claude.ai/install.ps1) |
| 🌐 **Trang chủ Anthropic Claude** | [claude.ai](https://claude.ai/) |
| 📚 **Anthropic Claude Code Docs** | [docs.anthropic.com](https://docs.anthropic.com/) |
