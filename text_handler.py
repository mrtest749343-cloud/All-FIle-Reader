"""
handlers/text_handler.py — Handles all text-readable file formats.
Heavy imports (docx, pdfplumber) are loaded lazily inside extract_text().
"""

from __future__ import annotations

import os

from base_handler import FileHandler

_TEXT_EXTENSIONS = {
    ".txt", ".md", ".rst", ".log", ".ini", ".cfg", ".env",
    ".json", ".xml", ".yaml", ".yml", ".toml", ".csv", ".tsv",
    ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".htm", ".css",
    ".sh", ".bat", ".sql", ".r", ".java", ".c", ".cpp", ".h",
    ".go", ".rb", ".php", ".swift", ".kt", ".rs",
    ".docx", ".pdf", ".rtf",
}


class TextHandler(FileHandler):

    @staticmethod
    def can_handle(path: str) -> bool:
        ext = os.path.splitext(path)[1].lower()
        if ext in _TEXT_EXTENSIONS:
            return True
        # Fallback: try to detect plain-text files with no extension
        if ext == "":
            try:
                with open(path, "rb") as fh:
                    chunk = fh.read(512)
                # Heuristic: if >90 % of bytes are printable ASCII → text
                printable = sum(32 <= b < 127 or b in (9, 10, 13) for b in chunk)
                return printable / max(len(chunk), 1) > 0.90
            except Exception:
                return False
        return False

    def open_viewer(self, path: str, parent) -> None:
        # Lazy import — only pulled in when we actually need the viewer
        from text_viewer import TextViewer
        TextViewer(parent, path)

    # ── Text extraction (used by TextViewer) ─────────────────────────────────
    @staticmethod
    def extract_text(path: str) -> str:
        ext = os.path.splitext(path)[1].lower()

        if ext == ".pdf":
            return TextHandler._read_pdf(path)
        if ext == ".docx":
            return TextHandler._read_docx(path)
        if ext == ".rtf":
            return TextHandler._read_rtf(path)
        # All other text formats
        return TextHandler._read_plain(path)

    @staticmethod
    def _read_plain(path: str) -> str:
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
        for enc in encodings:
            try:
                with open(path, "r", encoding=enc) as fh:
                    return fh.read()
            except (UnicodeDecodeError, LookupError):
                continue
        # Binary fallback — show hex-like dump
        with open(path, "rb") as fh:
            raw = fh.read(8192)
        return raw.decode("latin-1")

    @staticmethod
    def _read_pdf(path: str) -> str:
        try:
            import pdfplumber  # type: ignore
            with pdfplumber.open(path) as pdf:
                pages = []
                for i, page in enumerate(pdf.pages, 1):
                    page_content = f"── Page {i} ──\n"
                    
                    # Extract tables first
                    try:
                        tables = page.extract_tables()
                        if tables:
                            page_content += "\n[TABLES]\n"
                            for table_idx, table in enumerate(tables, 1):
                                page_content += f"\nTable {table_idx}:\n"
                                # Format table as ASCII
                                if table:
                                    # Get column widths
                                    col_widths = [max(len(str(row[col])) if col < len(row) else 0 for row in table) for col in range(len(table[0]))]
                                    # Print header separator
                                    page_content += "+" + "+".join("-" * (w + 2) for w in col_widths) + "+\n"
                                    # Print rows
                                    for row in table:
                                        cells = [str(cell or "").ljust(col_widths[idx]) for idx, cell in enumerate(row)]
                                        page_content += "| " + " | ".join(cells) + " |\n"
                                    page_content += "+" + "+".join("-" * (w + 2) for w in col_widths) + "+\n"
                            page_content += "\n"
                    except Exception as table_err:
                        pass  # Skip table extraction if it fails
                    
                    # Extract regular text
                    text = page.extract_text() or ""
                    if text.strip():
                        page_content += "[TEXT]\n" + text
                    
                    if page_content.strip():
                        pages.append(page_content)
                
                return "\n\n".join(pages) if pages else "(No extractable content found in PDF)"
        except ImportError:
            pass
        # Fallback: PyPDF2 (doesn't support table extraction)
        try:
            import PyPDF2  # type: ignore
            text_parts = []
            with open(path, "rb") as fh:
                reader = PyPDF2.PdfReader(fh)
                for i, page in enumerate(reader.pages, 1):
                    t = page.extract_text() or ""
                    text_parts.append(f"── Page {i} ──\n{t}")
            return "\n\n".join(text_parts) or "(No extractable text)"
        except ImportError:
            return "⚠  PDF reading requires pdfplumber or PyPDF2.\nInstall: pip install pdfplumber"

    @staticmethod
    def _read_docx(path: str) -> str:
        try:
            import docx  # type: ignore
            doc = docx.Document(path)
            paragraphs = [p.text for p in doc.paragraphs]
            return "\n".join(paragraphs)
        except ImportError:
            return "⚠  DOCX reading requires python-docx.\nInstall: pip install python-docx"
        except Exception as exc:
            return f"⚠  Could not read DOCX: {exc}"

    @staticmethod
    def _read_rtf(path: str) -> str:
        # Best-effort: strip RTF control words
        with open(path, "rb") as fh:
            raw = fh.read().decode("latin-1")
        import re
        text = re.sub(r"\\[a-z]+\d* ?", " ", raw)
        text = re.sub(r"[{}\\]", "", text)
        return text.strip()
