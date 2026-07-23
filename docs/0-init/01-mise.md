# 🛠️ Hướng Dẫn Cài Đặt & Sử Dụng Mise Trên Windows

Tài liệu này hướng dẫn chi tiết từng bước để cài đặt và sử dụng **Mise** (trình quản lý môi trường phát triển & phiên bản công cụ siêu tốc) trên hệ điều hành Windows.

---

## 1. Mise Là Gì? Tại Sao Nên Sử Dụng?

**Mise** (trước đây là `rtx`) là một công cụ quản lý phiên bản môi trường đa năng (polyglot tool version manager) viết bằng Rust, thay thế hoàn toàn cho các công cụ như `nvm`, `fnm`, `pyenv`, `asdf`.

### 🌟 Ưu Điểm Nổi Bật

- ⚡ **Tốc độ cực nhanh**: Chạy mượt mà, không làm chậm cửa sổ Terminal/PowerShell.
- 📦 **Quản lý đa ngôn ngữ**: Quản lý cùng lúc Node.js, Python, Go, Rust, Ruby, Java, Claude Code...
- 📂 **Cấu hình theo dự án**: Tự động chuyển phiên bản công cụ khi bạn di chuyển (`cd`) vào từng thư mục dự án nhờ file `mise.toml`.

---

## 2. Các Bước Cài Đặt Trên Windows

### Bước 1: Cài đặt qua WinGet (Khuyên dùng)

`winget` là trình quản lý gói chính thức của Microsoft tích hợp sẵn trên Windows 10/11. Lệnh này sẽ tự động thêm Mise vào biến môi trường `PATH`.

Mở **PowerShell** và chạy lệnh:

```powershell
winget install --id jdx.mise --accept-source-agreements --accept-package-agreements
```

### Cách dự phòng: Cài qua PowerShell Script

Nếu máy tính của bạn không có `winget`, bạn có thể cài trực tiếp từ script chính thức:

```powershell
iwr https://mise.run/install.ps1 | iex
```

---

## 3. Khởi Động Lại Terminal & Kiểm Tra (Reload & Verify)

> [!IMPORTANT]
> **Khởi động lại Shell:**
> Sau khi cài đặt xong, cửa sổ PowerShell đang mở sẽ chưa nhận diện ngay được lệnh `mise`.
> 👉 Hãy **ĐÓNG và MỞ LẠI** cửa sổ PowerShell (hoặc tab Windows Terminal mới).

Sau khi mở cửa sổ mới, chạy các lệnh kiểm tra:

```powershell
mise --version          # Hiển thị phiên bản (Ví dụ: 2026.7.11 windows-x64)
mise doctor             # Kiểm tra hệ thống (Nên báo "No problems found")
```

> [!NOTE]
> Nếu gõ `mise` vẫn báo lỗi *"not recognized"*, bạn có thể kiểm tra xem đường dẫn WinGet đã có trong `PATH` người dùng chưa:
> ```powershell
> [System.Environment]::GetEnvironmentVariable('PATH', 'User') -split ';' | Where-Object { $_ -like '*WinGet\Links*' }
> ```

---

## 4. Hướng Dẫn Sử Dụng Nhanh (Quickstart)

### 4.1. Chạy thử công cụ mà không cần cài trước

Mise cho phép bạn chạy thử một phiên bản Node.js hay Python ngay lập tức:

```powershell
mise exec python@3.13 -- python --version
mise exec node@20 -- node --version
```

### 4.2. Cài đặt công cụ toàn cục (Global)

Cài đặt phiên bản dùng chung cho tất cả các thư mục trên máy tính:

```powershell
mise use --global node@lts
mise use --global python@3.13
mise use --global npm:@anthropic-ai/claude-code
```

*(Danh sách công cụ toàn cục sẽ được lưu tại `~\.config\mise\config.toml`)*.

---

## 5. Quản Lý Phiên Bản Theo Dự Án (Per-project)

Để cố định phiên bản Node.js hoặc Python cho từng dự án riêng biệt, tạo file `mise.toml` ở thư mục gốc dự án:

```toml
[tools]
node = "20.11.0"
python = "3.12.4"
```

Chạy lệnh `mise install` trong thư mục đó. Lần đầu tiên Mise thấy file mới sẽ hỏi xác nhận độ tin cậy:

```text
Trust it? [y/n]
```

👉 Nhấn `y` để xác nhận.

---

## 6. Cập Nhật Và Gỡ Bỏ (Updating & Removing)

```powershell
mise self-update        # Cập nhật chính Mise lên bản mới nhất
winget upgrade jdx.mise # Cập nhật qua WinGet
winget uninstall jdx.mise # Gỡ bỏ Mise qua WinGet
```

---

## 7. Mẹo & Lưu Ý Cho Windows

> [!NOTE]
> - **PowerShell 7+**: Tính năng tự động đổi `PATH` khi `cd` chuyển thư mục hoạt động mượt nhất trên **PowerShell 7 (`pwsh.exe`)**. Nếu dùng PowerShell 5.1 mặc định, bạn chỉ cần mở lại cửa sổ mới sau khi `cd`.
> - **Chạy song song**: Mise không can thiệp hay làm hỏng các bản Node/Python có sẵn của hệ thống.

---

## 🔗 8. Tài Liệu Tham Khảo & Đường Dẫn Tải Về (References)

| Tài nguyên | Đường dẫn (URL) |
| :--- | :--- |
| 🌐 **Trang chủ chính thức** | [mise.jdx.dev](https://mise.jdx.dev/) |
| 📖 **Tài liệu Bắt đầu (Getting Started)** | [mise.jdx.dev/getting-started.html](https://mise.jdx.dev/getting-started.html) |
| 🪟 **Hướng dẫn cài đặt Windows** | [mise.jdx.dev/installing-mise.html#windows](https://mise.jdx.dev/installing-mise.html#windows) |
| 💻 **Mise Windows Installer Script** | [mise.run/install.ps1](https://mise.run/install.ps1) |
| 🐙 **Mise GitHub Repository** | [github.com/jdx/mise](https://github.com/jdx/mise) |
| 🛠️ **Cấu hình `mise.toml` chi tiết** | [mise.jdx.dev/configuration.html](https://mise.jdx.dev/configuration.html) |
| 📦 **Danh sách công cụ hỗ trợ** | [mise.jdx.dev/dev-tools/](https://mise.jdx.dev/dev-tools/) |
