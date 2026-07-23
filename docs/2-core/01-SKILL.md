# 🎯 Skill — Đóng Gói Quy Trình Thành Lệnh Tái Sử Dụng

Tài liệu này trình bày chi tiết về **Skill** trong Claude Code: ý nghĩa, cấu trúc, cơ chế nạp vào context, và các khuyến nghị chính thức từ Anthropic ([code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills)).

---

## 1. Skill Là Gì?

**Skill** là một "gói kỹ năng" mở rộng khả năng của Claude: bạn viết hướng dẫn vào file `SKILL.md`, Claude thêm nó vào "hộp đồ nghề" — tự dùng khi phù hợp, hoặc bạn gọi trực tiếp bằng `/tên-skill`.

So sánh với CLAUDE.md để thấy rõ ý nghĩa:

| | CLAUDE.md | Skill |
| :--- | :--- | :--- |
| **Thời điểm nạp** | Luôn luôn, mọi phiên | Chỉ khi được gọi (on-demand) |
| **Phù hợp với** | Quy tắc ngắn, là *sự thật* của dự án | Quy trình nhiều bước, *cách làm* một việc |
| **Chi phí context** | Trả mỗi phiên | Gần như 0 cho tới khi dùng |

**Khi nào nên tạo Skill?** Theo docs chính thức: khi bạn thấy mình **dán đi dán lại cùng một đoạn hướng dẫn / checklist / quy trình nhiều bước** vào chat, hoặc khi một mục trong CLAUDE.md đã phình từ "một sự thật" thành "cả một quy trình" — hãy tách nó thành Skill.

> [!NOTE]
> - **Custom slash commands kiểu cũ đã được gộp vào Skill**: file `.claude/commands/deploy.md` và skill `.claude/skills/deploy/SKILL.md` đều tạo lệnh `/deploy` và hoạt động như nhau. Anthropic khuyến nghị dùng Skill vì hỗ trợ thêm supporting files, script đi kèm...
> - Skill tuân theo chuẩn mở **Agent Skills** ([agentskills.io](https://agentskills.io)) — dùng được cả ở Claude Code, claude.ai và Agent SDK.

---

## 2. Vị Trí Đặt & Quy Tắc Đặt Tên

Mỗi skill là **một thư mục** chứa file `SKILL.md`. **Tên thư mục chính là tên lệnh** (`.claude/skills/review-code/SKILL.md` → `/review-code`).

| Cấp độ | Vị trí | Áp dụng cho | Chia sẻ |
| :--- | :--- | :--- | :--- |
| **Personal** | `~/.claude/skills/<tên>/SKILL.md` | Mọi dự án của bạn | Chỉ mình bạn |
| **Project** | `.claude/skills/<tên>/SKILL.md` | Dự án hiện tại | Cả team (qua git) |
| **Plugin** | `<plugin>/skills/<tên>/SKILL.md` | Nơi plugin được bật | Qua cài plugin |
| **Enterprise** | Theo managed settings | Toàn tổ chức | IT quản lý |

**Khi trùng tên**: enterprise đè personal, personal đè project; skill ở bất kỳ cấp nào cũng đè skill có sẵn (bundled) cùng tên. Plugin skill có namespace riêng (`/tên-plugin:tên-skill`) nên không xung đột.

---

## 3. Cấu Trúc File `SKILL.md`

Gồm 2 phần: **frontmatter** (khối YAML giữa 2 dấu `---`) và **nội dung hướng dẫn** (Markdown). **Mọi trường frontmatter đều tùy chọn — chỉ `description` là được khuyến nghị bắt buộc** để Claude biết khi nào dùng skill.

```markdown
---
name: review-code
description: Review code theo checklist của team. Dùng khi cần review thay đổi trước khi commit/tạo MR.
argument-hint: "[đường-dẫn-file]"
allowed-tools: Read Grep Bash(git *)
---

Review code tại $ARGUMENTS theo checklist sau:

1. **Đúng đắn**: logic có case biên nào bị bỏ sót không?
2. **Bảo mật**: có hardcode secret/API key không?
3. **Chuẩn team**: đặt tên, format có theo quy ước trong CLAUDE.md không?

Xuất kết quả theo mức độ: 🔴 Phải sửa / 🟡 Nên sửa / 🟢 Gợi ý.
```

### Bảng tham chiếu frontmatter đầy đủ

| Trường | Ý nghĩa |
| :--- | :--- |
| `name` | Tên hiển thị trong danh sách skill (mặc định = tên thư mục; tên lệnh vẫn lấy theo thư mục). |
| `description` | **Quan trọng nhất** — căn cứ để Claude quyết định *khi nào tự dùng* skill. Nếu bỏ trống, lấy đoạn văn đầu tiên của nội dung. |
| `when_to_use` | Ngữ cảnh bổ sung: các cụm từ kích hoạt, ví dụ yêu cầu. Được nối vào sau `description`. |
| `argument-hint` | Gợi ý tham số hiện khi autocomplete, vd: `"[số-issue]"` hoặc `"[file] [format]"`. |
| `arguments` | Khai báo tham số có tên theo vị trí, vd `arguments: [issue, branch]` → dùng `$issue`, `$branch` trong nội dung. |
| `disable-model-invocation` | `true` = Claude **không tự ý** dùng; chỉ bạn gọi bằng `/tên`. Dành cho quy trình có tác dụng phụ (deploy, commit, gửi tin nhắn). |
| `user-invocable` | `false` = ẩn khỏi menu `/`; Claude vẫn tự dùng được. Dành cho "kiến thức nền" không phải hành động. |
| `allowed-tools` | Tool được dùng **không cần hỏi quyền** trong lượt gọi skill. Hết hiệu lực khi bạn gửi tin nhắn tiếp theo. Vd: `Bash(git *)`. |
| `disallowed-tools` | Tool bị **loại khỏi** phiên khi skill hoạt động. Cũng hết hiệu lực ở tin nhắn kế. |
| `model` | Model dùng khi skill chạy (`haiku`/`sonnet`/`opus`/`inherit`). Chỉ áp dụng cho lượt hiện tại. |
| `effort` | Mức nỗ lực suy luận: `low`/`medium`/`high`... (tùy model hỗ trợ). |
| `context` | `fork` = chạy skill trong **subagent tách biệt** (không dùng context hội thoại chính). |
| `agent` | Loại agent dùng khi `context: fork`: `Explore`, `Plan`, `general-purpose` hoặc custom agent (xem [03-AGENT.md](./03-AGENT.md)). Mặc định: `general-purpose`. |
| `hooks` | Hook (PreToolUse...) chỉ có hiệu lực trong vòng đời skill. |
| `paths` | Danh sách glob pattern — skill chỉ tự kích hoạt khi Claude làm việc với file khớp pattern. |
| `shell` | Shell chạy lệnh inline: `bash` (mặc định) hoặc `powershell` (hữu ích trên Windows). |

---

## 4. Ba Chế Độ Gọi Skill (Invocation Matrix)

Đây là bảng quan trọng nhất để thiết kế skill đúng ý đồ (nguyên văn từ docs chính thức):

| Frontmatter | Bạn gọi được? | Claude tự gọi được? | Nạp vào context khi nào |
| :--- | :---: | :---: | :--- |
| *(mặc định)* | ✅ | ✅ | Description luôn trong context; nội dung đầy đủ nạp khi được gọi |
| `disable-model-invocation: true` | ✅ | ❌ | Description **không** trong context; nạp khi bạn gọi `/tên` |
| `user-invocable: false` | ❌ | ✅ | Description luôn trong context; nạp khi Claude gọi |

**Cách chọn chế độ:**
- **Mặc định** — đa số skill: checklist review, quy ước viết API, template...
- **`disable-model-invocation: true`** — hành động có tác dụng phụ hoặc cần kiểm soát thời điểm: `/commit`, `/deploy`, `/send-slack-message`. Docs chính thức: *"Bạn không muốn Claude tự quyết định deploy chỉ vì thấy code có vẻ sẵn sàng."*
- **`user-invocable: false`** — kiến thức nền không phải hành động: skill `legacy-system-context` giải thích hệ thống cũ hoạt động ra sao — người dùng gõ `/legacy-system-context` chẳng có ý nghĩa gì, nhưng Claude cần tự tra khi đụng vào code cũ.

### Tham số & biến thay thế

| Biến | Ý nghĩa |
| :--- | :--- |
| `$ARGUMENTS` | Toàn bộ chuỗi tham số người dùng gõ. Nếu nội dung không chứa `$ARGUMENTS`, tham số được tự nối vào cuối. |
| `$0`, `$1`, `$2`... | Tham số theo vị trí (0-based). Giá trị nhiều từ thì bọc trong nháy: `/my-skill "hello world" second` → `$0` = `hello world`. |
| `$tên` | Tham số có tên khai báo trong `arguments`. |
| `${CLAUDE_SKILL_DIR}` | Thư mục chứa SKILL.md — dùng để gọi script đóng gói kèm skill. |
| `${CLAUDE_PROJECT_DIR}` | Thư mục gốc dự án. |
| `${CLAUDE_SESSION_ID}` | ID phiên hiện tại (hữu ích cho logging). |

Ví dụ: skill `migrate-component` với nội dung *"Migrate the $0 component from $1 to $2"* — gọi `/migrate-component SearchBar React Vue` → *"Migrate the SearchBar component from React to Vue"*.

---

## 5. Dynamic Context Injection — Bơm Dữ Liệu Thật Vào Skill

Cú pháp `` !`lệnh-shell` `` chạy lệnh **trước khi** nội dung skill được gửi cho Claude — output của lệnh **thay thế** placeholder, Claude chỉ nhìn thấy kết quả cuối, không thấy lệnh:

```markdown
---
description: Tóm tắt thay đổi chưa commit và cảnh báo rủi ro. Dùng khi người dùng hỏi "đã sửa gì", cần viết commit message, hoặc muốn review diff.
---

## Thay đổi hiện tại

!`git diff HEAD`

## Hướng dẫn

Tóm tắt các thay đổi trên trong 2-3 gạch đầu dòng, sau đó liệt kê rủi ro
(thiếu xử lý lỗi, hardcode giá trị, test cần cập nhật). Diff rỗng thì nói rõ.
```

Cần chạy nhiều lệnh thì dùng khối ` ```! `:

````markdown
```!
node --version
git status --short
```
````

> [!IMPORTANT]
> - Lệnh chạy **một lần duy nhất lúc nạp skill** (preprocessing) — không phải Claude thực thi, và output không được quét lại để chạy tiếp lệnh lồng nhau.
> - Dấu `!` phải ở **đầu dòng hoặc ngay sau khoảng trắng** thì mới được nhận diện.
> - Trên Windows không có Git Bash, thêm `shell: powershell` vào frontmatter để lệnh chạy bằng PowerShell.
> - Đây là tính năng mạnh nhưng nhạy cảm về bảo mật: tổ chức có thể tắt bằng `"disableSkillShellExecution": true` trong managed settings.

---

## 6. Supporting Files — Progressive Disclosure

Skill không chỉ có mỗi SKILL.md. Cấu trúc thư mục khuyến nghị:

```text
my-skill/
├── SKILL.md          # BẮT BUỘC — hướng dẫn chính + "bản đồ" trỏ tới file khác
├── reference.md      # Tài liệu chi tiết — chỉ nạp khi cần
├── examples.md       # Ví dụ đầu ra mẫu — chỉ nạp khi cần
└── scripts/
    └── helper.py     # Script để CHẠY, không nạp vào context
```

**Nguyên tắc progressive disclosure**: SKILL.md giữ phần cốt lõi; tài liệu dày (spec API, bộ ví dụ) tách ra file riêng và **tham chiếu từ SKILL.md kèm mô tả để Claude biết khi nào cần mở**:

```markdown
## Tài liệu bổ sung
- Chi tiết API đầy đủ: xem [reference.md](reference.md)
- Ví dụ sử dụng: xem [examples.md](examples.md)
```

**Đóng gói script**: skill có thể kèm script bất kỳ ngôn ngữ nào và cho phép chạy không cần hỏi quyền bằng cách kết hợp `${CLAUDE_SKILL_DIR}` ở cả 2 chỗ:

```markdown
---
name: render-chart
description: Vẽ biểu đồ từ file CSV
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/render.sh *)
---

Chạy `${CLAUDE_SKILL_DIR}/scripts/render.sh <file-csv>` để vẽ biểu đồ.
```

---

## 7. Skill Được Nạp Vào Context Như Thế Nào?

Hiểu cơ chế này để không lãng phí token:

- **Bình thường**: chỉ **description** của các skill nằm trong context (để Claude biết có gì); nội dung đầy đủ chỉ nạp khi skill được gọi.
- **Giới hạn description**: `description` + `when_to_use` bị cắt ở **1.536 ký tự** trong danh sách skill → **đưa use case chính lên đầu**.
- **Ngân sách danh sách skill** ≈ **1% context window** của model. Khi tràn, Claude Code bỏ bớt description của các skill *ít được gọi nhất* (tên thì luôn giữ).
- **Sau khi gọi**: nội dung skill **nằm lại trong context đến hết phiên** → mỗi dòng trong skill là chi phí token lặp lại.
- **Sau `/compact`**: mỗi skill được gắn lại tối đa **5.000 token** đầu, tổng các skill chung ngân sách **25.000 token** — skill gọi gần nhất được ưu tiên.

Kiểm tra chi phí thực tế: lệnh `/context` (dòng Skills) hoặc `/doctor`.

---

## 8. Best Practices (Khuyến Nghị Chính Thức Từ Anthropic)

1. **Giữ SKILL.md dưới 500 dòng** — tài liệu chi tiết tách ra supporting files.
2. **Thân skill phải cô đọng**: nội dung skill nằm lại trong context suốt phiên. *"Nói cần làm gì, đừng diễn giải vì sao"* — áp cùng tiêu chuẩn ngắn gọn như CLAUDE.md.
3. **Đầu tư vào `description`**: chứa **từ khóa người dùng sẽ gõ tự nhiên**, use case chính đặt lên đầu (vì bị cắt ở 1.536 ký tự). Description mơ hồ → skill không bao giờ được tự động gọi.
4. **Phân loại nội dung để chọn chế độ gọi**:
   - *Reference* (quy ước, pattern, style guide) → để mặc định, Claude tự áp dụng.
   - *Task* (deploy, commit, sinh code) → cân nhắc `disable-model-invocation: true` để bạn kiểm soát thời điểm.
5. **Viết dạng "chỉ dẫn thường trực"**: Claude không đọc lại file skill ở các lượt sau — hướng dẫn cần áp dụng xuyên suốt task thì viết như quy tắc thường trực, không phải bước làm-một-lần.
6. **`context: fork` chỉ dành cho skill có nhiệm vụ rõ ràng**: skill kiểu "hãy theo các quy ước API này" mà fork ra subagent thì subagent nhận được quy ước nhưng… không có việc gì để làm.
7. **Kiểm thử nghiêm túc**: thấy skill được kích hoạt ≠ skill hoạt động đúng. Docs khuyến nghị đo **2 thứ riêng biệt**: (a) Claude có gọi skill đúng lúc không, (b) đầu ra có đúng kỳ vọng không. Cách làm: chuẩn bị vài prompt thực tế, chạy trong **phiên mới tinh** có-skill và không-có-skill rồi so sánh (phiên mới quan trọng — context sót lại lúc viết skill sẽ che khuyết điểm của hướng dẫn).
8. **Một skill = một việc**: `review-code` riêng, `tao-release` riêng. Đừng gộp thành skill "làm-mọi-thứ".

### Xử lý sự cố thường gặp

| Triệu chứng | Cách xử lý |
| :--- | :--- |
| Skill không bao giờ được tự gọi | Thêm từ khóa tự nhiên vào `description`; hỏi Claude *"What skills are available?"* để xác nhận skill có trong danh sách; gọi thẳng `/tên-skill` để loại trừ lỗi nội dung. |
| Skill bị gọi quá thường xuyên | Thu hẹp `description` cho cụ thể hơn, hoặc chuyển sang `disable-model-invocation: true`. |
| `/tên-skill` chạy nhưng Claude không bao giờ tự dùng | Thường do YAML frontmatter lỗi cú pháp → Claude không đọc được `description`. Chạy `claude --debug` để xem lỗi parse. |
| Skill "hết tác dụng" giữa phiên dài | Nội dung vẫn còn nhưng model ưu tiên hướng khác — tăng độ rõ của chỉ dẫn, hoặc gọi lại skill sau khi `/compact`. |

---

## 9. Ví Dụ Tổng Hợp: Skill `/commit` An Toàn

Kết hợp nhiều kỹ thuật ở trên — chỉ gọi thủ công, cấp sẵn quyền git, bơm trạng thái repo:

```markdown
---
name: commit
description: Stage và commit các thay đổi hiện tại theo chuẩn conventional commits
disable-model-invocation: true
allowed-tools: Bash(git add *) Bash(git commit *) Bash(git status *)
---

## Trạng thái repo

!`git status --short`

## Nhiệm vụ

Commit các thay đổi trên:
1. Nhóm thay đổi liên quan vào cùng commit.
2. Viết message dạng conventional commits (feat/fix/docs...), tiếng Anh, ngắn gọn.
3. KHÔNG commit file chứa secret/API key — phát hiện thì dừng và cảnh báo.
```

> [!TIP]
> **Skill mẫu trong repo này**: [`.claude/skills/read-doc/`](../../.claude/skills/read-doc/SKILL.md) — skill đọc file PDF/Word/PowerPoint bằng Docling (chạy local), áp dụng đầy đủ các khuyến nghị trên: SKILL.md ngắn gọn + `reference.md` (progressive disclosure) + script đóng gói trong `scripts/` có cơ chế cache. Dùng nó làm khung khi viết skill của riêng bạn.

---

## 🔗 10. Tài Liệu Tham Khảo (References)

| Tài nguyên | Đường dẫn (URL) |
| :--- | :--- |
| 📖 **Claude Code Skills Docs (Chính thức)** | [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills) |
| 🌐 **Chuẩn mở Agent Skills** | [agentskills.io](https://agentskills.io) |
| 🧩 **Agent Skills — Anthropic Engineering** | [anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) |
| 📚 **Skill authoring best practices** | [platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) |
