"""Action registry: every step type the runner can execute.

Steps are plain dicts (usually loaded from YAML) with an "action" key.
New action types are added by writing a small async function and
decorating it with @action("name") - the runner never needs to change.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
from pathlib import Path
from typing import Any, Awaitable, Callable

ENV_PATTERN = re.compile(r"\$\{env:([A-Za-z_][A-Za-z0-9_]*)\}")


def resolve_value(value: Any) -> Any:
    """Substitutes ${env:VAR_NAME} in string values with the real env var.

    Keeps secrets (passwords, tokens) out of config files committed to git.
    """
    if isinstance(value, str):
        return ENV_PATTERN.sub(lambda m: os.environ.get(m.group(1), ""), value)
    return value


class ActionError(RuntimeError):
    pass


class ExecutionContext:
    def __init__(
        self,
        page: Any,
        macros: dict[str, list[dict]],
        results: dict[str, Any],
        default_delay_ms: int = 0,
    ):
        self.page = page
        self.macros = macros
        self.results = results
        self.default_delay_ms = default_delay_ms

    async def run_steps(self, steps: list[dict]) -> None:
        for step in steps:
            await self.run_step(step)

    async def run_step(self, step: dict) -> None:
        action_name = step["action"]
        handler = _REGISTRY.get(action_name)
        if handler is None:
            raise ActionError(
                f"Unknown action: {action_name!r}. "
                f"Available actions: {', '.join(sorted(_REGISTRY))}"
            )
        skip_keys = ("action", "delay_before", "delay_after")
        resolved = {k: resolve_value(v) for k, v in step.items() if k not in skip_keys}

        delay_before = step.get("delay_before", 0)
        if delay_before:
            await asyncio.sleep(delay_before / 1000)

        await handler(self, resolved)

        delay_after = step.get("delay_after", self.default_delay_ms)
        if delay_after:
            await asyncio.sleep(delay_after / 1000)


ActionHandler = Callable[[ExecutionContext, dict], Awaitable[None]]
_REGISTRY: dict[str, ActionHandler] = {}


def action(name: str) -> Callable[[ActionHandler], ActionHandler]:
    def decorator(fn: ActionHandler) -> ActionHandler:
        _REGISTRY[name] = fn
        return fn

    return decorator


def _timeout(step: dict) -> int:
    return step.get("timeout", 30000)


# --- Navigation -------------------------------------------------------

@action("goto")
async def _goto(ctx: ExecutionContext, step: dict) -> None:
    await ctx.page.goto(step["url"], wait_until=step.get("wait_until", "load"))


@action("reload")
async def _reload(ctx: ExecutionContext, step: dict) -> None:
    await ctx.page.reload(wait_until=step.get("wait_until", "load"))


@action("go_back")
async def _go_back(ctx: ExecutionContext, step: dict) -> None:
    await ctx.page.go_back(wait_until=step.get("wait_until", "load"))


@action("go_forward")
async def _go_forward(ctx: ExecutionContext, step: dict) -> None:
    await ctx.page.go_forward(wait_until=step.get("wait_until", "load"))


# --- Mouse / pointer ----------------------------------------------------

@action("click")
async def _click(ctx: ExecutionContext, step: dict) -> None:
    await ctx.page.click(
        step["selector"],
        timeout=_timeout(step),
        button=step.get("button", "left"),
        click_count=step.get("click_count", 1),
        modifiers=step.get("modifiers"),
        force=step.get("force", False),
    )


@action("dblclick")
async def _dblclick(ctx: ExecutionContext, step: dict) -> None:
    await ctx.page.dblclick(step["selector"], timeout=_timeout(step))


@action("click_coords")
async def _click_coords(ctx: ExecutionContext, step: dict) -> None:
    """Clicks at literal viewport coordinates, for sites with no stable selector."""
    await ctx.page.mouse.click(
        step["x"], step["y"],
        button=step.get("button", "left"),
        click_count=step.get("click_count", 1),
    )


@action("hover")
async def _hover(ctx: ExecutionContext, step: dict) -> None:
    await ctx.page.hover(step["selector"], timeout=_timeout(step))


@action("drag_and_drop")
async def _drag_and_drop(ctx: ExecutionContext, step: dict) -> None:
    await ctx.page.drag_and_drop(step["source"], step["target"], timeout=_timeout(step))


@action("scroll")
async def _scroll(ctx: ExecutionContext, step: dict) -> None:
    if step.get("selector"):
        await ctx.page.locator(step["selector"]).scroll_into_view_if_needed(timeout=_timeout(step))
    else:
        await ctx.page.mouse.wheel(step.get("delta_x", 0), step.get("delta_y", 500))


# --- Keyboard / forms ----------------------------------------------------

@action("fill")
async def _fill(ctx: ExecutionContext, step: dict) -> None:
    await ctx.page.fill(step["selector"], str(step["value"]), timeout=_timeout(step))


@action("type")
async def _type(ctx: ExecutionContext, step: dict) -> None:
    """Simulates real keystrokes (as opposed to `fill`, which sets the value directly)."""
    locator = ctx.page.locator(step["selector"])
    await locator.press_sequentially(str(step["value"]), delay=step.get("delay", 50))


@action("press")
async def _press(ctx: ExecutionContext, step: dict) -> None:
    """Sends a key/combo, e.g. "Control+Shift+K", either page-wide or to one element."""
    selector = step.get("selector")
    if selector:
        await ctx.page.press(selector, step["keys"], timeout=_timeout(step))
    else:
        await ctx.page.keyboard.press(step["keys"])


@action("check")
async def _check(ctx: ExecutionContext, step: dict) -> None:
    await ctx.page.check(step["selector"], timeout=_timeout(step))


@action("uncheck")
async def _uncheck(ctx: ExecutionContext, step: dict) -> None:
    await ctx.page.uncheck(step["selector"], timeout=_timeout(step))


@action("select_option")
async def _select_option(ctx: ExecutionContext, step: dict) -> None:
    await ctx.page.select_option(step["selector"], step["value"], timeout=_timeout(step))


@action("upload_file")
async def _upload_file(ctx: ExecutionContext, step: dict) -> None:
    await ctx.page.set_input_files(step["selector"], step["path"])


# --- Waiting --------------------------------------------------------------

@action("wait_for_selector")
async def _wait_for_selector(ctx: ExecutionContext, step: dict) -> None:
    await ctx.page.wait_for_selector(
        step["selector"], timeout=_timeout(step), state=step.get("state", "visible")
    )


@action("wait_for_url")
async def _wait_for_url(ctx: ExecutionContext, step: dict) -> None:
    await ctx.page.wait_for_url(step["url"], timeout=_timeout(step))


@action("wait_for_load_state")
async def _wait_for_load_state(ctx: ExecutionContext, step: dict) -> None:
    await ctx.page.wait_for_load_state(step.get("state", "load"), timeout=_timeout(step))


@action("sleep")
async def _sleep(ctx: ExecutionContext, step: dict) -> None:
    await asyncio.sleep(step["seconds"])


# --- Capture / extraction --------------------------------------------------

@action("screenshot")
async def _screenshot(ctx: ExecutionContext, step: dict) -> None:
    path = Path(step["path"])
    path.parent.mkdir(parents=True, exist_ok=True)
    selector = step.get("selector")
    if selector:
        await ctx.page.locator(selector).screenshot(path=str(path))
    else:
        await ctx.page.screenshot(path=str(path), full_page=step.get("full_page", True))


@action("scrape")
async def _scrape(ctx: ExecutionContext, step: dict) -> None:
    selector = step["selector"]
    attribute = step.get("attribute", "text")
    multiple = step.get("multiple", False)
    locator = ctx.page.locator(selector)

    async def read_one(loc: Any) -> Any:
        if attribute == "text":
            return (await loc.text_content() or "").strip()
        if attribute == "html":
            return await loc.inner_html()
        return await loc.get_attribute(attribute)

    if multiple:
        count = await locator.count()
        values = [await read_one(locator.nth(i)) for i in range(count)]
    else:
        values = await read_one(locator.first)

    ctx.results[step["save_as"]] = values


@action("evaluate")
async def _evaluate(ctx: ExecutionContext, step: dict) -> None:
    """Escape hatch: runs arbitrary JS in the page for whatever a site needs."""
    result = await ctx.page.evaluate(step["script"], step.get("arg"))
    if step.get("save_as"):
        ctx.results[step["save_as"]] = result


# --- QA / regression assertions --------------------------------------------

@action("assert")
async def _assert(ctx: ExecutionContext, step: dict) -> None:
    assertion = step["type"]
    selector = step.get("selector")
    locator = ctx.page.locator(selector) if selector else None

    if assertion == "visible":
        await locator.wait_for(state="visible", timeout=_timeout(step))
    elif assertion == "hidden":
        await locator.wait_for(state="hidden", timeout=_timeout(step))
    elif assertion == "text_equals":
        actual = (await locator.text_content() or "").strip()
        if actual != str(step["value"]):
            raise ActionError(f"assert text_equals failed: expected {step['value']!r}, got {actual!r}")
    elif assertion == "text_contains":
        actual = (await locator.text_content() or "").strip()
        if str(step["value"]) not in actual:
            raise ActionError(f"assert text_contains failed: {step['value']!r} not in {actual!r}")
    elif assertion == "url_equals":
        if ctx.page.url != step["value"]:
            raise ActionError(f"assert url_equals failed: expected {step['value']!r}, got {ctx.page.url!r}")
    elif assertion == "url_contains":
        if step["value"] not in ctx.page.url:
            raise ActionError(f"assert url_contains failed: {step['value']!r} not in {ctx.page.url!r}")
    elif assertion == "count_equals":
        count = await locator.count()
        if count != step["value"]:
            raise ActionError(f"assert count_equals failed: expected {step['value']}, got {count}")
    else:
        raise ActionError(f"Unknown assert type: {assertion}")


# --- Control flow / composition --------------------------------------------

@action("log")
async def _log(ctx: ExecutionContext, step: dict) -> None:
    print(f"[log] {step.get('message', '')}")


@action("repeat")
async def _repeat(ctx: ExecutionContext, step: dict) -> None:
    for _ in range(step["times"]):
        await ctx.run_steps(step.get("steps", []))


@action("run_macro")
async def _run_macro(ctx: ExecutionContext, step: dict) -> None:
    name = step["name"]
    macro_steps = ctx.macros.get(name)
    if macro_steps is None:
        raise ActionError(f"Unknown macro: {name!r}. Defined macros: {', '.join(sorted(ctx.macros))}")
    await ctx.run_steps(macro_steps)


def available_actions() -> list[str]:
    return sorted(_REGISTRY.keys())


def save_results(results: dict, path: str) -> None:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
