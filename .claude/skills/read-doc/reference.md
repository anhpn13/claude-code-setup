# read-doc — Tài liệu tham chiếu chi tiết

Tham chiếu cho skill `read-doc`. File này chỉ được nạp khi cần (progressive disclosure).
Nguồn: docs chính thức Docling v2.114.0 (tháng 7/2026) — https://docling-project.github.io/docling/reference/cli/

## 1. Docling là gì & vì sao chọn

[Docling](https://github.com/docling-project/docling) (dự án của IBM, thuộc LF AI & Data) parse tài liệu **hoàn toàn local** — không gửi dữ liệu ra dịch vụ bên thứ ba. Hiểu layout, bảng biểu, công thức; xuất Markdown sạch phù hợp cho LLM đọc.

**Định dạng vào**: PDF, DOCX, PPTX, XLSX, ODT/ODS/ODP, HTML, EPUB, Markdown, AsciiDoc, LaTeX, CSV, ảnh (PNG/JPEG/TIFF/BMP/WEBP)...
**Không hỗ trợ**: `.txt` thuần (script tự pass-through); `.doc`/`.xls`/`.ppt` đời cũ cần cài thêm LibreOffice.
**Định dạng ra**: `md` (mặc định), `json`, `html`, `text`, `doctags`, `chunks`...

## 2. Cài đặt qua mise (đã khai báo sẵn trong repo)

`mise.toml` của dự án đã khai báo:

```toml
[tools]
uv = "latest"                                              # pipx backend dùng uv bên dưới
"pipx:docling" = { version = "latest", extras = "easyocr" } # docling[easyocr], môi trường cách ly
```

Chạy `mise install` là có lệnh `docling` trên PATH. Lưu ý: gói nặng (kéo theo PyTorch), lần cài đầu mất vài phút.

Kiểm tra: `docling --version`

## 3. Cơ chế cache của skill

Docling **không có cache kết quả built-in** — script `scripts/parse_doc.py` tự làm:

- Khóa cache = SHA-256 (16 hex đầu) của **nội dung file + tùy chọn parse** → file đổi nội dung hay đổi tùy chọn là tự parse lại; trùng thì trả kết quả ngay.
- Vị trí: `<gốc-dự-án>/.cache/docling/<key>/<tên-file>.md` + `meta.json` (nguồn, tùy chọn, kích thước).
- Xóa cache: xóa thư mục `.cache/docling/`. Nếu dự án dùng git, thêm `.cache/` vào `.gitignore`.

## 4. Các flag CLI Docling hay dùng

Cú pháp: `docling <file-hoặc-url> [OPTIONS]` (mặc định đã là convert → Markdown).

| Flag | Giá trị (mặc định in đậm) | Ghi chú |
| :--- | :--- | :--- |
| `--to` | **md**, json, html, text, doctags, chunks | Lặp lại được để xuất nhiều định dạng |
| `--output` | thư mục (**.**) | File ra tên `<tên-gốc>.md` |
| `--ocr` / `--no-ocr` | **bật** | Tắt cho PDF digital → nhanh hơn nhiều |
| `--force-ocr` | tắt | Ép OCR đè cả text layer có sẵn |
| `--ocr-engine` | **auto**, easyocr, tesseract, rapidocr... | `auto` tự chọn engine có sẵn |
| `--ocr-lang` | vd `vi,en` | Tên ngôn ngữ tùy engine (easyocr: `vi`, `en`) |
| `--image-export-mode` | placeholder, **embedded**, referenced | Script dùng `placeholder` để Markdown không phình vì ảnh base64 |
| `--table-mode` | fast, **accurate** | Bảng phức tạp để `accurate` |
| `--pipeline` | **standard**, vlm, asr | `vlm` = parse bằng vision model (chậm, chất lượng khác) |
| `--pdf-backend` | **docling_parse**, pypdfium2... | Đổi khi PDF lỗi backend mặc định |
| `--device` | **auto**, cpu, cuda, mps | Có GPU NVIDIA thì `cuda` nhanh hơn hẳn |
| `--num-threads` | **4** | Tăng trên máy nhiều nhân |
| `--document-timeout` | giây | Chặn treo với file hỏng |
| `--enrich-formula`, `--enrich-code` | tắt | Bật khi cần công thức toán/code block chuẩn |
| `-v` / `-vv` | | Log info / debug khi cần chẩn đoán |

## 5. Model & chạy offline

- Lần parse **PDF/ảnh** đầu tiên, Docling tự tải model (layout, tableformer, OCR...) từ Hugging Face về `~/.cache/docling/models`. DOCX/PPTX/HTML **không cần model** — parse được ngay không cần mạng.
- Tải trước (chuẩn bị lớp học, máy hạn chế mạng):
  ```bash
  docling-tools models download                # bộ mặc định
  docling-tools models download -o /path/to/models  # chỉ định thư mục (macOS/Linux)
  docling-tools models download -o D:\models        # chỉ định thư mục (Windows)
  ```
- Trỏ model local: `docling --artifacts-path /path/to/models file.pdf` (hoặc `docling --artifacts-path "D:\models" file.pdf` trên Windows) hoặc đặt biến môi trường `DOCLING_ARTIFACTS_PATH`.

## 6. Xử lý sự cố

| Triệu chứng | Nguyên nhân / cách xử lý |
| :--- | :--- |
| `docling` not found | Chưa `mise install`, hoặc shell hiện tại chưa activate mise (PowerShell/Bash/Zsh) → mở lại terminal tại thư mục dự án. |
| Lần đầu parse PDF rất lâu | Đang tải model từ Hugging Face — bình thường. Tải trước bằng `docling-tools models download`. |
| PDF scan ra Markdown rỗng/thiếu chữ | OCR chưa chạy đúng: kiểm tra đã cài extra `easyocr` (mise.toml của repo đã có); thử `--force-ocr` và `--ocr-lang vi,en`. |
| PDF digital parse quá chậm | Thêm `--no-ocr` (OCR mặc định bật). |
| `.doc`/`.ppt`/`.xls` đời cũ lỗi | Docling cần LibreOffice cho định dạng legacy → convert sang docx/pptx trước, hoặc cài LibreOffice. |
| Máy không GPU (mọi OS), parse chậm | Bình thường với `--device cpu`; giảm kỳ vọng hoặc tăng `--num-threads`. |
| File đã sửa nhưng vẫn ra nội dung cũ | Không thể xảy ra theo thiết kế (cache theo hash nội dung) — nếu gặp, chạy script với `--force` và báo lại. |

## 7. Nguồn tham khảo

- CLI reference: https://docling-project.github.io/docling/reference/cli/
- Cài đặt: https://docling-project.github.io/docling/getting_started/installation/
- Định dạng hỗ trợ: https://docling-project.github.io/docling/usage/supported_formats/
- GitHub: https://github.com/docling-project/docling
- mise pipx backend: https://mise.jdx.dev/dev-tools/backends/pipx.html
