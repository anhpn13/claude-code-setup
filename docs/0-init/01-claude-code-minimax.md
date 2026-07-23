# ⚙️ Hướng Dẫn Cấu Hình Kết Nối MiniMax API Cho Claude Code

Tài liệu này hướng dẫn chi tiết cho **người mới bắt đầu** từng bước cấu hình **MiniMax API** cho công cụ **Claude Code CLI** bằng cách thiết lập trực tiếp file `.claude/settings.json`.

---

## 1. Yêu Cầu Tiền Đề

Để sử dụng mô hình **MiniMax-M3** với Claude Code, bạn cần có:
- **Claude Code CLI** đã được cài đặt thành công (Xem hướng dẫn tại [00-claude-code.md](./00-claude-code.md)).
- **MiniMax API Key** (được cấp trong buổi học): Đã đăng ký tài khoản và tạo API Key tại [MiniMax Developer Platform](https://platform.minimax.io/user-center/payment/token-plan).

---

## 2. Các Bước Cấu Hình Chi Tiết

### ⚠️ Lưu ý quan trọng trước khi cấu hình
Hãy xóa các biến môi trường Anthropic cũ (nếu có) để tránh xung đột, vì biến môi trường hệ thống sẽ ưu tiên đè lên cấu hình trong file `settings.json`:

**macOS/Linux (bash, zsh) — cho phiên terminal hiện tại:**
```bash
unset ANTHROPIC_AUTH_TOKEN
unset ANTHROPIC_BASE_URL
```

**Windows PowerShell:**
```powershell
Remove-Item Env:\ANTHROPIC_AUTH_TOKEN -ErrorAction SilentlyContinue
Remove-Item Env:\ANTHROPIC_BASE_URL -ErrorAction SilentlyContinue
```

*(Nếu bạn từng thêm dòng `export ANTHROPIC_...` trong file `~/.bashrc`/`~/.zshrc` (macOS/Linux) hoặc Environment Variables của Windows, hãy xóa các dòng đó — nếu không, biến sẽ tự xuất hiện lại ở phiên terminal kế tiếp)*.

---

### 📝 Bước 1: Tạo Hoặc Chỉnh Sửa File `.claude/settings.json`

File cấu hình có thể được áp dụng ở 2 cấp độ tùy thuộc vào nhu cầu của bạn:
- **Toàn cục (Global)**: `~/.claude/settings.json` *(áp dụng mặc định cho tất cả dự án)*.
- **Theo dự án (Project-level)**: `.claude/settings.json` *(nằm tại thư mục gốc của dự án)*.

---

### ⚙️ Bước 2: Thêm Khối Cấu Hình `"env"`

Mở file `settings.json` và thêm (hoặc cập nhật) khối `"env"` theo mẫu dưới đây:

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.minimax.io/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "<MINIMAX_TOKEN>",
    "CLAUDE_CODE_AUTO_COMPACT_WINDOW": "1000000",
    "ANTHROPIC_MODEL": "MiniMax-M3[1m]",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "MiniMax-M3[1m]",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "MiniMax-M3[1m]",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "MiniMax-M3[1m]"
  }
}
```

> [!NOTE]
> **Giải thích chi tiết các thông số:**
> - `ANTHROPIC_BASE_URL`: Địa chỉ Endpoint API của MiniMax tương thích Anthropic SDK (`https://api.minimax.io/anthropic` cho người dùng quốc tế, hoặc `https://api.minimaxi.com/anthropic` cho người dùng tại Trung Quốc).
> - `ANTHROPIC_AUTH_TOKEN`: Thay `<MINIMAX_TOKEN>` bằng mã API Key lấy từ [MiniMax Platform](https://platform.minimax.io/user-center/payment/token-plan).
> - `CLAUDE_CODE_AUTO_COMPACT_WINDOW`: Đặt thành `1000000` (1 triệu tokens), khớp với Context Window của mô hình MiniMax-M3.
> - `ANTHROPIC_MODEL` & các biến mô hình mặc định: Đặt thành `MiniMax-M3[1m]` để Claude Code mặc định sử dụng mô hình MiniMax-M3 cho mọi tác vụ.

---

### 🧪 Bước 3: Kiểm Tra & Xác Minh Cấu Hình Trong Terminal

1. Mở terminal tại thư mục dự án và gõ lệnh:
   ```bash
   claude
   ```
2. Sau khi khởi động, chọn **Trust This Folder** để cấp quyền cho Claude Code làm việc trong thư mục.
3. Trong giao diện dòng lệnh Claude Code (TUI), gõ các câu lệnh slash để kiểm tra:
   - `/status` ➔ Xác nhận `ANTHROPIC_BASE_URL` trỏ tới `api.minimax.io/anthropic`.
   - `/model` ➔ Xác nhận mô hình đang active hiển thị `MiniMax-M3`.

---

## 🔗 4. Tài Liệu Tham Khảo (References)

| Tài nguyên | Đường dẫn (URL) |
| :--- | :--- |
| 🌐 **Tài liệu cấu hình MiniMax cho Claude Code (Chính thức)** | [platform.minimax.io/docs/token-plan/claude-code](https://platform.minimax.io/docs/token-plan/claude-code) |
| 🔑 **MiniMax API Key Platform** (được cấp trong khóa học) | [platform.minimax.io/user-center/payment/token-plan](https://platform.minimax.io/user-center/payment/token-plan) |
| 📚 **Anthropic Claude Code Docs** | [code.claude.com/docs/en/setup](https://code.claude.com/docs/en/setup) |
