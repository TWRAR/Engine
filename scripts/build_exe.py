"""Builds standalone Windows executables with PyInstaller: Automater.exe
(the GUI) and AutomaterCLI.exe (the CLI).

Run with: python scripts/build_exe.py
Requires the 'build' extra: pip install -e ".[build]"

The exe bundles Python, Playwright's driver, PySide6, and every other
dependency - but NOT a browser. That's fine for the default/normal setup
(browser.channel: default|brave|chrome|edge|firefox, which launches the
user's own already-installed browser); only a config that leaves Playwright
to use its own bundled Chromium needs `playwright install chromium` run
once on the target machine first.
"""
from __future__ import annotations

from pathlib import Path

import PyInstaller.__main__

REPO_ROOT = Path(__file__).resolve().parent.parent
VERSION = (REPO_ROOT / "VERSION.md").read_text(encoding="utf-8").strip()
ICON = REPO_ROOT / "assets" / "icon.ico"
DIST_DIR = REPO_ROOT / "dist"
BUILD_DIR = REPO_ROOT / "build"

COMMON_ARGS = [
    "--onefile",
    "--noconfirm",
    f"--distpath={DIST_DIR}",
    f"--workpath={BUILD_DIR}",
    f"--specpath={BUILD_DIR}",
    "--collect-all=playwright",
    "--collect-all=keyboard",
    "--collect-all=qasync",
    f"--paths={REPO_ROOT}",
]


def build_gui() -> None:
    # The About tab and disclaimer dialog read assets/logo.png, CHANGELOG.md,
    # and VERSION.md at runtime via automater.paths.APP_ROOT (which resolves
    # to sys._MEIPASS in a frozen build) - bundle them as data so those
    # lookups succeed instead of silently no-op'ing (missing icon/logo/blank
    # changelog) in the packaged exe.
    PyInstaller.__main__.run([
        str(REPO_ROOT / "gui_main.py"),
        "--name=Automater",
        "--windowed",
        f"--icon={ICON}",
        f"--add-data={REPO_ROOT / 'assets'};assets",
        f"--add-data={REPO_ROOT / 'CHANGELOG.md'};.",
        f"--add-data={REPO_ROOT / 'VERSION.md'};.",
        *COMMON_ARGS,
    ])


def build_cli() -> None:
    PyInstaller.__main__.run([
        str(REPO_ROOT / "main.py"),
        "--name=AutomaterCLI",
        "--console",
        *COMMON_ARGS,
    ])


def main() -> None:
    print(f"Building Automater v{VERSION} standalone executables...")
    build_gui()
    build_cli()
    print(f"\nDone. Output in {DIST_DIR}:")
    print(f"  - Automater.exe     (GUI, double-click to run)")
    print(f"  - AutomaterCLI.exe  (CLI, run with --config <file.yaml>)")


if __name__ == "__main__":
    main()
