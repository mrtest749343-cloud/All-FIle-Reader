"""
Universal File Reader — main entry point.
Run: python main.py
"""

import sys
import os

# ── Ensure project root is on the path ──────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

import customtkinter as ctk
from tkinterdnd2 import TkinterDnD

from drop_zone import DropZone
from history_bar import HistoryBar

# ── Global appearance ────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class App(TkinterDnD.Tk):
    """Root window — inherits from TkinterDnD.Tk so DnD works on all children."""

    def __init__(self):
        super().__init__()
        self.title("Universal File Reader")
        self.geometry("720x480")
        self.resizable(True, True)
        self.minsize(600, 400)
        self.configure(bg="#1c1c2e")
        self._build_ui()

    # ── UI ───────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Header ──────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 6))

        ctk.CTkLabel(
            header,
            text="📂  Universal File Reader",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text="read-only · any format",
            font=ctk.CTkFont(size=12),
            text_color="#6b7280",
        ).pack(side="left", padx=12, pady=(6, 0))

        # ── Drop zone ────────────────────────────────────────────────────────
        self.drop_zone = DropZone(self)
        self.drop_zone.pack(padx=24, pady=(8, 6), fill="both", expand=True)

        # ── History bar ──────────────────────────────────────────────────────
        self.history_bar = HistoryBar(self, open_callback=self.drop_zone.open_file)
        self.history_bar.pack(padx=24, pady=(0, 16), fill="x")


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
