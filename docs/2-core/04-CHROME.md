# 🌐 Chrome — Cho Claude Code Điều Khiển Trình Duyệt Thật Của Bạn

Tài liệu này tổng hợp tính năng **Claude in Chrome**: cho phép Claude mở tab Chrome, đọc console, click, điền form, tải file... từ chính phiên Claude Code (CLI hoặc VS Code). Tài liệu chính thức: [code.claude.com/docs/en/chrome](https://code.claude.com/docs/en/chrome).

---

## 1. Nó Là Gì, Khác Gì So Với "Computer Use"?

Claude Code có 2 cách điều khiển máy tính:

| | **Claude in Chrome** | **Computer use** |
| :--- | :--- | :--- |
| Phạm vi | Trình duyệt Chrome của bạn | Toàn bộ desktop macOS |
| Cơ chế | Extension Chrome ↔ native messaging host | Claude điều khiển chuột/bàn phím |
| Đăng nhập | Dùng session bạn đang đăng nhập sẵn trong Chrome | Phải đăng nhập riêng |
| Khi nào dùng | Test web app, debug frontend, scrape dữ liệu, fill form | Tác vụ không làm được trong browser (vd app native) |

> Trong Claude Code bạn dùng **Chrome** cho mọi thứ liên quan tới web. Computer use chỉ là fallback cho việc ngoài browser.

---

## 2. Cài Đặt 1 Lần

Bạn cần có **đủ cả 3**:

1. **Google Chrome, Microsoft Edge, hoặc trình duyệt Chromium khác** (Brave, Arc, Vivaldi, Opera đều được — trừ WSL).
2. **Extension "Claude in Chrome"** từ Chrome Web Store — phiên bản ≥ 1.0.36 ([link cài](https://chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn)).
3. **Claude Code** + đăng nhập bằng tài khoản Anthropic trực tiếp (Pro / Max / Team / Enterprise).

> [!IMPORTANT]
> - **Extension auth độc lập với model provider**: extension xác thực qua **tài khoản claude.ai** (cần đăng ký Anthropic) — đây là auth của extension, **không liên quan** tới API key mà Claude Code CLI dùng để gọi model. Nghĩa là vẫn dùng Chrome extension bình thường khi chạy qua MiniMax / Bedrock / Vertex / Foundry — miễn là có tài khoản claude.ai để extension auth. Repo này chạy MiniMax + Chrome extension cùng lúc, hoạt động bình thường.
> - Tính năng Chrome **không có trên WSL**.

### Bật khi cần

```bash
claude --chrome                 # bật cho phiên này
```

Hoặc `/chrome` → chọn **Enabled by default** để mặc định luôn bật (đổi lại: tăng context usage vì browser tools luôn được nạp).

---

## 3. Những Gì Claude Làm Được Trong Chrome

Các tool bạn sẽ thấy trong session khi Chrome bật (`mcp__claude-in-chrome__*`):

| Nhóm tool | Mục đích |
| :--- | :--- |
| `tabs_context_mcp`, `tabs_create_mcp`, `tabs_close_mcp` | Quản lý tab: xem tab nào đang mở, mở tab mới, đóng tab |
| `navigate` | Điều hướng URL trong tab hiện tại |
| `computer`, `find`, `form_input`, `select_browser` | Click, gõ phím, tìm phần tử, điền form, chọn browser |
| `read_page`, `get_page_text` | Đọc DOM / text của trang (trả về Markdown) |
| `read_console_messages`, `read_network_requests` | Đọc log console và network — **debug frontend cực mạnh** |
| `gif_creator` | Quay GIF thao tác để demo / review |
| `javascript_tool` | Chạy JS tuỳ ý trong context trang |
| `file_upload`, `upload_image` | Upload file từ máy lên form web |
| `resize_window` | Đổi kích thước cửa sổ |

Tất cả đều có quyền site-level — quản lý trong **Chrome Extension settings**, không phải trong Claude Code.

---

## 4. Flow Làm Việc Thực Tế

### 4.1. Test web app đang chạy local

Bạn vừa sửa validation form, muốn Claude kiểm tra luôn:

```text
Mở localhost:3000, thử submit form với email không hợp lệ,
xem có hiện message lỗi đúng chỗ không.
```

Claude sẽ tự navigate, click, đọc DOM, báo lại.

### 4.2. Debug bằng console log

```text
Vào trang dashboard, đọc console xem có error nào khi load trang không.
```

Không nên hỏi "đọc tất cả console" — log rất ồn. Dùng `read_console_messages` với `pattern` (regex) để filter.

### 4.3. Điền form hàng loạt

```text
Đọc contacts.csv, với mỗi dòng vào CRM, click "Add Contact",
điền name + email + phone.
```

### 4.4. Upload file

```text
Vào bug tracker, tạo issue mới, attach logs/session.log.
```

**Giới hạn**: tổng ≤ 10 MB, file không có hard link (loại trừ `node_modules`).

### 4.5. Trích dữ liệu từ web

```text
Vào trang product listing, lấy name + price + availability cho từng sản phẩm,
lưu ra CSV.
```

### 4.6. Ghi vào Google Docs / Gmail / Notion

Vì Claude dùng session Chrome đang đăng nhập sẵn, không cần API connector:

```text
Dựa vào commit gần đây, viết project update rồi paste vào
Google Doc docs.google.com/document/d/abc...
```

### 4.7. Quay GIF demo

```text
Quay GIF luồng checkout từ "add to cart" tới "order confirmed".
```

> [!WARNING]
> GIF ghi lại **mọi thứ nhìn thấy trên màn hình**, kể cả thông tin đang đăng nhập. Review trước khi share ngoài team.

---

## 5. Quyền Và An Toàn

### 5.1. 2 loại tool call

| Loại | Ví dụ | Khi nào hỏi quyền |
| :--- | :--- | :--- |
| **Chỉ đọc** | `read_page`, `get_page_text`, `read_console_messages`, screenshot | Không hỏi (kể cả trong Plan mode) |
| **Thay đổi trạng thái** | Click, gõ, navigate, quản lý tab, quay GIF | **Luôn hỏi** |

Từ v2.1.199+, một số call "chỉ đọc" mà set flag state-changing (vd `createIfEmpty`, `clear` log, `save_to_disk` ảnh) cũng bị hỏi — chi tiết trong docs.

### 5.2. Site permission

Extension Claude in Chrome quản lý site-level permission riêng — **không** qua Claude Code. Khi Claude muốn làm việc trên một site lần đầu, extension sẽ hỏi bạn. Cấp quyền 1 lần thì nhớ.

### 5.3. Login & CAPTCHA

Claude **không đăng nhập được** và cũng không giải CAPTCHA. Khi gặp:

- Trang login: extension dừng lại, **bạn tự đăng nhập** trong cùng cửa sổ Chrome.
- CAPTCHA: bạn giải tay, rồi bảo Claude tiếp tục.

Đây là điểm mấu chốt: Chrome integration dùng session thật của bạn, nên những gì bạn đã đăng nhập thì Claude xài luôn — **không cần OAuth, không cần API key cho từng dịch vụ**.

---

## 6. Khi Gặp Lỗi

| Triệu chứng | Cách xử lý |
| :--- | :--- |
| "Browser extension is not connected" | Restart Chrome + Claude Code, `/chrome` → Reconnect extension |
| `/chrome` hiện "Not detected" | Vào `chrome://extensions` xem extension đã bật chưa |
| "No tab available" | Claude act trước khi tab sẵn sàng — bảo Claude tạo tab mới |
| Extension service worker idle sau lâu không dùng | `/chrome` → Reconnect extension |
| Modal dialog (alert/confirm) chặn | **Claude không dismiss được dialog** — bạn tắt tay trong Chrome |
| Named pipe conflict trên Windows | Đóng phiên Claude Code khác đang mở Chrome |
| Lần đầu bật mà không thấy extension | Restart Chrome — extension cần đọc native messaging config mới |

Debug chi tiết: chạy `claude --debug-file /tmp/claude.log` (hoặc `/debug` trong phiên) rồi đọc log.

---

## 7. Anti-Pattern — Khi Nào **Không** Nên Dùng Chrome

| Tình huống | Vì sao |
| :--- | :--- |
| Scrape hàng nghìn trang | Dùng API/Scraper chuyên dụng, không phải AI lái Chrome từng trang |
| Tác vụ lặp lại hàng ngày ổn định | Viết script chạy nền — Claude tốn token, không free, không reliable cho batch |
| Trang nặng JS cần đợi lâu | Claude dễ timeout — dùng Playwright/Selenium có retry/wait tốt hơn |
| Cần verify chính xác 100% layout | Claude "nhìn" screenshot/DOM khác designer nhìn — vẫn cần QA tay cho pixel-perfect |
| Bạn đang dùng MiniMax/Bedrock/Vertex | Chrome extension vẫn hoạt động bình thường — extension auth qua claude.ai độc lập với model provider |

---

## 🔗 Tài Liệu Tham Khảo

| Tài nguyên | URL |
| :--- | :--- |
| 📖 **Use Claude Code with Chrome (chính thức)** | [code.claude.com/docs/en/chrome](https://code.claude.com/docs/en/chrome) |
| 🧩 **Extension trên Chrome Web Store** | [chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn](https://chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn) |
| 🆘 **Hướng dẫn cho end-user** | [support.claude.com/en/articles/12012173](https://support.claude.com/en/articles/12012173-getting-started-with-claude-in-chrome) |
| 💻 **Computer use (fallback ngoài browser)** | [code.claude.com/docs/en/computer-use](https://code.claude.com/docs/en/computer-use) |