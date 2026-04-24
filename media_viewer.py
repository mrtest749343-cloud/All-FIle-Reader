"""
viewers/media_viewer.py — Audio/video player window.

Audio:  pygame.mixer  (pure Python, no extra system deps)
Video:  python-vlc    (optional; falls back to opening with system player)
"""

from __future__ import annotations

import os
import time
import threading
import tkinter as tk
import customtkinter as ctk

from base_viewer import BaseViewer
from media_handler import MediaHandler


class MediaViewer(BaseViewer):

    def __init__(self, master, path: str):
        super().__init__(master, path, viewer_type="audio" if MediaHandler.is_audio(path) else "video")
        self.geometry("620x400")

        self._is_audio = MediaHandler.is_audio(path)
        self._playing = False
        self._duration = 0.0
        self._start_time = 0.0
        self._paused_pos = 0.0
        self._mixer_ok = False
        self._seek_dragging = False

        self._build_info_panel()
        self._build_controls()
        self._build_progress()
        self._init_audio()

    # ── Info panel ───────────────────────────────────────────────────────────
    def _build_info_panel(self):
        panel = ctk.CTkFrame(self.body, fg_color="#141428", corner_radius=12)
        panel.pack(fill="x", padx=20, pady=(16, 8))

        icon = "🎵" if self._is_audio else "🎬"
        ctk.CTkLabel(panel, text=icon, font=ctk.CTkFont(size=40)).pack(pady=(16, 4))

        ctk.CTkLabel(
            panel,
            text=os.path.basename(self.path),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#e2e8f0",
            wraplength=520,
        ).pack()

        size = self._file_size()
        ext  = os.path.splitext(self.path)[1].upper()
        ctk.CTkLabel(
            panel,
            text=f"{ext}  •  {size}",
            font=ctk.CTkFont(size=11),
            text_color="#4a5568",
        ).pack(pady=(2, 14))

    # ── Progress bar ─────────────────────────────────────────────────────────
    def _build_progress(self):
        prog_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        prog_frame.pack(fill="x", padx=24, pady=(0, 4))

        self._time_label = ctk.CTkLabel(
            prog_frame, text="0:00", font=ctk.CTkFont(size=11), text_color="#6b7280", width=36
        )
        self._time_label.pack(side="left")

        self._seek_var = tk.DoubleVar(value=0)
        self._seek = ctk.CTkSlider(
            prog_frame,
            from_=0, to=100,
            variable=self._seek_var,
            command=self._on_seek_move,
            button_color="#52b788",
            progress_color="#2d6a4f",
        )
        self._seek.pack(side="left", fill="x", expand=True, padx=8)
        self._seek.bind("<ButtonPress-1>", self._on_seek_press)
        self._seek.bind("<ButtonRelease-1>", self._on_seek_release)

        self._dur_label = ctk.CTkLabel(
            prog_frame, text="0:00", font=ctk.CTkFont(size=11), text_color="#6b7280", width=36
        )
        self._dur_label.pack(side="left")

    # ── Controls ─────────────────────────────────────────────────────────────
    def _build_controls(self):
        ctrl = ctk.CTkFrame(self.body, fg_color="transparent")
        ctrl.pack(pady=8)

        self._play_btn = ctk.CTkButton(
            ctrl,
            text="▶  Play",
            width=110,
            height=40,
            corner_radius=20,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2d6a4f",
            hover_color="#40916c",
            command=self._toggle_play,
        )
        self._play_btn.pack(side="left", padx=8)

        ctk.CTkButton(
            ctrl,
            text="⏹  Stop",
            width=90,
            height=40,
            corner_radius=20,
            fg_color="#3d1515",
            hover_color="#6b2121",
            command=self._stop,
        ).pack(side="left", padx=8)

        # Volume
        vol_frame = ctk.CTkFrame(ctrl, fg_color="transparent")
        vol_frame.pack(side="left", padx=16)
        ctk.CTkLabel(vol_frame, text="🔊", font=ctk.CTkFont(size=16)).pack(side="left")
        self._vol_slider = ctk.CTkSlider(
            vol_frame,
            from_=0, to=1,
            width=100,
            command=self._set_volume,
            button_color="#52b788",
            progress_color="#2d6a4f",
        )
        self._vol_slider.set(0.8)
        self._vol_slider.pack(side="left", padx=6)

        # Status label
        self._status_var = tk.StringVar(value="Ready")
        ctk.CTkLabel(
            self.body,
            textvariable=self._status_var,
            font=ctk.CTkFont(size=11),
            text_color="#4a5568",
        ).pack(pady=(4, 0))

    # ── pygame audio ─────────────────────────────────────────────────────────
    def _init_audio(self):
        if not self._is_audio:
            self._handle_video()
            return

        def _load():
            try:
                import pygame  # type: ignore
                pygame.mixer.init()
                pygame.mixer.music.load(self.path)
                self._mixer_ok = True
                # Attempt to get duration via mutagen
                try:
                    from mutagen import File as MutagenFile  # type: ignore
                    info = MutagenFile(self.path)
                    if info is not None and hasattr(info, "info"):
                        self._duration = float(info.info.length)
                except Exception:
                    self._duration = 0.0
                self.after(0, self._update_duration_label)
                self.after(0, lambda: self._status_var.set("Ready — click Play"))
            except ImportError:
                self.after(0, lambda: self._status_var.set(
                    "⚠  pygame not installed.  pip install pygame"
                ))
            except Exception as exc:
                self.after(0, lambda: self._status_var.set(f"⚠  {exc}"))

        threading.Thread(target=_load, daemon=True).start()

    def _handle_video(self):
        """Try vlc; fall back to system open."""
        try:
            import vlc  # type: ignore  # noqa: F401
            self._status_var.set("python-vlc detected — opening video…")
            self._open_vlc()
        except ImportError:
            self._status_var.set("Opening with system player…")
            import subprocess, sys, platform
            plat = platform.system()
            try:
                if plat == "Windows":
                    os.startfile(self.path)  # type: ignore
                elif plat == "Darwin":
                    subprocess.Popen(["open", self.path])
                else:
                    subprocess.Popen(["xdg-open", self.path])
            except Exception as exc:
                self._status_var.set(f"⚠  {exc}")

    def _open_vlc(self):
        """Embed a vlc MediaPlayer into this window."""
        try:
            import vlc  # type: ignore
            self._vlc_instance = vlc.Instance()
            self._vlc_player  = self._vlc_instance.media_player_new()
            media = self._vlc_instance.media_new(self.path)
            self._vlc_player.set_media(media)

            # Embed into Tk frame
            embed = tk.Frame(self.body, bg="black")
            embed.pack(fill="both", expand=True, padx=8, pady=8)
            self.update()
            wid = embed.winfo_id()
            import platform
            if platform.system() == "Windows":
                self._vlc_player.set_hwnd(wid)
            elif platform.system() == "Darwin":
                self._vlc_player.set_nsobject(wid)
            else:
                self._vlc_player.set_xwindow(wid)

            self._vlc_player.play()
            self._playing = True
            self._play_btn.configure(text="⏸  Pause")
            self._status_var.set("Playing via VLC…")
        except Exception as exc:
            self._status_var.set(f"⚠  VLC error: {exc}")

    # ── Playback controls ────────────────────────────────────────────────────
    def _toggle_play(self):
        if not self._mixer_ok:
            return
        import pygame  # type: ignore
        if self._playing:
            pygame.mixer.music.pause()
            self._paused_pos += time.time() - self._start_time
            self._playing = False
            self._play_btn.configure(text="▶  Play")
            self._status_var.set("Paused")
        else:
            if self._paused_pos > 0:
                pygame.mixer.music.unpause()
            else:
                pygame.mixer.music.play()
                self._set_volume(self._vol_slider.get())
            self._start_time = time.time()
            self._playing = True
            self._play_btn.configure(text="⏸  Pause")
            self._status_var.set("Playing…")
            self._tick()

    def _stop(self):
        if not self._mixer_ok:
            return
        import pygame  # type: ignore
        pygame.mixer.music.stop()
        self._playing = False
        self._paused_pos = 0.0
        self._seek_var.set(0)
        self._play_btn.configure(text="▶  Play")
        self._time_label.configure(text="0:00")
        self._status_var.set("Stopped")

    def _set_volume(self, val):
        if self._mixer_ok:
            try:
                import pygame  # type: ignore
                pygame.mixer.music.set_volume(float(val))
            except Exception:
                pass

    # ── Seek ─────────────────────────────────────────────────────────────────
    def _on_seek_press(self, event):
        self._seek_dragging = True

    def _on_seek_move(self, val):
        if self._seek_dragging and self._duration > 0:
            secs = float(val) / 100.0 * self._duration
            self._time_label.configure(text=self._fmt(secs))

    def _on_seek_release(self, event):
        self._seek_dragging = False
        if not self._mixer_ok or self._duration == 0:
            return
        import pygame  # type: ignore
        pct = self._seek_var.get() / 100.0
        pos_secs = pct * self._duration
        pygame.mixer.music.play(start=pos_secs)
        self._paused_pos = pos_secs
        self._start_time = time.time()
        if not self._playing:
            pygame.mixer.music.pause()

    # ── Ticker ───────────────────────────────────────────────────────────────
    def _tick(self):
        if not self._playing:
            return
        elapsed = self._paused_pos + (time.time() - self._start_time)
        self._time_label.configure(text=self._fmt(elapsed))
        if self._duration > 0 and not self._seek_dragging:
            pct = min(elapsed / self._duration * 100, 100)
            self._seek_var.set(pct)
            if pct >= 100:
                self._stop()
                return
        self.after(500, self._tick)

    def _update_duration_label(self):
        self._dur_label.configure(text=self._fmt(self._duration))

    # ── Helpers ──────────────────────────────────────────────────────────────
    @staticmethod
    def _fmt(secs: float) -> str:
        secs = max(0, int(secs))
        m, s = divmod(secs, 60)
        return f"{m}:{s:02d}"

    def _file_size(self) -> str:
        size = os.path.getsize(self.path)
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def destroy(self):
        try:
            if self._mixer_ok:
                import pygame  # type: ignore
                pygame.mixer.music.stop()
        except Exception:
            pass
        super().destroy()
