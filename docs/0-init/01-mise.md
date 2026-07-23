# 🛠️ Hướng Dẫn Cài Đặt & Sử Dụng Mise (Windows / macOS / Linux)

Tài liệu này hướng dẫn chi tiết từng bước để cài đặt và sử dụng **Mise** (trình quản lý môi trường phát triển & phiên bản công cụ siêu tốc) trên **Windows, macOS và Linux**.

---

## 1. Mise Là Gì? Tại Sao Nên Sử Dụng?

**Mise** (trước đây là `rtx`) là một công cụ quản lý phiên bản môi trường đa năng (polyglot tool version manager) viết bằng Rust, thay thế hoàn toàn cho các công cụ như `nvm`, `fnm`, `pyenv`, `asdf`.

### 🌟 Ưu Điểm Nổi Bật

- ⚡ **Tốc độ cực nhanh**: Chạy mượt mà, không làm chậm cửa sổ Terminal.
- 📦 **Quản lý đa ngôn ngữ**: Quản lý cùng lúc Node.js, Python, Go, Rust, Ruby, Java, Claude Code...
- 📂 **Cấu hình theo dự án**: Tự động chuyển phiên bản công cụ khi bạn di chuyển (`cd`) vào từng thư mục dự án nhờ file `mise.toml`.
- 🖥️ **Cross-platform**: Cùng một `mise.toml` chạy được y hệt trên Windows, macOS, Linux.

---

## 2. Các Bước Cài Đặt

### macOS

Cách khuyến nghị — qua **Homebrew**:

```bash
brew install mise
```

Homebrew tự động thêm hook activation vào shell profile — thường không cần làm gì thêm. Kiểm tra bằng `mise doctor` (§ 3).

**Cách dự phòng** — script cài đặt trực tiếp:

```bash
curl https://mise.run | sh
```

Sau đó thêm dòng activation vào shell profile (xem § 2.3 bên dưới).

### Linux

**Script cài đặt (mọi distro):**

```bash
curl https://mise.run | sh
```

**Ubuntu/Debian (qua apt, dùng PPA):**

```bash
sudo add-apt-repository -y ppa:jdxcode/mise
sudo apt update
sudo apt install -y mise
```

**Fedora/RHEL (qua dnf):**

```bash
dnf copr enable jdxcode/mise
dnf install mise
```

Sau khi cài bằng script hoặc package manager, cần thêm dòng activation vào shell profile (xem § 2.3).

### 2.3. Kích hoạt Shell (Bắt buộc trên macOS/Linux nếu cài qua script/apt/dnf)

Thêm dòng sau vào file cấu hình shell tương ứng, rồi mở lại terminal:

**Bash** (`~/.bashrc`):
```bash
echo 'eval "$(mise activate bash)"' >> ~/.bashrc
```

**Zsh** (`~/.zshrc`, hoặc `$ZDOTDIR/.zshrc` nếu bạn có set `ZDOTDIR`):
```bash
echo 'eval "$(mise activate zsh)"' >> "${ZDOTDIR-$HOME}/.zshrc"
```

> [!NOTE]
> Nếu cài qua Homebrew, mise thường đã tự activate — chạy `mise doctor` để xác nhận trước khi thêm dòng trên (thêm 2 lần không hỏng gì, chỉ dư thừa).

### Windows

Cách khuyến nghị — qua **WinGet**:

`winget` là trình quản lý gói chính thức của Microsoft tích hợp sẵn trên Windows 10/11. Lệnh này sẽ tự động thêm Mise vào biến môi trường `PATH`.

Mở **PowerShell** và chạy lệnh:

```powershell
winget install --id jdx.mise --accept-source-agreements --accept-package-agreements
```

**Cách dự phòng** — Nếu máy tính của bạn không có `winget`:

```powershell
iwr https://mise.run/install.ps1 | iex
```

---

## 3. Khởi Động Lại Terminal & Kiểm Tra (Reload & Verify)

> [!IMPORTANT]
> **Khởi động lại Shell:**
> Sau khi cài đặt xong, cửa sổ terminal đang mở sẽ chưa nhận diện ngay được lệnh `mise`.
> 👉 Hãy **ĐÓNG và MỞ LẠI** cửa sổ terminal (hoặc tab mới).

Sau khi mở cửa sổ mới, chạy các lệnh kiểm tra (giống nhau trên mọi OS):

```bash
mise --version          # Hiển thị phiên bản, ví dụ: 2026.7.11 windows-x64 / macos-arm64 / linux-x64
mise doctor             # Kiểm tra hệ thống (Nên báo "No problems found")
```

> [!NOTE]
> **Windows** — Nếu gõ `mise` vẫn báo lỗi *"not recognized"*, kiểm tra xem đường dẫn WinGet đã có trong `PATH` người dùng chưa:
> ```powershell
> [System.Environment]::GetEnvironmentVariable('PATH', 'User') -split ';' | Where-Object { $_ -like '*WinGet\Links*' }
> ```
> **macOS/Linux** — Nếu vẫn báo `command not found`, kiểm tra dòng `eval "$(mise activate ...)"` đã có trong đúng file profile mà shell hiện tại đọc (`echo $SHELL` để biết đang dùng bash hay zsh).

---

## 4. Hướng Dẫn Sử Dụng Nhanh (Quickstart)

### 4.1. Chạy thử công cụ mà không cần cài trước

Mise cho phép bạn chạy thử một phiên bản Node.js hay Python ngay lập tức (cú pháp giống nhau mọi OS):

```bash
mise exec python@3.13 -- python --version
mise exec node@20 -- node --version
```

### 4.2. Cài đặt công cụ toàn cục (Global)

Cài đặt phiên bản dùng chung cho tất cả các thư mục trên máy tính:

```bash
mise use --global node@lts
mise use --global python@3.13
mise use --global npm:@anthropic-ai/claude-code
```

*(Danh sách công cụ toàn cục lưu tại `~/.config/mise/config.toml` trên macOS/Linux, `~\.config\mise\config.toml` trên Windows)*.

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

**macOS/Linux:**
```bash
mise self-update          # Cập nhật chính Mise lên bản mới nhất
brew upgrade mise          # Nếu cài qua Homebrew
```

**Windows:**
```powershell
mise self-update        # Cập nhật chính Mise lên bản mới nhất
winget upgrade jdx.mise # Cập nhật qua WinGet
winget uninstall jdx.mise # Gỡ bỏ Mise qua WinGet
```

---

## 7. Mẹo & Lưu Ý Theo Từng OS

> [!NOTE]
> - **Windows PowerShell 7+**: Tính năng tự động đổi `PATH` khi `cd` chuyển thư mục hoạt động mượt nhất trên **PowerShell 7 (`pwsh.exe`)**. Nếu dùng PowerShell 5.1 mặc định, bạn chỉ cần mở lại cửa sổ mới sau khi `cd`.
> - **macOS/Linux**: cơ chế tương đương dựa trên hook shell (`eval "$(mise activate bash|zsh)"`) — hoạt động ngay khi `cd`, không cần mở lại terminal.
> - **Chạy song song**: Mise không can thiệp hay làm hỏng các bản Node/Python có sẵn của hệ thống, trên mọi OS.

---

## 🔗 8. Tài Liệu Tham Khảo & Đường Dẫn Tải Về (References)

| Tài nguyên | Đường dẫn (URL) |
| :--- | :--- |
| 🌐 **Trang chủ chính thức** | [mise.jdx.dev](https://mise.jdx.dev/) |
| 📖 **Tài liệu Bắt đầu (Getting Started)** | [mise.jdx.dev/getting-started.html](https://mise.jdx.dev/getting-started.html) |
| 💻 **Hướng dẫn cài đặt đầy đủ (mọi OS)** | [mise.jdx.dev/installing-mise.html](https://mise.jdx.dev/installing-mise.html) |
| 🐙 **Mise GitHub Repository** | [github.com/jdx/mise](https://github.com/jdx/mise) |
| 🛠️ **Cấu hình `mise.toml` chi tiết** | [mise.jdx.dev/configuration.html](https://mise.jdx.dev/configuration.html) |
| 📦 **Danh sách công cụ hỗ trợ** | [mise.jdx.dev/dev-tools/](https://mise.jdx.dev/dev-tools/) |
