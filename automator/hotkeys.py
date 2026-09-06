"""Global hotkey listener: maps real keyboard presses to control signals or step lists.

Runs system-wide (via the `keyboard` package's low-level hook) so hotkeys work
even while the browser window has focus. Callbacks fire on keyboard's internal
hook thread, so events are handed to the asyncio loop with call_soon_threadsafe.
"""
from __future__ import annotations

import asyncio
from typing import Any

import keyboard


class HotkeyListener:
    def __init__(self, loop: asyncio.AbstractEventLoop, queue: "asyncio.Queue[dict[str, Any]]"):
        self._loop = loop
        self._queue = queue
        self._registered: list[str] = []

    def register(self, hotkeys: dict[str, Any]) -> None:
        for combo, binding in hotkeys.items():
            keyboard.add_hotkey(combo, self._make_callback(combo, binding))
            self._registered.append(combo)

    def _make_callback(self, combo: str, binding: Any):
        def callback() -> None:
            self._loop.call_soon_threadsafe(
                self._queue.put_nowait, {"combo": combo, "binding": binding}
            )

        return callback

    def stop(self) -> None:
        for combo in self._registered:
            try:
                keyboard.remove_hotkey(combo)
            except KeyError:
                pass
        self._registered.clear()
