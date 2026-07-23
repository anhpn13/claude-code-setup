# 🔌 MCP — Kết Nối Claude Với Công Cụ Bên Ngoài

Tài liệu này giải thích khái niệm **MCP (Model Context Protocol)** trong Claude Code: ý nghĩa, các phạm vi cấu hình, bảo mật và best practice. Phần thực hành cài đặt cụ thể (Firecrawl) xem tại bài [1-customize/01-mcp.md](../1-customize/01-mcp.md).

---

## 1. MCP Là Gì?

**MCP (Model Context Protocol)** là giao thức mở (do Anthropic khởi xướng) cho phép Claude Code kết nối với **công cụ và dữ liệu bên ngoài**: cơ sở dữ liệu, API, trình duyệt web, GitHub/GitLab, Slack...

Một **MCP Server** có thể cung cấp cho Claude 3 loại năng lực:

- 🛠️ **Tools**: các hàm Claude gọi được (search web, query database, tạo issue...).
- 📄 **Resources**: nguồn dữ liệu Claude đọc được (tài liệu, log, schema...).
- 📋 **Prompts**: các workflow định nghĩa sẵn, xuất hiện như slash command.

**Ý nghĩa thực tế:** bản thân model chỉ biết những gì có trong context và codebase. MCP là "cánh tay nối dài" — không có nó, Claude không tự search web, không đọc được Jira/GitLab, không truy cập database.

> [!IMPORTANT]
> **Với setup MiniMax của khóa học**: tính năng Web Search tích hợp sẵn của Claude Code chạy trên hạ tầng Anthropic nên **không hoạt động** khi trỏ API về MiniMax. Vì vậy MCP search (**Firecrawl**) là **bắt buộc** để Claude tìm kiếm thông tin trên web — đã hướng dẫn cài tại [1-customize/01-mcp.md](../1-customize/01-mcp.md).

---

## 2. Ba Phạm Vi (Scope) Cấu Hình

| Scope | Lưu ở đâu | Áp dụng | Chia sẻ |
| :--- | :--- | :--- | :--- |
| **Local** | `~/.claude.json` (mục riêng theo dự án) | Chỉ dự án hiện tại | Chỉ mình bạn |
| **Project** | `.mcp.json` tại thư mục gốc dự án | Dự án hiện tại | Cả team (qua git) |
| **User** | `~/.claude.json` (mục global) | Mọi dự án của bạn | Chỉ mình bạn |

**Cách chọn scope:**
- Server cả team cần (search, GitLab, database dev) → **Project** (`.mcp.json`, commit lên git).
- Tool cá nhân dùng ở mọi dự án → **User**.
- Thử nghiệm hoặc chứa credential nhạy cảm → **Local**.

---

## 3. Cách Thêm MCP Server

### Cách 1: Dùng lệnh CLI `claude mcp add`

```powershell
# Server dạng HTTP (remote) — khuyến nghị khi có
claude mcp add --transport http github https://api.githubcopilot.com/mcp/

# Server dạng stdio (chạy process local) — lưu ý dấu "--" ngăn cách
claude mcp add --transport stdio firecrawl -- firecrawl-mcp

# Chỉ định scope (mặc định là local)
claude mcp add --transport http context7 --scope project https://mcp.context7.com/mcp
```

### Cách 2: Viết trực tiếp file `.mcp.json` (scope project)

```json
{
  "mcpServers": {
    "firecrawl": {
      "command": "firecrawl-mcp",
      "args": [],
      "env": {
        "FIRECRAWL_API_KEY": "${FIRECRAWL_API_KEY}"
      }
    }
  }
}
```

> [!TIP]
> `.mcp.json` hỗ trợ **biến môi trường**: `${VAR}` hoặc `${VAR:-giá_trị_mặc_định}` trong các trường `command`, `args`, `env`, `url`, `headers`. Dùng cách này để **không commit API key thật** lên git.

### Các lệnh quản lý hữu ích

```powershell
claude mcp list        # Liệt kê server đã cấu hình + trạng thái
claude mcp get <tên>   # Xem chi tiết 1 server
claude mcp remove <tên>
```

Trong phiên Claude Code (TUI), gõ `/mcp` để xem trạng thái kết nối, số lượng tool và đăng nhập OAuth nếu server yêu cầu.

---

## 4. Quy Tắc Đặt Tên Tool

Tool từ MCP server luôn có tên dạng:

```text
mcp__<tên-server>__<tên-tool>

# Ví dụ:
mcp__firecrawl__firecrawl_search
mcp__firecrawl__firecrawl_scrape
```

Nắm quy tắc này để: cấu hình permission (`mcp__firecrawl__*` = cho phép mọi tool của server firecrawl), và giới hạn tool cho Subagent (xem bài [03-AGENT.md](./03-AGENT.md)).

---

## 5. Bảo Mật

> [!WARNING]
> MCP server là **code của bên thứ ba chạy với quyền truy cập dữ liệu của bạn**. Chỉ cài server từ nguồn tin cậy.

- **Duyệt trước khi chạy**: khi mở dự án có `.mcp.json` trong repo, Claude Code sẽ **hỏi bạn xác nhận** trước khi kết nối (chống repo độc hại cài server lạ). Lỡ chọn nhầm thì reset bằng: `claude mcp reset-project-choices`.
- **Không commit API key thật** vào `.mcp.json` — dùng biến môi trường `${VAR}` như ví dụ trên.
- **Prompt injection**: nội dung web/scrape trả về có thể chứa chỉ dẫn độc hại. Cảnh giác khi cho phép Claude tự động chạy lệnh dựa trên dữ liệu lấy từ ngoài.

---

## 6. Best Practices

1. **Ít mà chất**: mỗi MCP server thêm định nghĩa tool vào context (tốn token) và tăng bề mặt rủi ro. Chỉ bật server thực sự dùng; server thừa thì `claude mcp remove`.
2. **Chọn đúng scope**: tool của team → project scope để cả team dùng chung 1 cấu hình; đừng bắt mỗi người tự cài tay.
3. **Kiểm tra sau khi cài**: `/mcp` phải hiển thị server ở trạng thái **Connected** — chưa connected thì tool chưa dùng được.
4. **Output lớn**: kết quả tool bị giới hạn ~25.000 token. Khi cần scrape/crawl trang lớn, hướng dẫn Claude lấy từng phần thay vì cả trang.

---

## 🔗 7. Tài Liệu Tham Khảo (References)

| Tài nguyên | Đường dẫn (URL) |
| :--- | :--- |
| 📖 **Claude Code MCP Docs (Chính thức)** | [code.claude.com/docs/en/mcp](https://code.claude.com/docs/en/mcp) |
| 🌐 **Trang chủ Model Context Protocol** | [modelcontextprotocol.io](https://modelcontextprotocol.io/) |
| 🔥 **Bài thực hành: Cài Firecrawl MCP** | [1-customize/01-mcp.md](../1-customize/01-mcp.md) |
