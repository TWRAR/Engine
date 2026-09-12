"""Builds a standalone TWRAR executable with PyInstaller, for whatever
platform this is run on.

Run with: python scripts/build_release_files.py
Installs its own dependencies (requirements.txt + PyInstaller) first, no
separate build.bat/build.sh wrapper or manual `pip install` needed.

PyInstaller can't cross-compile - run this on each platform (Windows,
macOS, Linux) you want a native build for; that's also what the Release
GitHub Actions workflow does, once per OS runner.

The exe/binary bundles Python, Playwright's driver, PySide6, and every
other dependency - but NOT a browser. That's fine for the default/normal
setup (browser.channel: default|brave|chrome|edge|firefox, which launches
the user's own already-installed browser); only a config that leaves
Playwright to use its own bundled Chromium needs
`playwright install chromium` run once on the target machine first.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"

REPO_ROOT = Path(__file__).resolve().parent.parent
VERSION = (REPO_ROOT / "VERSION.md").read_text(encoding="utf-8").strip()
DIST_DIR = REPO_ROOT / "dist"
BUILD_DIR = REPO_ROOT / "build"

_DATA_SEP = ";" if IS_WINDOWS else ":"


def _add_data(src: Path, dest: str) -> str:
    return f"--add-data={src}{_DATA_SEP}{dest}"


def _icon_args() -> list[str]:
    if IS_WINDOWS:
        icon = REPO_ROOT / "assets" / "icon.ico"
    elif IS_MACOS:
        icon = REPO_ROOT / "assets" / "icon.icns"
    else:
        # PyInstaller doesn't support icon embedding for plain Linux/ELF
        # binaries - nothing useful to pass here.
        return []
    return [f"--icon={icon}"] if icon.is_file() else []


COMMON_ARGS = [
    "--onefile",
    "--noconfirm",
    f"--distpath={DIST_DIR}",
    f"--workpath={BUILD_DIR}",
    f"--specpath={BUILD_DIR}",
    "--collect-all=playwright",
    "--collect-all=qasync",
    f"--paths={REPO_ROOT}",
]


def ensure_dependencies() -> None:
    # No more build.bat/build.sh wrapper to install these first - this
    # script is now run directly (`python scripts/build_release_files.py`),
    # so it installs its own runtime + build dependencies before importing
    # PyInstaller.
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-r", str(REPO_ROOT / "requirements.txt"), "-q"]
    )
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "-q"])


def build_gui() -> None:
    import PyInstaller.__main__

    # The About tab and disclaimer dialog read assets/logo.png, CHANGELOG.md,
    # and VERSION.md at runtime via src.paths.APP_ROOT (which resolves
    # to sys._MEIPASS in a frozen build) - bundle them as data so those
    # lookups succeed instead of silently no-op'ing (missing icon/logo/blank
    # changelog) in the packaged exe.
    PyInstaller.__main__.run([
        str(REPO_ROOT / "gui.py"),
        "--name=TWRAR",
        "--windowed",
        *_icon_args(),
        _add_data(REPO_ROOT / "assets", "assets"),
        _add_data(REPO_ROOT / "CHANGELOG.md", "."),
        _add_data(REPO_ROOT / "VERSION.md", "."),
        *COMMON_ARGS,
    ])


def main() -> None:
    print(f"Building TWRAR v{VERSION} standalone executable for {sys.platform}...")
    print("Installing build dependencies...")
    ensure_dependencies()
    build_gui()
    print(f"\nDone. Output in {DIST_DIR}:")
    print("  - TWRAR  (double-click to run - .exe on Windows, .app on macOS)")


if __name__ == "__main__":
    main()
