"""Filesystem layout for Site Automator's per-install runtime state.

User data (GUI settings, the disclaimer acknowledgment) lives in the
platform-standard per-user app directory so it survives repo/git updates:
  Windows: %APPDATA%\\Automater\\
  Linux:   ~/.local/share/Automater/
"""

import os
from pathlib import Path

if os.name == "nt":
    _base = Path(os.environ.get("APPDATA", Path.home()))
else:
    _base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

USER_DATA_DIR = _base / "Automater"

CONFIGS_DIR = USER_DATA_DIR / "configs"
CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
