"""Persisted GUI settings (browser defaults, disclaimer acknowledgment).

Separate from the YAML automation configs under configs/ - those describe a
specific run and are the user's own project data (loaded/saved explicitly
via the GUI's Load/Save Config buttons); this file holds the GUI's own
preferences, local to this install, and is never meant to be committed or
shared.
"""
from __future__ import annotations

import json
from typing import Any

from automater.paths import CONFIGS_DIR

SETTINGS_PATH = CONFIGS_DIR / "settings.json"

# Single source of truth for defaults - every key the GUI reads from
# settings must have one here, so a partial/older settings.json on disk
# still gets filled in via _deep_merge().
DEFAULT_SETTINGS: dict[str, Any] = {
    "disclaimer_confirmed": False,
    "default_browser_channel": "default",
    "default_headless": False,
    "default_user_data_dir": "",
    "last_config_path": "",
}


def _deep_merge(defaults: dict, overrides: dict) -> dict:
    merged = dict(defaults)
    for key, value in overrides.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_settings() -> dict:
    """Load settings.json, creating it with DEFAULT_SETTINGS if it doesn't
    exist yet. Falls back to the in-memory defaults (without touching disk)
    if the file can't be read or written.
    """
    if not SETTINGS_PATH.exists():
        try:
            SETTINGS_PATH.write_text(json.dumps(DEFAULT_SETTINGS, indent=2), encoding="utf-8")
        except OSError:
            pass
        return dict(DEFAULT_SETTINGS)

    try:
        user_settings = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return dict(DEFAULT_SETTINGS)

    merged = _deep_merge(DEFAULT_SETTINGS, user_settings)
    if merged != user_settings:
        try:
            SETTINGS_PATH.write_text(json.dumps(merged, indent=2), encoding="utf-8")
        except OSError:
            pass
    return merged


def save_settings(settings: dict) -> None:
    try:
        SETTINGS_PATH.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    except OSError:
        pass


def confirm_disclaimer() -> None:
    """Patch disclaimer_confirmed=true into settings.json without touching any other field."""
    try:
        existing = json.loads(SETTINGS_PATH.read_text(encoding="utf-8")) if SETTINGS_PATH.exists() else {}
    except (OSError, ValueError):
        existing = {}
    existing["disclaimer_confirmed"] = True
    save_settings(existing)
