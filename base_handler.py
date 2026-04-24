"""
handlers/base_handler.py — Abstract base class for all file handlers.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod


class FileHandler(ABC):
    """
    Base class for all file type handlers.

    Subclasses must implement:
        • can_handle(path)  — quick check (no heavy imports)
        • open_viewer(path, parent) — create and show the viewer window
    """

    @staticmethod
    @abstractmethod
    def can_handle(path: str) -> bool:
        """Return True if this handler supports the given file path."""
        ...

    @abstractmethod
    def open_viewer(self, path: str, parent) -> None:
        """
        Open the appropriate viewer window for *path*.
        *parent* is the Tk root window (used to position the new window).
        """
        ...

    # ── Shared utilities ─────────────────────────────────────────────────────
    @staticmethod
    def file_ext(path: str) -> str:
        return os.path.splitext(path)[1].lower()

    @staticmethod
    def human_size(path: str) -> str:
        size = os.path.getsize(path)
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
