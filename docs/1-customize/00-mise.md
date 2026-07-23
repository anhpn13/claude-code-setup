# 🛠️ Hướng Dẫn Tùy Chỉnh Cấu Hình `mise.toml` 

Tài liệu này hướng dẫn chi tiết cách tùy chỉnh cấu hình file `mise.toml` trong dự án để thiết lập môi trường phát triển gồm **Python**, **Node.js** và tự động khởi tạo môi trường ảo Python (`.venv`).

---

## 1. Kiểm Tra Trạng Thái Mise Trên Máy

Trước khi bắt đầu, hãy xác nhận công cụ **Mise** đã được cài đặt và hoạt động bình thường trên máy tính của bạn:

```powershell
mise --version    # Kiểm tra phiên bản (Ví dụ: 2026.7.11 windows-x64)
mise doctor       # Kiểm tra sức khỏe hệ thống (Báo "No problems found")
```

> [!NOTE]
> Kết quả kiểm tra thực tế trên máy hiện tại:
> - **Phiên bản**: `2026.7.11 windows-x64`
> - **Trạng thái**: ✅ `No problems found` (Đã cài đặt thành công và sẵn sàng sử dụng).

---

## 2. Cấu Hình File `mise.toml` Cho Dự Án

File `mise.toml` được đặt tại thư mục gốc của dự án để khai báo và cố định danh sách các ngôn ngữ lập trình cùng môi trường ảo Python.

### Mẫu File Cấu Hình `mise.toml` (Node.js & Python)

Dưới đây là file `mise.toml` chuẩn hóa tích hợp **Python** và **Node.js**:

```toml
# mise configuration — https://mise.jdx.dev
# Áp dụng cho riêng thư mục dự án này.

[tools]
# 1. Python — chỉ định phiên bản Python yêu cầu
python = "3.13"

# 2. Node.js — theo dõi phiên bản LTS mới nhất
node = "lts"

[env]
# Tự động tạo và kích hoạt môi trường ảo Python tại thư mục .venv
_.python.venv = { path = ".venv", create = true }
```

---

## 3. Tự Động Quản Lý & Kích Hoạt Python Virtualenv (`.venv`)

> [!TIP]
> **Tính năng tự động tạo & kích hoạt Virtualenv:**
> Khai báo `_.python.venv = { path = ".venv", create = true }` trong khối `[env]` mang lại 2 lợi ích lớn:
> 1. **Tự động khởi tạo**: Khi bạn chạy lệnh `mise install`, Mise sẽ tự động khởi tạo một môi trường ảo `.venv` chuẩn hóa với đúng phiên bản Python được chọn trong `[tools]` mà không cần gõ lệnh `python -m venv .venv`.
> 2. **Tự động Activate**: Ngay khi bạn `cd` vào thư mục dự án, Mise sẽ tự động kích hoạt môi trường ảo `.venv` này (thêm các đường dẫn binary của `.venv` vào đầu biến `PATH`), loại bỏ hoàn toàn việc phải chạy thủ công lệnh `.\.venv\Scripts\Activate.ps1`.

---

## 4. Thực Hành Cài Đặt & Sử Dụng Các Công Cụ

Sau khi cập nhật file `mise.toml`, chạy lệnh sau để tải và cài đặt Node.js, Python cũng như tạo `.venv`:

```powershell
mise install
```

Màn hình sẽ xác nhận Mise tự động cài đặt các công cụ và khởi tạo `.venv`:
```text
mise python@3.13 ✓ installed
mise node@lts ✓ installed
mise creating venv with stdlib at: ...\.venv
mise all tools are installed
```

Kiểm tra danh sách các công cụ đã được cài đặt và kích hoạt trong dự án:

```powershell
mise ls
```

---

## 🔗 5. Tài Liệu Tham Khảo & Liên Kết

| Công cụ / Tài liệu | Đường dẫn (URL) |
| :--- | :--- |
| 🛠️ **Trang chủ Mise** | [mise.jdx.dev](https://mise.jdx.dev/) |
| 🐍 **Mise Python & Venv Management Docs** | [mise.jdx.dev/lang/python.html](https://mise.jdx.dev/lang/python.html) |
| 💚 **Mise Node.js Management Docs** | [mise.jdx.dev/lang/node.html](https://mise.jdx.dev/lang/node.html) |
