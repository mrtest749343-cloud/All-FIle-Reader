"""
viewers/text_viewer.py — Scrollable, read-only text viewer.
Supports: txt, md, pdf, docx, json, csv, code files, etc.
"""

from __future__ import annotations

import os
import json
import threading
import tkinter as tk
import customtkinter as ctk

from base_viewer import BaseViewer


class TextViewer(BaseViewer):

    def __init__(self, master, path: str):
        super().__init__(master, path, viewer_type="text")
        self._build_toolbar()
        self._build_text_area()
        self._build_statusbar()
        self._load_async()

    # ── Toolbar ──────────────────────────────────────────────────────────────
    def _build_toolbar(self):
        bar = ctk.CTkFrame(self.body, fg_color="#141428", corner_radius=0, height=38)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        ctk.CTkLabel(
            bar,
            text="🔍  Read-only view",
            font=ctk.CTkFont(size=11),
            text_color="#4a5568",
        ).pack(side="left", padx=12)

        # Font size controls
        self._font_size = tk.IntVar(value=13)
        ctk.CTkButton(bar, text="A−", width=36, height=26, command=self._font_dec).pack(side="right", padx=4, pady=6)
        ctk.CTkButton(bar, text="A+", width=36, height=26, command=self._font_inc).pack(side="right", padx=2, pady=6)

        # Word wrap toggle
        self._wrap = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            bar,
            text="Wrap",
            variable=self._wrap,
            command=self._toggle_wrap,
            font=ctk.CTkFont(size=11),
            width=70,
        ).pack(side="right", padx=10)

    def _font_inc(self):
        self._font_size.set(min(self._font_size.get() + 1, 28))
        self._apply_font()

    def _font_dec(self):
        self._font_size.set(max(self._font_size.get() - 1, 8))
        self._apply_font()

    def _apply_font(self):
        self._text.configure(font=("Consolas", self._font_size.get()))

    def _toggle_wrap(self):
        mode = "word" if self._wrap.get() else "none"
        self._text.configure(wrap=mode)

    # ── Text area ────────────────────────────────────────────────────────────
    def _build_text_area(self):
        frame = ctk.CTkFrame(self.body, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=0, pady=0)

        self._text = tk.Text(
            frame,
            wrap="word",
            state="disabled",
            font=("Consolas", 13),
            bg="#0f0f1a",
            fg="#c9d1d9",
            insertbackground="#c9d1d9",
            selectbackground="#264f78",
            relief="flat",
            padx=16,
            pady=12,
            borderwidth=0,
        )
        scrollbar = ctk.CTkScrollbar(frame, command=self._text.yview)
        self._text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self._text.pack(side="left", fill="both", expand=True)

    # ── Status bar ───────────────────────────────────────────────────────────
    def _build_statusbar(self):
        bar = ctk.CTkFrame(self.body, fg_color="#141428", corner_radius=0, height=28)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        self._status_var = tk.StringVar(value="Loading…")
        ctk.CTkLabel(
            bar,
            textvariable=self._status_var,
            font=ctk.CTkFont(size=11),
            text_color="#4a5568",
            anchor="w",
        ).pack(side="left", padx=12)

    # ── Async loading ────────────────────────────────────────────────────────
    def _load_async(self):
        threading.Thread(target=self._load_text, daemon=True).start()

    def _load_text(self):
        try:
            from text_handler import TextHandler
            content = TextHandler.extract_text(self.path)

            # Pretty-print JSON
            ext = os.path.splitext(self.path)[1].lower()
            if ext == ".json":
                try:
                    content = json.dumps(json.loads(content), indent=2, ensure_ascii=False)
                except Exception:
                    pass

            self.after(0, self._display_text, content)
        except Exception as exc:
            self.after(0, self._display_text, f"⚠  Error reading file:\n{exc}")

    def _display_text(self, content: str):
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        self._text.insert("1.0", content)
        self._text.configure(state="disabled")

        lines = content.count("\n") + 1
        chars = len(content)
        size = self._human_size()
        self._status_var.set(
            f"{lines:,} lines  •  {chars:,} chars  •  {size}  •  {os.path.basename(self.path)}"
        )

    def _human_size(self) -> str:
        size = os.path.getsize(self.path)
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
