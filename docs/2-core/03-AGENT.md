# 🤖 Subagent — Trợ Lý Chuyên Biệt Với Context Riêng

Tài liệu này giải thích **Subagent (custom agent)** trong Claude Code: ý nghĩa, cách tạo, cách gọi và best practice. Cuối bài là phần thực hành tạo **Research Agent** — agent được khuyến nghị cho khóa học.

---

## 1. Subagent Là Gì?

**Subagent** là một "trợ lý AI chuyên biệt" được định nghĩa bằng file Markdown, có:
- 🧠 **Context window riêng** — chạy tách biệt, không làm phình context của phiên chính.
- 📜 **System prompt riêng** — được "huấn luyện" bằng chỉ dẫn chuyên cho 1 loại việc.
- 🔧 **Bộ tool giới hạn riêng** — chỉ được dùng những tool bạn cho phép.
- ⚡ **Model riêng** — có thể chạy model rẻ/nhanh hơn cho việc đơn giản.

**Ý nghĩa thực tế:**
- **Tiết kiệm context**: việc "đào bới" (đọc 30 file, search web 10 lần) diễn ra trong context của subagent; phiên chính chỉ nhận **kết luận cuối cùng**. Đây là kỹ thuật quan trọng nhất để làm việc lâu mà không bị đầy context.
- **An toàn hơn**: agent chỉ-đọc (không có tool `Write`/`Edit`) thì không thể sửa nhầm code.
- **Chuyên môn hóa**: mỗi agent một nghề — researcher, code-reviewer, debugger.

> [!NOTE]
> **Phân biệt với Skill**: Skill chạy **ngay trong** cuộc hội thoại chính (bơm hướng dẫn vào context hiện tại); Subagent chạy **tách riêng** rồi trả về kết quả. Việc nhẹ, cần tương tác → Skill. Việc nặng, nhiều bước tìm kiếm/đọc → Subagent.

---

## 2. Vị Trí Đặt File

| Vị trí | Phạm vi | Chia sẻ |
| :--- | :--- | :--- |
| `.claude/agents/<tên>.md` | Dự án hiện tại | Cả team (qua git) |
| `~/.claude/agents/<tên>.md` | Mọi dự án trên máy bạn | Chỉ mình bạn |

### Agent có sẵn (built-in)
Claude Code kèm sẵn một số agent: **Explore** (khám phá code, chỉ-đọc, nhanh), **Plan** (lập kế hoạch), **general-purpose** (đa dụng). Bạn tạo thêm custom agent khi cần hành vi chuyên biệt hơn.

---

## 3. Cấu Trúc File Agent

Gồm frontmatter (YAML) + system prompt (phần Markdown phía dưới):

```markdown
---
name: code-reviewer
description: Review code về chất lượng, bảo mật, chuẩn team. Dùng khi cần review thay đổi trước khi commit.
model: sonnet
tools:
  - Read
  - Grep
  - Glob
---

Bạn là senior code reviewer. Phân tích code theo các tiêu chí:
- Chất lượng thiết kế và pattern
- Lỗ hổng bảo mật
- Tuân thủ chuẩn của dự án (xem CLAUDE.md)

Đưa ra nhận xét cụ thể, chỉ rõ file:dòng, phân mức 🔴/🟡/🟢.
```

### Các trường frontmatter quan trọng

| Trường | Bắt buộc | Ý nghĩa |
| :--- | :---: | :--- |
| `name` | ✅ | Tên định danh để gọi agent. |
| `description` | ✅ | Căn cứ để Claude **tự quyết định giao việc** cho agent. Viết rõ: làm gì + dùng khi nào. |
| `model` | — | `haiku` / `sonnet` / `opus` / `inherit` (mặc định: kế thừa model phiên chính). |
| `tools` | — | **Danh sách trắng** tool được dùng. Không khai báo = kế thừa toàn bộ. Hỗ trợ pattern MCP: `mcp__firecrawl__*`. |
| `disallowedTools` | — | Danh sách đen — cấm tool cụ thể (vd: `Write`, `Edit`). |

> [!NOTE]
> **Lưu ý cho học viên dùng MiniMax**: giá trị `model: sonnet` là **tên lớp model**, sẽ được ánh xạ qua biến `ANTHROPIC_DEFAULT_SONNET_MODEL` trong `settings.json` — với setup của khóa học, tất cả đều trỏ về `MiniMax-M3[1m]` nên agent vẫn chạy bình thường. Khi dùng API Anthropic thật, `sonnet` sẽ là Claude Sonnet (cân bằng tốt giữa chất lượng/tốc độ/chi phí — phù hợp cho agent nghiên cứu).

---

## 4. Cách Gọi Agent

1. **Claude tự giao việc (auto-delegation)**: khi yêu cầu khớp với `description` — vd bạn gõ *"tìm hiểu giúp tôi cách dùng X"* → Claude tự giao cho agent `researcher`.
2. **Gọi đích danh trong chat**: nhắc tên agent, vd *"dùng agent researcher tìm hiểu về mise"*.
3. **Lệnh `/agents`**: mở giao diện quản lý — xem danh sách, tạo mới, chỉnh sửa agent.

---

## 5. Thực Hành: Tạo Research Agent (Khuyến Nghị Cho Khóa Học)

Đây là agent hữu ích nhất nên tạo đầu tiên: chuyên **nghiên cứu/tìm kiếm thông tin** bằng Firecrawl MCP, chỉ-đọc (an toàn), chạy model `sonnet`.

Tạo file `.claude/agents/researcher.md` với nội dung:

```markdown
---
name: researcher
description: Nghiên cứu chuyên sâu một chủ đề — search web bằng Firecrawl, đọc tài liệu/codebase, tổng hợp có nguồn. Dùng khi cần tìm hiểu công nghệ, thư viện, so sánh giải pháp, hoặc tra cứu tài liệu.
model: sonnet
tools:
  - Read
  - Grep
  - Glob
  - mcp__firecrawl__firecrawl_search
  - mcp__firecrawl__firecrawl_scrape
---

Bạn là trợ lý nghiên cứu kỹ lưỡng. Nhiệm vụ: điều tra chủ đề được giao và trả về
báo cáo ngắn gọn, chính xác, có dẫn nguồn.

## Quy trình
1. Xác định 2-4 câu hỏi con cần trả lời.
2. Search web bằng firecrawl_search; ưu tiên tài liệu chính thức.
3. Scrape trang quan trọng bằng firecrawl_scrape để đọc chi tiết.
4. Nếu liên quan tới dự án, đọc thêm code/docs trong repo (Read/Grep/Glob).
5. Đối chiếu chéo: thông tin quan trọng phải có ≥2 nguồn hoặc từ nguồn chính thức.

## Định dạng đầu ra
- **Kết luận** (2-3 câu trả lời thẳng câu hỏi).
- **Chi tiết** theo từng câu hỏi con, kèm URL nguồn.
- **Độ tin cậy**: ghi rõ điểm nào chưa chắc chắn / thông tin có thể đã cũ.
Không bịa nguồn. Không chắc thì nói không chắc.
```

### Kiểm tra agent hoạt động

1. Khởi động lại Claude Code (hoặc gõ `/agents` xác nhận `researcher` xuất hiện).
2. Thử giao việc:
   ```text
   dùng agent researcher: tìm hiểu mise là gì và so sánh với asdf
   ```
3. Quan sát: agent chạy trong context riêng, search bằng Firecrawl, và phiên chính chỉ nhận về bản báo cáo tổng hợp.

> [!TIP]
> File `.claude/agents/researcher.md` đã được tạo sẵn trong repo này để bạn dùng ngay và tham khảo.

---

## 6. Best Practices

1. **Một agent một nghề (single responsibility)**: `researcher` chỉ nghiên cứu, `code-reviewer` chỉ review. Agent "đa năng" thì description mơ hồ → Claude không biết lúc nào nên giao việc.
2. **Giới hạn tool chặt nhất có thể**: agent nghiên cứu không cần `Write`/`Edit`/`Bash`. Ít tool = an toàn hơn + agent tập trung hơn.
3. **Chọn model theo độ khó**: việc đọc-tóm tắt nhẹ → `haiku`; nghiên cứu/review → `sonnet`; suy luận phức tạp → `opus`. Đây là cách tối ưu chi phí quan trọng khi dùng API thật.
4. **Đầu tư vào `description`** (giống Skill): quyết định việc auto-delegation có hoạt động hay không.
5. **System prompt nêu rõ định dạng đầu ra**: agent trả kết quả về phiên chính — yêu cầu đầu ra có cấu trúc (kết luận trước, nguồn kèm theo) giúp phiên chính dùng lại dễ dàng.

---

## 🔗 7. Tài Liệu Tham Khảo (References)

| Tài nguyên | Đường dẫn (URL) |
| :--- | :--- |
| 📖 **Claude Code Subagents Docs (Chính thức)** | [code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents) |
| 🧠 **Multi-agent research system — Anthropic** | [anthropic.com/engineering/multi-agent-research-system](https://www.anthropic.com/engineering/multi-agent-research-system) |
| 🔌 **Bài trước: MCP** | [02-MCP.md](./02-MCP.md) |
