"""Checks GitHub for a newer Engine release than the one currently running.

Fully best-effort: any network failure, rate limit, or malformed response
is swallowed and treated as "no update found" rather than raised - this
must never block or crash the GUI, and there's no requirement to check
successfully (offline use is normal for this tool).
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Optional, TypedDict

LATEST_RELEASE_API = "https://api.github.com/repos/TWRAR/Engine/releases/latest"
RELEASES_URL = "https://github.com/TWRAR/Engine/releases"


class UpdateInfo(TypedDict):
    version: str
    url: str


def _parse_version(text: str) -> tuple[int, ...]:
    """"v3.10.2" / "3.10.2" -> (3, 10, 2). Non-numeric segments become 0
    rather than raising, so an unexpected tag format just compares low."""
    text = text.strip()
    if text[:1] in ("v", "V"):
        text = text[1:]
    parts = []
    for chunk in text.split("."):
        digits = "".join(ch for ch in chunk if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def check_for_update(current_version: str, timeout: float = 5.0) -> Optional[UpdateInfo]:
    """Returns the latest release's version/URL if it's newer than
    `current_version`, or None if already current (or the check failed).
    Runs a blocking network call - call this from a thread/executor, not
    directly on the GUI's event loop.
    """
    try:
        request = urllib.request.Request(
            LATEST_RELEASE_API,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "TWRAR-update-check",
            },
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.load(response)
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return None

    latest_tag = data.get("tag_name") or ""
    if not latest_tag:
        return None

    if _parse_version(latest_tag) > _parse_version(current_version):
        return {
            "version": latest_tag.lstrip("vV"),
            "url": data.get("html_url") or RELEASES_URL,
        }
    return None
