"""Filesystem layout for TWRAR's per-install runtime state.

User data (GUI settings, the disclaimer acknowledgment) lives in the
platform-standard per-user app directory so it survives repo/git updates:
  Windows: %APPDATA%\\TWRAR\\
  macOS:   ~/Library/Application Support/TWRAR/
  Linux:   ~/.local/share/TWRAR/ (or $XDG_DATA_HOME/TWRAR/)
"""

import os
import sys
from pathlib import Path

if sys.platform == "win32":
    _base = Path(os.environ.get("APPDATA", Path.home()))
elif sys.platform == "darwin":
    _base = Path.home() / "Library" / "Application Support"
else:
    _base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

USER_DATA_DIR = _base / "TWRAR"

CONFIGS_DIR = USER_DATA_DIR / "configs"
CONFIGS_DIR.mkdir(parents=True, exist_ok=True)

# Where bundled read-only app files (assets/, CHANGELOG.md, VERSION.md) live.
# Under a PyInstaller onefile build, __file__ resolves into the bootloader's
# temp extraction dir rather than reliably alongside the repo - sys._MEIPASS
# is the documented, reliable way to find bundled data there instead.
if getattr(sys, "frozen", False):
    APP_ROOT = Path(sys._MEIPASS)  # type: ignore[attr-defined]
else:
    APP_ROOT = Path(__file__).resolve().parent.parent
