---
name: read-doc
description: Đọc nội dung file PDF, Word (docx), PowerPoint (pptx), Excel (xlsx), ảnh scan, EPUB... bằng cách convert sang Markdown với Docling chạy hoàn toàn local, có cache (mỗi file chỉ parse một lần). Dùng khi cần đọc, tóm tắt, trích xuất thông tin từ file tài liệu mà tool Read không đọc được hoặc đọc kém.
argument-hint: "[đường-dẫn-file]"
allowed-tools: Bash(python ${CLAUDE_SKILL_DIR}/scripts/parse_doc.py *)
---

## Quy trình đọc file tài liệu (áp dụng xuyên suốt phiên)

1. Parse file bằng script kèm skill (cache tự động — file đã parse trước đó trả kết quả ngay, không tốn công parse lại):

   ```bash
   python "${CLAUDE_SKILL_DIR}/scripts/parse_doc.py" "<đường-dẫn-file>"
   ```

2. Script in ra đường dẫn file **Markdown** trong cache → dùng tool **Read** đọc file đó.
3. Nếu Markdown dài (script có báo số dòng): đọc theo từng phần bằng `offset`/`limit`, hoặc dùng Grep trên file cache để nhảy thẳng tới mục cần tìm — đừng nạp cả file lớn vào context.

## Tùy chọn của script

| Tình huống | Thêm cờ |
| :--- | :--- |
| PDF digital (chữ chọn được, không phải scan) | `--no-ocr` — nhanh hơn nhiều |
| Chỉ cần đọc nội dung chữ, không quan tâm bảng biểu chính xác | `--fast` — bỏ qua OCR + table-structure model, bảng ra text thô thay vì Markdown table |
| PDF/ảnh scan tiếng Việt | `--ocr-lang vi,en` |
| File nguồn đổi nội dung nhưng muốn ép parse lại | `--force` |

PDF luôn dùng backend `pypdfium2` (nhẹ hơn, ổn định hơn backend mặc định của Docling trên Windows).

## Quy tắc

- File `.txt`, `.md`, `.csv`, `.json`...: script trả về `PASS-THROUGH` → đọc trực tiếp bằng Read, không qua Docling.
- Script trả `CACHE HIT` nghĩa là dùng lại kết quả cũ — nếu người dùng nói file vừa được sửa, chạy lại với `--force`.
- Cần parse hàng loạt (>5 file) → hỏi người dùng trước, vì parse PDF tốn thời gian.
- Lần parse PDF/ảnh đầu tiên trên máy sẽ tải model về `~/.cache/docling/models` (cần mạng, hơi lâu) — báo trước cho người dùng nếu thấy chậm.

## Khi gặp lỗi hoặc cần flag Docling nâng cao

Xem [reference.md](reference.md) — cài đặt qua mise, bảng flag CLI đầy đủ, OCR engine, chạy offline, và cách xử lý các lỗi thường gặp.
