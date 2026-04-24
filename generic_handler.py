"""
handlers/generic_handler.py — Catch-all handler for any unrecognised file type.
Shows metadata and a hex preview.
"""

from __future__ import annotations

from base_handler import FileHandler


class GenericHandler(FileHandler):

    @staticmethod
    def can_handle(path: str) -> bool:
        return True  # always matches — must be last in router list

    def open_viewer(self, path: str, parent) -> None:
        from generic_viewer import GenericViewer
        GenericViewer(parent, path)
