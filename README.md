# Universal File Reader

A lightweight, modular desktop application for **reading any file** —
text documents, audio, video, archives, executables, and more.
Built with Python + CustomTkinter.

---

## File Structure

```
file_reader/
├── main.py                 ← entry point
├── requirements.txt
├── ui/
│   ├── drop_zone.py        ← drag-and-drop / click-to-select widget
│   └── history_bar.py      ← recent files strip
├── handlers/
│   ├── base_handler.py     ← abstract FileHandler base class
│   ├── router.py           ← routes file → correct handler
│   ├── text_handler.py     ← txt, pdf, docx, json, code…
│   ├── media_handler.py    ← mp3, wav, mp4, avi…
│   └── generic_handler.py  ← catch-all (zip, exe, bin…)
└── viewers/
    ├── base_viewer.py      ← shared Toplevel window base
    ├── text_viewer.py      ← scrollable read-only text
    ├── media_viewer.py     ← audio player + video fallback
    └── generic_viewer.py   ← metadata + hex preview
```

---

## Quick Start

### 1 — Clone / download

```bash
git clone <repo>
cd file_reader
```

### 2 — Create a virtual environment (recommended)

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate
```

### 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### 4 — Run

```bash
python main.py
```

---

## Features

| Format group | Examples | Viewer |
|---|---|---|
| Plain text / code | `.txt .py .js .md .csv .json .yaml` | Scrollable text with font size control |
| Documents | `.pdf .docx .rtf` | Extracted text viewer |
| Audio | `.mp3 .wav .ogg .flac .aac .m4a` | Built-in player (play/pause/seek/volume) |
| Video | `.mp4 .avi .mkv .mov` | System player (or VLC embedded if installed) |
| Everything else | `.zip .exe .bin` | Metadata panel + hex preview |

### Extra features
- 🌑 Dark mode by default
- 🕓 Recent files bar (persisted across sessions)
- ⚡ Lazy loading — heavy libraries only imported when needed
- 🛡 Graceful error handling (corrupted / unreadable files)
- 🔠 Font size controls in text viewer
- 🔁 Word-wrap toggle

---

## Optional: Embedded Video Playback

For embedded video (instead of opening system player):

1. Install [VLC media player](https://www.videolan.org/vlc/)
2. Install the Python binding:

```bash
pip install python-vlc
```

---

## Tested on

- Python 3.10 / 3.11 / 3.12
- Windows 10/11, macOS 13+, Ubuntu 22.04+
