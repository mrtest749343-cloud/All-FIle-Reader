"""
viewers/generic_viewer.py — Metadata + hex-preview viewer for unknown file types.
"""

from __future__ import annotations

import os
import stat
import time
import threading
import tkinter as tk
import customtkinter as ctk

from base_viewer import BaseViewer


class GenericViewer(BaseViewer):

    def __init__(self, master, path: str):
        super().__init__(master, path, viewer_type="generic")
        self.geometry("680x540")
        self._build_metadata_panel()
        self._build_hex_panel()
        self._load_async()

    # ── Metadata panel ───────────────────────────────────────────────────────
    def _build_metadata_panel(self):
        panel = ctk.CTkFrame(self.body, fg_color="#141428", corner_radius=12)
        panel.pack(fill="x", padx=20, pady=(16, 8))

        ctk.CTkLabel(
            panel,
            text="📄  File Information",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#a8dadc",
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(12, 6))

        self._meta_vars: dict[str, tk.StringVar] = {}
        labels = [
            ("Name",       os.path.basename(self.path)),
            ("Path",       self.path),
            ("Extension",  os.path.splitext(self.path)[1] or "(none)"),
            ("Size",       self._human_size()),
            ("Modified",   self._mod_time()),
            ("Permissions","…"),
        ]

        for row, (key, val) in enumerate(labels, start=1):
            ctk.CTkLabel(
                panel,
                text=key,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#6b7280",
                anchor="e",
                width=90,
            ).grid(row=row, column=0, sticky="e", padx=(16, 8), pady=3)

            var = tk.StringVar(value=val)
            self._meta_vars[key] = var
            ctk.CTkLabel(
                panel,
                textvariable=var,
                font=ctk.CTkFont(size=12),
                text_color="#e2e8f0",
                anchor="w",
                wraplength=480,
            ).grid(row=row, column=1, sticky="w", padx=(0, 16), pady=3)

        panel.grid_columnconfigure(1, weight=1)
        ctk.CTkFrame(panel, height=12, fg_color="transparent").grid(row=99, column=0)

    # ── Hex preview panel ────────────────────────────────────────────────────
    def _build_hex_panel(self):
        ctk.CTkLabel(
            self.body,
            text="HEX PREVIEW  (first 256 bytes)",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#4a5568",
            anchor="w",
        ).pack(fill="x", padx=24, pady=(4, 2))

        frame = ctk.CTkFrame(self.body, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self._hex_text = tk.Text(
            frame,
            wrap="none",
            state="disabled",
            font=("Courier", 11),
            bg="#0a0a18",
            fg="#68d391",
            relief="flat",
            padx=12,
            pady=8,
            height=10,
        )
        sb_y = ctk.CTkScrollbar(frame, command=self._hex_text.yview)
        sb_x = ctk.CTkScrollbar(frame, orientation="horizontal", command=self._hex_text.xview)
        self._hex_text.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)

        sb_y.pack(side="right", fill="y")
        sb_x.pack(side="bottom", fill="x")
        self._hex_text.pack(side="left", fill="both", expand=True)

    # ── Async data load ──────────────────────────────────────────────────────
    def _load_async(self):
        threading.Thread(target=self._load_data, daemon=True).start()

    def _load_data(self):
        try:
            # Permissions
            st = os.stat(self.path)
            perm = stat.filemode(st.st_mode)
            self.after(0, lambda: self._meta_vars["Permissions"].set(perm))

            # Hex preview
            with open(self.path, "rb") as fh:
                raw = fh.read(256)
            hex_lines = self._format_hex(raw)
            self.after(0, self._display_hex, hex_lines)
        except Exception as exc:
            self.after(0, self._display_hex, f"⚠  {exc}")

    def _display_hex(self, content: str):
        self._hex_text.configure(state="normal")
        self._hex_text.delete("1.0", "end")
        self._hex_text.insert("1.0", content)
        self._hex_text.configure(state="disabled")

    # ── Helpers ──────────────────────────────────────────────────────────────
    @staticmethod
    def _format_hex(data: bytes) -> str:
        lines = []
        for i in range(0, len(data), 16):
            chunk = data[i:i+16]
            hex_part  = " ".join(f"{b:02X}" for b in chunk).ljust(47)
            ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
            lines.append(f"{i:04X}  {hex_part}  │{ascii_part}│")
        return "\n".join(lines)

    def _human_size(self) -> str:
        size = os.path.getsize(self.path)
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def _mod_time(self) -> str:
        ts = os.path.getmtime(self.path)
        return time.strftime("%Y-%m-%d  %H:%M:%S", time.localtime(ts))
