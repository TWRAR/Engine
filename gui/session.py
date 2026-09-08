"""Owns the live Playwright browser: launching, recording, and playback.

Runs entirely on the Qt/asyncio event loop provided by qasync, so callbacks
from Playwright and signal emission to widgets can happen directly - no
manual cross-thread bridging needed.
"""
from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Optional

from PySide6.QtCore import QObject, Signal
from playwright.async_api import Frame, Page, async_playwright

from automater.actions import ExecutionContext
from automater.browser import launch_context
from gui.recorder_js import RECORDER_JS

_NAV_QUIET_WINDOW = 0.7  # seconds; navigations sooner than this after an
# action are assumed to be that action's own effect, not a separate step.


class BrowserSession(QObject):
    step_recorded = Signal(dict)
    log = Signal(str)
    browser_started = Signal()
    browser_stopped = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.playwright = None
        self.context = None
        self.page: Optional[Page] = None
        self.recording = False
        self._last_action_time = 0.0

    @property
    def is_running(self) -> bool:
        return self.page is not None

    async def start(self, browser_cfg: dict, user_data_dir: str, start_url: str | None) -> None:
        self.playwright = await async_playwright().start()
        self.context = await launch_context(self.playwright, browser_cfg, user_data_dir)
        self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()

        await self.context.expose_binding("__record_event", self._on_record_event)
        await self.context.add_init_script(RECORDER_JS)

        if start_url:
            await self.page.goto(start_url)

        self.log.emit("Browser started.")
        self.browser_started.emit()

    async def stop(self) -> None:
        self.stop_recording()
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()
        self.playwright = None
        self.context = None
        self.page = None
        self.log.emit("Browser stopped.")
        self.browser_stopped.emit()

    def start_recording(self) -> None:
        if not self.page:
            return
        self.recording = True
        self._last_action_time = time.monotonic()
        self.page.on("framenavigated", self._on_navigated)
        self.log.emit("Recording started.")

    def stop_recording(self) -> None:
        if self.recording and self.page:
            try:
                self.page.remove_listener("framenavigated", self._on_navigated)
            except Exception:
                pass
        if self.recording:
            self.log.emit("Recording stopped.")
        self.recording = False

    async def _on_record_event(self, source: Any, payload_json: str) -> None:
        self._last_action_time = time.monotonic()
        if not self.recording:
            return
        data = json.loads(payload_json)
        step = self._to_step(data)
        if step:
            self.step_recorded.emit(step)

    def _on_navigated(self, frame: Frame) -> None:
        if not self.page or frame != self.page.main_frame:
            return
        if not self.recording:
            return
        if time.monotonic() - self._last_action_time < _NAV_QUIET_WINDOW:
            return
        self.step_recorded.emit({"action": "goto", "url": frame.url})

    @staticmethod
    def _to_step(data: dict) -> Optional[dict]:
        t = data.get("type")
        selector = data.get("selector")

        if t == "click":
            step: dict[str, Any] = {"action": "click", "selector": selector}
            modifiers = data.get("modifiers") or []
            if modifiers:
                step["modifiers"] = modifiers
            return step
        if t == "fill":
            return {"action": "fill", "selector": selector, "value": data.get("value", "")}
        if t == "check":
            return {"action": "check" if data.get("checked") else "uncheck", "selector": selector}
        if t == "select_option":
            return {"action": "select_option", "selector": selector, "value": data.get("value", "")}
        if t == "press":
            return {"action": "press", "selector": selector, "keys": data.get("keys")}
        return None


class PlaybackController(QObject):
    step_started = Signal(int, str)
    step_finished = Signal(int, str)
    step_failed = Signal(int, str, str)
    finished = Signal(bool)  # True if stopped early

    def __init__(self, ctx: ExecutionContext) -> None:
        super().__init__()
        self.ctx = ctx
        self._pause_event = asyncio.Event()
        self._pause_event.set()
        self._stop_requested = False

    def pause(self) -> None:
        self._pause_event.clear()

    def resume(self) -> None:
        self._pause_event.set()

    def stop(self) -> None:
        self._stop_requested = True
        self._pause_event.set()

    async def run(self, steps: list[dict]) -> None:
        stopped_early = False
        for i, step in enumerate(steps):
            await self._pause_event.wait()
            if self._stop_requested:
                stopped_early = True
                break
            action_name = step.get("action", "?")
            self.step_started.emit(i, action_name)
            try:
                await self.ctx.run_step(step)
            except Exception as exc:
                self.step_failed.emit(i, action_name, str(exc))
                stopped_early = True
                break
            self.step_finished.emit(i, action_name)
        self.finished.emit(stopped_early)
