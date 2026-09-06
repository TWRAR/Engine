"""Orchestrator: loads a YAML config, drives the browser, listens for hotkeys."""
from __future__ import annotations

import argparse
import asyncio
import tempfile
from pathlib import Path
from typing import Any

import yaml
from playwright.async_api import async_playwright

from automator.actions import ExecutionContext, save_results
from automator.browser import launch_context
from automator.hotkeys import HotkeyListener


async def _drain_hotkeys(ctx: ExecutionContext, queue: "asyncio.Queue[dict[str, Any]]", paused: bool) -> bool:
    while not queue.empty():
        event = queue.get_nowait()
        combo, binding = event["combo"], event["binding"]

        if binding == "pause":
            paused = not paused
            print(f"[hotkey:{combo}] {'paused' if paused else 'resumed'}")
        elif binding == "quit":
            print(f"[hotkey:{combo}] quit requested")
            raise SystemExit(0)
        elif isinstance(binding, list):
            print(f"[hotkey:{combo}] running {len(binding)} step(s)")
            await ctx.run_steps(binding)
        else:
            print(f"[hotkey:{combo}] ignoring unrecognized binding: {binding!r}")

    return paused


async def execute_steps(
    ctx: ExecutionContext,
    steps: list[dict],
    hotkey_queue: "asyncio.Queue[dict[str, Any]] | None" = None,
) -> None:
    paused = False
    i = 0
    while i < len(steps):
        if hotkey_queue is not None:
            try:
                paused = await _drain_hotkeys(ctx, hotkey_queue, paused)
            except SystemExit:
                return

        if paused:
            await asyncio.sleep(0.1)
            continue

        step = steps[i]
        print(f"[step {i + 1}/{len(steps)}] {step['action']}")
        try:
            await ctx.run_step(step)
        except Exception as exc:
            raise RuntimeError(f"Step {i + 1} ({step['action']}) failed: {exc}") from exc
        i += 1


async def run(config_path: str) -> None:
    config = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))

    browser_cfg = config.get("browser", {})
    user_data_dir = config.get("user_data_dir") or tempfile.mkdtemp(prefix="automator-profile-")
    macros = config.get("macros", {})
    default_delay_ms = config.get("default_delay_ms", 0)

    results: dict[str, Any] = {}
    hotkey_queue: asyncio.Queue = asyncio.Queue()
    loop = asyncio.get_event_loop()

    listener = None
    hotkeys_cfg = config.get("hotkeys")

    async with async_playwright() as playwright:
        context = await launch_context(playwright, browser_cfg, user_data_dir)
        page = context.pages[0] if context.pages else await context.new_page()
        ctx = ExecutionContext(page=page, macros=macros, results=results, default_delay_ms=default_delay_ms)

        if hotkeys_cfg:
            listener = HotkeyListener(loop, hotkey_queue)
            listener.register(hotkeys_cfg)
            print(f"Hotkeys active: {list(hotkeys_cfg.keys())}")

        start_url = config.get("start_url")
        if start_url:
            await page.goto(start_url)

        try:
            await execute_steps(ctx, config.get("steps", []), hotkey_queue)
        finally:
            output_cfg = config.get("output", {})
            if output_cfg.get("results_file"):
                save_results(results, output_cfg["results_file"])
                print(f"Results saved to {output_cfg['results_file']}")
            if listener:
                listener.stop()
            await context.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Stux.Group site QA/regression + scraping automator")
    parser.add_argument("--config", required=True, help="Path to a YAML config file")
    args = parser.parse_args()
    asyncio.run(run(args.config))


if __name__ == "__main__":
    main()
