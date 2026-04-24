"""
viewers/base_viewer.py — Shared base class for all viewer windows.
"""

from __future__ import annotations

import os
import customtkinter as ctk


class BaseViewer(ctk.CTkToplevel):
    """
    A Toplevel window with:
      • consistent dark theme
      • a header bar showing filename + extension badge
      • a body frame for each viewer's content
      • Close button
    """

    _BADGE_COLORS: dict[str, str] = {
        "text":    "#2d6a4f",
        "audio":   "#1a3a6b",
        "video":   "#4a1942",
        "generic": "#4a3000",
    }

    def __init__(self, master, path: str, viewer_type: str = "generic", **kwargs):
        super().__init__(master, **kwargs)
        self.path = path
        self.viewer_type = viewer_type
        self._configure_window()
        self._build_header()
        self.body = ctk.CTkFrame(self, fg_color="#0f0f1a", corner_radius=0)
        self.body.pack(fill="both", expand=True)
        self.lift()
        self.focus_force()

    # ── Window setup ─────────────────────────────────────────────────────────
    def _configure_window(self):
        name = os.path.basename(self.path)
        self.title(name)
        self.geometry("800x560")
        self.configure(fg_color="#0f0f1a")
        self.resizable(True, True)

    # ── Header ───────────────────────────────────────────────────────────────
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=0, height=52)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Extension badge
        ext = os.path.splitext(self.path)[1].upper() or "???"
        badge_bg = self._BADGE_COLORS.get(self.viewer_type, "#333")
        ctk.CTkLabel(
            header,
            text=ext,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=badge_bg,
            corner_radius=6,
            width=48,
            height=26,
        ).pack(side="left", padx=14, pady=12)

        # Filename
        ctk.CTkLabel(
            header,
            text=os.path.basename(self.path),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#e2e8f0",
            anchor="w",
        ).pack(side="left", padx=4)

        # Close button
        ctk.CTkButton(
            header,
            text="✕  Close",
            width=90,
            height=30,
            corner_radius=8,
            fg_color="#3d1515",
            hover_color="#6b2121",
            font=ctk.CTkFont(size=12),
            command=self.destroy,
        ).pack(side="right", padx=14)
