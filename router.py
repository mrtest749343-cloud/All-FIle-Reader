"""
handlers/router.py — Decides which handler to use for a given file.

Heavy imports (docx, pdfplumber, pygame…) are deferred inside each handler
so startup stays fast.
"""

from __future__ import annotations

import os

from text_handler import TextHandler
from media_handler import MediaHandler
from generic_handler import GenericHandler
from history_bar import add_to_history


# Ordered list of handlers — first match wins
_HANDLERS = [
    TextHandler(),
    MediaHandler(),
    GenericHandler(),   # catch-all — always last
]


def route_file(path: str, parent=None) -> None:
    """Open *path* in the appropriate viewer window."""
    path = os.path.normpath(path)

    # Update history (fire-and-forget; errors silently ignored)
    try:
        add_to_history(path)
        if parent is not None:
            # Refresh history bar on the main thread
            for widget in parent.winfo_children():
                if hasattr(widget, "history_bar"):
                    parent.after(0, widget.history_bar.refresh)
            if hasattr(parent, "history_bar"):
                parent.after(0, parent.history_bar.refresh)
    except Exception:
        pass

    for handler in _HANDLERS:
        if handler.can_handle(path):
            # Viewer windows must be created on the main thread
            if parent is not None:
                parent.after(0, handler.open_viewer, path, parent)
            else:
                handler.open_viewer(path, parent)
            return

    # Should never reach here because GenericHandler is catch-all
    raise RuntimeError(f"No handler found for: {path}")
