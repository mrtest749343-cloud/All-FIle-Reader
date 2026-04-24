"""
handlers/media_handler.py — Handles audio and video files.
"""

from __future__ import annotations

import os

from base_handler import FileHandler

_AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac", ".aac", ".wma", ".m4a", ".opus"}
_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg"}

_MEDIA_EXTENSIONS = _AUDIO_EXTENSIONS | _VIDEO_EXTENSIONS


class MediaHandler(FileHandler):

    @staticmethod
    def can_handle(path: str) -> bool:
        return os.path.splitext(path)[1].lower() in _MEDIA_EXTENSIONS

    @staticmethod
    def is_audio(path: str) -> bool:
        return os.path.splitext(path)[1].lower() in _AUDIO_EXTENSIONS

    @staticmethod
    def is_video(path: str) -> bool:
        return os.path.splitext(path)[1].lower() in _VIDEO_EXTENSIONS

    def open_viewer(self, path: str, parent) -> None:
        from media_viewer import MediaViewer
        MediaViewer(parent, path)
