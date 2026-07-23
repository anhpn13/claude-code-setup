#!/usr/bin/env python3
"""Parse a document (PDF/DOCX/PPTX/XLSX/images/...) to Markdown via Docling,
with content-hash caching so each file is only parsed once.

Usage:
    python parse_doc.py <file> [--force] [--no-ocr] [--ocr-lang LANGS] [--fast]

Prints the path of the cached Markdown file for the caller to Read.
Exit codes: 0 = success or pass-through, 1 = input error, 2 = docling failure.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Plain-text formats the Read tool handles natively — no parsing needed.
PASS_THROUGH = {".txt", ".md", ".markdown", ".rst", ".csv", ".tsv", ".log",
                ".json", ".yaml", ".yml", ".toml", ".xml"}

# Formats Docling supports (subset most relevant for this skill).
DOCLING_EXTS = {".pdf", ".docx", ".pptx", ".xlsx", ".docm", ".pptm", ".xlsm",
                ".odt", ".ods", ".odp",
                ".html", ".htm", ".epub", ".adoc", ".asciidoc",
                ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}

# Default PDF backend: docling_parse (docling's default) crashes natively on
# some PDFs on Windows; pypdfium2 is lighter and has not shown the issue.
PDF_BACKEND = "pypdfium2"


def cache_root() -> Path:
    base = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    return Path(base) / ".cache" / "docling"


def file_digest(path: Path, options: list[str]) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    h.update("|".join(options).encode("utf-8"))
    return h.hexdigest()[:16]


# Only worth showing a map of the document past this many lines — short files
# are cheap to just read in full.
TOC_MIN_LINES = 40
TOC_MAX_ENTRIES = 40

_ATX_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
# Fallback for docs with no real Markdown headings (e.g. DOCX authored with
# manual bold text instead of Word's "Heading" styles — Docling then has no
# structural signal to promote them to #, so they stay as bold paragraphs).
_BOLD_LINE = re.compile(r"^\*\*([^*]+)\*\*$")


def extract_toc(md_text: str) -> str:
    """Build a line-numbered outline: real # headings if present, else
    whole-line-bold paragraphs as a best-effort fallback. Empty string if
    neither pattern is found (nothing to map)."""
    lines = md_text.split("\n")

    atx = []
    for i, line in enumerate(lines, start=1):
        m = _ATX_HEADING.match(line)
        if m:
            atx.append((i, len(m.group(1)), m.group(2)))
    if atx:
        entries = atx
        source = "heading"
    else:
        entries = [(i, 1, m.group(1)) for i, line in enumerate(lines, start=1)
                   if (m := _BOLD_LINE.match(line))]
        source = "bold-line (không có # heading thật trong file này)"

    if not entries:
        return ""

    shown = entries[:TOC_MAX_ENTRIES]
    body = "\n".join(f"{'  ' * (level - 1)}L{ln}: {text}" for ln, level, text in shown)
    header = f"Mục lục ({source}, {len(entries)} mục" + (
        f", hiện {TOC_MAX_ENTRIES} đầu tiên" if len(entries) > TOC_MAX_ENTRIES else ""
    ) + "):"
    return f"{header}\n{body}"


def report_toc(out_md: Path) -> None:
    text = out_md.read_text(encoding="utf-8", errors="replace")
    n_lines = text.count("\n") + 1
    print(f"({n_lines} dòng Markdown)")
    if n_lines <= TOC_MIN_LINES:
        return
    toc = extract_toc(text)
    if toc:
        print(toc)
        print("→ Dùng offset/limit của Read hoặc Grep để nhảy thẳng tới mục cần, "
              "đừng đọc cả file.")
    else:
        print("(không phát hiện heading/mục — dùng Grep theo từ khoá để định vị "
              "nội dung cần tìm)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("file", help="document to parse")
    ap.add_argument("--force", action="store_true",
                    help="re-parse even if a cached result exists")
    ap.add_argument("--no-ocr", action="store_true",
                    help="skip OCR (much faster; use for digital, non-scanned PDFs)")
    ap.add_argument("--ocr-lang", default=None,
                    help="comma-separated OCR languages, e.g. 'vi,en'")
    ap.add_argument("--fast", action="store_true",
                    help="speed over fidelity for PDFs: implies --no-ocr and "
                         "skips the table-structure model (tables come out as "
                         "plain text, not Markdown tables)")
    args = ap.parse_args()

    src = Path(args.file).expanduser().resolve()
    if not src.is_file():
        print(f"ERROR: file not found: {src}", file=sys.stderr)
        return 1

    ext = src.suffix.lower()
    if ext in PASS_THROUGH:
        print("PASS-THROUGH: plain-text file, no parsing needed. "
              f"Read it directly with the Read tool:\n{src}")
        return 0
    if ext not in DOCLING_EXTS:
        print(f"WARNING: unrecognized extension '{ext}' — trying docling anyway.",
              file=sys.stderr)

    opts: list[str] = []
    if args.no_ocr or args.fast:
        opts.append("--no-ocr")
    if args.ocr_lang:
        opts += ["--ocr-lang", args.ocr_lang]
    if args.fast:
        opts.append("--no-tables")
    if ext == ".pdf":
        opts += ["--pdf-backend", PDF_BACKEND]

    key = file_digest(src, opts)
    out_dir = cache_root() / key
    out_md = out_dir / (src.stem + ".md")

    if out_md.is_file() and not args.force:
        print(f"CACHE HIT (key {key}) - already parsed, no work done. "
              f"Read the Markdown with the Read tool:\n{out_md}")
        report_toc(out_md)
        return 0

    docling = shutil.which("docling")
    if docling is None:
        print("ERROR: `docling` CLI not found on PATH.\n"
              "It is declared in this project's mise.toml - run `mise install` "
              "in the project root, then retry.", file=sys.stderr)
        return 2

    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [docling, str(src),
           "--to", "md",
           "--image-export-mode", "placeholder",
           "--output", str(out_dir),
           *opts]
    print("Parsing with Docling (first ever PDF/image parse downloads models "
          "to ~/.cache/docling/models - can take a while)...", file=sys.stderr)
    proc = subprocess.run(cmd, capture_output=True, text=True)

    if proc.returncode != 0 or not out_md.is_file():
        tail = "\n".join((proc.stderr or proc.stdout or "").splitlines()[-15:])
        print(f"ERROR: docling failed (exit {proc.returncode}).\n{tail}\n"
              "See the read-doc skill's reference.md for troubleshooting.",
              file=sys.stderr)
        return 2

    (out_dir / "meta.json").write_text(json.dumps({
        "source": str(src),
        "cache_key": key,
        "options": opts,
        "source_bytes": src.stat().st_size,
    }, indent=2), encoding="utf-8")

    print(f"PARSED OK - cached under key {key}. "
          f"Read it with the Read tool:\n{out_md}")
    report_toc(out_md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
