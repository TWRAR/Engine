"""Browser launching: defaults to the user's actual default browser, via a
persistent Playwright context. Brave/Chrome/Edge/Firefox all supported.
"""
from __future__ import annotations

import shutil
import winreg
from pathlib import Path
from typing import Any, Optional

from playwright.async_api import BrowserContext, Playwright

BRAVE_PATHS = [
    r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
]
CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]
EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]
FIREFOX_PATHS = [
    r"C:\Program Files\Mozilla Firefox\firefox.exe",
    r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
]

# Maps the registered default-browser ProgId (HKCU UserChoice) to a
# (playwright browser type, candidate install paths) pair.
_PROGID_MAP: list[tuple[str, tuple[str, list[str]]]] = [
    ("BraveHTML", ("chromium", BRAVE_PATHS)),
    ("ChromeHTML", ("chromium", CHROME_PATHS)),
    ("MSEdgeHTM", ("chromium", EDGE_PATHS)),
    ("FirefoxURL", ("firefox", FIREFOX_PATHS)),
]


def _find_first(paths: list[str], which_name: Optional[str] = None) -> Optional[str]:
    for path in paths:
        if Path(path).exists():
            return path
    if which_name:
        return shutil.which(which_name)
    return None


def find_brave_executable() -> Optional[str]:
    return _find_first(BRAVE_PATHS, "brave")


def find_chrome_executable() -> Optional[str]:
    return _find_first(CHROME_PATHS, "chrome")


def find_edge_executable() -> Optional[str]:
    return _find_first(EDGE_PATHS, "msedge")


def find_firefox_executable() -> Optional[str]:
    return _find_first(FIREFOX_PATHS, "firefox")


def detect_default_browser() -> tuple[str, Optional[str]]:
    """Reads the Windows default-browser registration and resolves it to
    (playwright browser type, executable path). Falls back to Brave, then
    Playwright's own bundled Chromium, if detection fails.
    """
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\https\UserChoice",
        ) as key:
            prog_id, _ = winreg.QueryValueEx(key, "ProgId")
    except OSError:
        return "chromium", find_brave_executable()

    for prefix, (browser_type, paths) in _PROGID_MAP:
        if prog_id.startswith(prefix):
            return browser_type, _find_first(paths)

    # Unrecognized default (e.g. Opera, Vivaldi) - fall back to Brave/bundled Chromium.
    return "chromium", find_brave_executable()


_CHANNEL_RESOLVERS = {
    "brave": lambda: ("chromium", find_brave_executable()),
    "chrome": lambda: ("chromium", find_chrome_executable()),
    "edge": lambda: ("chromium", find_edge_executable()),
    "firefox": lambda: ("firefox", find_firefox_executable()),
    "default": detect_default_browser,
}


async def launch_context(playwright: Playwright, browser_cfg: dict, user_data_dir: str) -> BrowserContext:
    executable_path = browser_cfg.get("executable_path")
    browser_type_name = browser_cfg.get("browser_type")  # explicit override, rarely needed

    if not executable_path:
        channel = browser_cfg.get("channel", "default")
        resolver = _CHANNEL_RESOLVERS.get(channel)
        if resolver is None:
            raise RuntimeError(
                f"Unknown browser.channel: {channel!r}. "
                f"Use one of {sorted(_CHANNEL_RESOLVERS)}, or set browser.executable_path directly."
            )
        resolved_type, executable_path = resolver()
        browser_type_name = browser_type_name or resolved_type
        if not executable_path:
            raise RuntimeError(
                f"Could not find an executable for channel {channel!r} on this machine. "
                "Set browser.executable_path explicitly in the config."
            )

    browser_type_name = browser_type_name or "chromium"
    browser_type = getattr(playwright, browser_type_name)

    launch_args: list[str] = list(browser_cfg.get("args", []))
    extension_path = browser_cfg.get("load_extension")
    if extension_path:
        if browser_type_name != "chromium":
            raise RuntimeError("load_extension is only supported for Chromium-based browsers.")
        launch_args += [
            f"--disable-extensions-except={extension_path}",
            f"--load-extension={extension_path}",
        ]

    viewport = browser_cfg.get("viewport") or {"width": 1440, "height": 900}

    kwargs: dict[str, Any] = dict(
        user_data_dir=user_data_dir,
        headless=browser_cfg.get("headless", False),
        viewport=viewport,
        args=launch_args,
        executable_path=executable_path,
    )

    return await browser_type.launch_persistent_context(**kwargs)
