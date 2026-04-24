"""
ui/drop_zone.py — Central drag-and-drop / click-to-select widget.
"""

from __future__ import annotations

import os
import threading
import tkinter as tk
import customtkinter as ctk
from tkinterdnd2 import DND_FILES
from tkinter import filedialog

from router import route_file


class DropZone(ctk.CTkFrame):
    """
    A rounded frame that:
      • accepts file drag-and-drop
      • opens a file dialog on click
      • dispatches to the correct viewer via handlers.router
    """

    _IDLE_TEXT = "⬇   Drop a file here\nor click to browse"
    _HOVER_TEXT = "Release to open file"

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            corner_radius=16,
            border_width=2,
            border_color="#2d6a4f",
            fg_color="#16213e",
            **kwargs,
        )

        self._build_ui()
        self._register_dnd()

    # ── UI ───────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Icon
        self._icon_label = ctk.CTkLabel(
            self,
            text="📁",
            font=ctk.CTkFont(size=52),
        )
        self._icon_label.pack(expand=True, pady=(30, 4))

        # Main instruction text
        self._text_label = ctk.CTkLabel(
            self,
            text=self._IDLE_TEXT,
            font=ctk.CTkFont(size=16),
            text_color="#a8dadc",
            justify="center",
        )
        self._text_label.pack(expand=True, pady=(4, 6))

        # Sub-hint
        self._hint_label = ctk.CTkLabel(
            self,
            text="txt · pdf · docx · mp3 · mp4 · zip · and more",
            font=ctk.CTkFont(size=11),
            text_color="#4a5568",
        )
        self._hint_label.pack(pady=(0, 30))

        # Status label (shown while processing)
        self._status_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#68d391",
        )
        self._status_label.pack(pady=(0, 8))

        # Make the whole frame clickable
        for widget in (self, self._icon_label, self._text_label, self._hint_label):
            widget.bind("<Button-1>", self._on_click)
            widget.bind("<Enter>", self._on_mouse_enter)
            widget.bind("<Leave>", self._on_mouse_leave)

    # ── Drag-and-Drop ────────────────────────────────────────────────────────
    def _register_dnd(self):
        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<DragEnter>>", self._on_drag_enter)
        self.dnd_bind("<<DragLeave>>", self._on_drag_leave)
        self.dnd_bind("<<Drop>>", self._on_drop)

    def _on_drag_enter(self, event):
        self.configure(border_color="#52b788", fg_color="#1a2a3a")
        self._text_label.configure(text=self._HOVER_TEXT, text_color="#52b788")
        self._icon_label.configure(text="📥")

    def _on_drag_leave(self, event):
        self._reset_appearance()

    def _on_drop(self, event):
        self._reset_appearance()
        raw = event.data.strip()
        # tkinterdnd2 may wrap paths in braces on some platforms
        path = raw.strip("{}")
        # Handle multiple dropped files — only first
        if "\n" in path:
            path = path.split("\n")[0].strip("{}")
        self.open_file(path)

    # ── Click to browse ──────────────────────────────────────────────────────
    def _on_click(self, event=None):
        path = filedialog.askopenfilename(title="Select a file")
        if path:
            self.open_file(path)

    # ── Mouse hover ──────────────────────────────────────────────────────────
    def _on_mouse_enter(self, event=None):
        self.configure(border_color="#40916c")

    def _on_mouse_leave(self, event=None):
        self.configure(border_color="#2d6a4f")

    # ── File opening ─────────────────────────────────────────────────────────
    def open_file(self, path: str):
        """Route a file path to the appropriate viewer (threaded to keep UI responsive)."""
        if not os.path.isfile(path):
            self._set_status(f"⚠  File not found: {os.path.basename(path)}", color="#fc8181")
            return

        self._set_status(f"Opening {os.path.basename(path)} …", color="#68d391")
        threading.Thread(
            target=self._dispatch,
            args=(path,),
            daemon=True,
        ).start()

    def _dispatch(self, path: str):
        """Run in background thread; viewer windows must be created on main thread."""
        try:
            route_file(path, parent=self.winfo_toplevel())
        except Exception as exc:
            self.after(0, self._set_status, f"⚠  {exc}", "#fc8181")
        else:
            self.after(0, self._set_status, f"✔  Opened: {os.path.basename(path)}", "#68d391")

    # ── Helpers ──────────────────────────────────────────────────────────────
    def _reset_appearance(self):
        self.configure(border_color="#2d6a4f", fg_color="#16213e")
        self._text_label.configure(text=self._IDLE_TEXT, text_color="#a8dadc")
        self._icon_label.configure(text="📁")
        self._status_label.configure(text="")  # Clear status message

    def _set_status(self, msg: str, color: str = "#68d391"):
        self._status_label.configure(text=msg, text_color=color)
        # Auto-reset after 3 seconds
        self.after(3000, self._reset_appearance)
