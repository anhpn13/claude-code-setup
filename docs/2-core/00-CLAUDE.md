# 🧠 CLAUDE.md — "Bộ Nhớ" Của Dự Án

Tài liệu này giải thích **CLAUDE.md** là gì, vì sao nó là file quan trọng nhất khi làm việc với **Claude Code**, và cách viết một file CLAUDE.md hiệu quả.

---

## 1. CLAUDE.md Là Gì?

**CLAUDE.md** là file hướng dẫn (dạng Markdown) được Claude Code **tự động nạp vào ngữ cảnh (context) ở đầu MỖI phiên làm việc**. Bạn có thể coi nó như bản "nội quy + sổ tay dự án" mà Claude luôn đọc trước khi bắt tay vào việc.

**Ý nghĩa thực tế:**
- 🔁 **Không phải lặp lại chỉ dẫn**: Những quy tắc bạn hay phải nhắc ("trả lời ngắn gọn", "dùng tiếng Việt", "chạy test trước khi commit") chỉ cần viết 1 lần.
- 📏 **Chuẩn hóa hành vi cho cả team**: File nằm trong repo, commit lên git → mọi thành viên dùng Claude Code đều nhận cùng một bộ quy tắc.
- 🧭 **Định hướng, không phải cấu hình**: Nội dung CLAUDE.md là *hướng dẫn bằng ngôn ngữ tự nhiên* đưa vào context, không phải config bắt buộc — vì vậy viết càng rõ ràng, Claude tuân thủ càng tốt.

---

## 2. Các Cấp Độ File & Vị Trí Đặt

Claude Code nạp CLAUDE.md từ nhiều vị trí (nội dung được **cộng dồn**, không ghi đè nhau):

| Cấp độ | Vị trí | Phạm vi áp dụng | Chia sẻ |
| :--- | :--- | :--- | :--- |
| **User (cá nhân)** | `~/.claude/CLAUDE.md` | Mọi dự án trên máy bạn | Chỉ mình bạn |
| **Project (dự án)** | `./CLAUDE.md` (thư mục gốc dự án) | Dự án hiện tại | Cả team (qua git) |
| **Local (cá nhân theo dự án)** | `./CLAUDE.local.md` | Dự án hiện tại | Chỉ mình bạn *(nhớ thêm vào `.gitignore`)* |
| **Thư mục con** | `subdir/CLAUDE.md` | Chỉ nạp khi Claude làm việc trong thư mục đó | Tùy vị trí |

> [!NOTE]
> **Quy tắc chọn nơi đặt:**
> - Sở thích cá nhân (phong cách trả lời, ngôn ngữ) → `~/.claude/CLAUDE.md`.
> - Quy ước của dự án/team (lệnh build, coding style) → `./CLAUDE.md` và commit lên git.
> - Ghi chú riêng chỉ mình bạn cần trong dự án → `./CLAUDE.local.md`.

---

## 3. Cách Tạo & Quản Lý

### Cách 1: Sinh tự động bằng lệnh `/init`
Mở Claude Code trong thư mục dự án và gõ:
```text
/init
```
Claude sẽ tự phân tích codebase (lệnh build, cấu trúc thư mục, quy ước code...) và sinh ra file `CLAUDE.md` ban đầu. Sau đó bạn chỉnh sửa lại theo nhu cầu.

### Cách 2: Viết tay
Tạo file `CLAUDE.md` ở thư mục gốc dự án và viết bằng Markdown thông thường.

### Xem & chỉnh sửa trong phiên làm việc
```text
/memory
```
Lệnh này liệt kê tất cả các file memory đang được nạp trong phiên hiện tại và cho phép mở để chỉnh sửa.

### Thêm ghi nhớ nhanh trong lúc chat
Khi đang làm việc, bạn có thể nói trực tiếp: *"thêm quy tắc này vào CLAUDE.md: luôn chạy `npm test` trước khi commit"* — Claude sẽ tự cập nhật file.

---

## 4. Import File Khác Với Cú Pháp `@path`

CLAUDE.md có thể tham chiếu nội dung file khác để giữ bản thân nó gọn gàng:

```markdown
Xem tổng quan dự án tại @README.md
Danh sách lệnh npm tại @package.json
Quy trình git của team: @docs/git-workflow.md
```

> [!NOTE]
> - Đường dẫn tương đối tính theo vị trí file chứa import; hỗ trợ cả đường dẫn tuyệt đối (vd: `@~/shared-rules.md`).
> - Import lồng nhau tối đa **4 cấp**.
> - Cú pháp `@path` nằm trong code block hoặc backtick sẽ **không** được thực thi (chỉ là chữ).

---

## 5. Best Practices Khi Viết CLAUDE.md

> [!IMPORTANT]
> **Nguyên tắc vàng: NGẮN và CỤ THỂ.** CLAUDE.md được nạp vào context ở *mọi* phiên — file càng dài càng tốn token và Claude càng khó tuân thủ đầy đủ.

1. **Giữ dưới ~200 dòng**. Nội dung chi tiết (quy trình nhiều bước, tài liệu tham khảo) nên tách ra file riêng rồi import bằng `@path`, hoặc chuyển thành **Skill** (xem bài [01-SKILL.md](./01-SKILL.md)).
2. **Cụ thể hơn là chung chung**:
   - ❌ "Hãy format code đẹp" → ✅ "Dùng indent 2 space, chạy `prettier --write` sau khi sửa file".
   - ❌ "Test kỹ trước khi xong" → ✅ "Chạy `npm test` trước khi commit".
3. **Dùng heading + bullet**, tránh đoạn văn dài. Cấu trúc rõ ràng giúp Claude "tra cứu" quy tắc chính xác hơn.
4. **Chỉ ghi những gì Claude không tự suy ra được**: quy ước riêng của team, lệnh đặc thù, điều cấm kỵ. Không cần chép lại những gì đã hiển nhiên trong code.
5. **Tránh mâu thuẫn**: nếu có nhiều CLAUDE.md (user + project), kiểm tra để các quy tắc không đá nhau.

### Ví dụ thực tế
File [`CLAUDE.md`](../../CLAUDE.md) ở thư mục gốc của chính repo này là một ví dụ chuẩn: ngắn gọn, chia nhóm rõ (Nguyên tắc / Output / Cách làm việc / Ngôn ngữ), mỗi quy tắc là 1 bullet cụ thể.

---

## 🔗 6. Tài Liệu Tham Khảo (References)

| Tài nguyên | Đường dẫn (URL) |
| :--- | :--- |
| 📖 **Claude Code Memory Docs (Chính thức)** | [code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory) |
| ✍️ **Claude Code Best Practices (Anthropic Blog)** | [anthropic.com/engineering/claude-code-best-practices](https://www.anthropic.com/engineering/claude-code-best-practices) |
| 📚 **Claude Code Docs** | [code.claude.com/docs](https://code.claude.com/docs) |
