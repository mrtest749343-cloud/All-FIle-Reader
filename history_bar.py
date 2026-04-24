"""
ui/history_bar.py — horizontal strip showing recently opened files.
"""

from __future__ import annotations

import os
import json
from typing import Callable

import customtkinter as ctk

_HISTORY_FILE = os.path.join(os.path.dirname(__file__), "..", ".file_history.json")
_MAX_HISTORY = 8


def load_history() -> list[str]:
    try:
        with open(_HISTORY_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return [p for p in data if os.path.isfile(p)]
    except Exception:
        return []


def save_history(paths: list[str]):
    try:
        with open(_HISTORY_FILE, "w", encoding="utf-8") as fh:
            json.dump(paths[:_MAX_HISTORY], fh)
    except Exception:
        pass


def add_to_history(path: str):
    history = load_history()
    history = [p for p in history if p != path]
    history.insert(0, path)
    save_history(history[:_MAX_HISTORY])


class HistoryBar(ctk.CTkFrame):
    """
    A thin horizontal bar showing the last N opened files as clickable chips.
    """

    def __init__(self, master, open_callback: Callable[[str], None], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._open_cb = open_callback
        self._build()

    def _build(self):
        # Clear existing widgets
        for w in self.winfo_children():
            w.destroy()

        history = load_history()
        if not history:
            ctk.CTkLabel(
                self,
                text="No recent files",
                font=ctk.CTkFont(size=11),
                text_color="#4a5568",
            ).pack(side="left")
            return

        ctk.CTkLabel(
            self,
            text="Recent:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#6b7280",
        ).pack(side="left", padx=(0, 6))

        for path in history:
            name = os.path.basename(path)
            btn = ctk.CTkButton(
                self,
                text=name,
                width=10,
                height=24,
                corner_radius=8,
                font=ctk.CTkFont(size=11),
                fg_color="#1e3a5f",
                hover_color="#2d6a4f",
                command=lambda p=path: self._open(p),
            )
            btn.pack(side="left", padx=3)

    def _open(self, path: str):
        self._open_cb(path)

    def refresh(self):
        self._build()
