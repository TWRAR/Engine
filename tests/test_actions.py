import json
from pathlib import Path

import pytest

from twrar.actions import (
    ActionError,
    ExecutionContext,
    available_actions,
    resolve_value,
    save_results,
)


def test_resolve_value_substitutes_env_var(monkeypatch):
    monkeypatch.setenv("TWRAR_TEST_SECRET", "hunter2")
    assert resolve_value("${env:TWRAR_TEST_SECRET}") == "hunter2"


def test_resolve_value_missing_env_var_becomes_empty(monkeypatch):
    monkeypatch.delenv("TWRAR_TEST_MISSING", raising=False)
    assert resolve_value("${env:TWRAR_TEST_MISSING}") == ""


def test_resolve_value_passes_through_non_strings():
    assert resolve_value(42) == 42
    assert resolve_value(None) is None
    assert resolve_value(True) is True


def test_resolve_value_embedded_in_larger_string(monkeypatch):
    monkeypatch.setenv("TWRAR_TEST_USER", "leo")
    assert resolve_value("user=${env:TWRAR_TEST_USER}!") == "user=leo!"


async def test_run_step_unknown_action_raises():
    ctx = ExecutionContext(page=None, macros={}, results={})
    with pytest.raises(ActionError, match="Unknown action"):
        await ctx.run_step({"action": "does_not_exist"})


async def test_run_step_resolves_env_vars_before_dispatch(monkeypatch):
    monkeypatch.setenv("TWRAR_TEST_VALUE", "resolved")
    seen = {}

    async def fake_handler(ctx, step):
        seen.update(step)

    from twrar import actions

    monkeypatch.setitem(actions._REGISTRY, "fake", fake_handler)
    ctx = ExecutionContext(page=None, macros={}, results={})
    await ctx.run_step({"action": "fake", "value": "${env:TWRAR_TEST_VALUE}"})

    assert seen == {"value": "resolved"}


async def test_run_macro_unknown_raises():
    ctx = ExecutionContext(page=None, macros={"known": []}, results={})
    with pytest.raises(ActionError, match="Unknown macro"):
        await ctx.run_step({"action": "run_macro", "name": "missing"})


async def test_run_macro_runs_its_steps():
    calls = []

    async def fake_handler(ctx, step):
        calls.append(step["marker"])

    from twrar import actions

    macros = {"greet": [{"action": "fake", "marker": "a"}, {"action": "fake", "marker": "b"}]}
    ctx = ExecutionContext(page=None, macros=macros, results={})
    actions._REGISTRY["fake"] = fake_handler
    try:
        await ctx.run_step({"action": "run_macro", "name": "greet"})
    finally:
        del actions._REGISTRY["fake"]

    assert calls == ["a", "b"]


async def test_repeat_runs_nested_steps_n_times():
    calls = []

    async def fake_handler(ctx, step):
        calls.append(1)

    from twrar import actions

    actions._REGISTRY["fake"] = fake_handler
    try:
        ctx = ExecutionContext(page=None, macros={}, results={})
        await ctx.run_step({"action": "repeat", "times": 3, "steps": [{"action": "fake"}]})
    finally:
        del actions._REGISTRY["fake"]

    assert calls == [1, 1, 1]


def test_available_actions_matches_registry():
    from twrar import actions

    assert available_actions() == sorted(actions._REGISTRY.keys())
    assert "click" in available_actions()
    assert "run_macro" in available_actions()


def test_save_results_creates_parent_dir_and_writes_json(tmp_path):
    out_path = tmp_path / "nested" / "results.json"
    save_results({"prices": ["1", "2"]}, str(out_path))

    assert out_path.exists()
    assert json.loads(out_path.read_text(encoding="utf-8")) == {"prices": ["1", "2"]}


# --- retry / continue_on_error / step_results / screenshots ----------------

async def test_run_step_records_a_passed_step_result():
    from twrar import actions

    async def fake_handler(ctx, step):
        pass

    actions._REGISTRY["fake"] = fake_handler
    try:
        ctx = ExecutionContext(page=None, macros={}, results={})
        await ctx.run_step({"action": "fake"})
    finally:
        del actions._REGISTRY["fake"]

    assert len(ctx.step_results) == 1
    result = ctx.step_results[0]
    assert result.index == 1
    assert result.action == "fake"
    assert result.status == "passed"
    assert result.attempts == 1
    assert result.error is None


async def test_run_step_retries_until_success():
    from twrar import actions

    calls = {"n": 0}

    async def flaky_handler(ctx, step):
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("not yet")

    actions._REGISTRY["flaky"] = flaky_handler
    try:
        ctx = ExecutionContext(page=None, macros={}, results={})
        await ctx.run_step({"action": "flaky", "retry": {"times": 3}})
    finally:
        del actions._REGISTRY["flaky"]

    assert calls["n"] == 3
    assert ctx.step_results[0].status == "passed"
    assert ctx.step_results[0].attempts == 3


async def test_run_step_raises_after_exhausting_retries():
    from twrar import actions

    async def always_fails(ctx, step):
        raise RuntimeError("nope")

    actions._REGISTRY["always_fails"] = always_fails
    try:
        ctx = ExecutionContext(page=None, macros={}, results={})
        with pytest.raises(RuntimeError, match="nope"):
            await ctx.run_step({"action": "always_fails", "retry": {"times": 2}})
    finally:
        del actions._REGISTRY["always_fails"]

    assert ctx.step_results[0].status == "failed"
    assert ctx.step_results[0].attempts == 2


async def test_continue_on_error_swallows_the_exception():
    from twrar import actions

    async def always_fails(ctx, step):
        raise RuntimeError("nope")

    actions._REGISTRY["always_fails"] = always_fails
    try:
        ctx = ExecutionContext(page=None, macros={}, results={})
        await ctx.run_step({"action": "always_fails", "continue_on_error": True})
    finally:
        del actions._REGISTRY["always_fails"]

    assert ctx.step_results[0].status == "continued"
    assert "nope" in ctx.step_results[0].error


async def test_on_step_result_hook_is_called():
    from twrar import actions

    async def fake_handler(ctx, step):
        pass

    actions._REGISTRY["fake"] = fake_handler
    seen = []
    try:
        ctx = ExecutionContext(page=None, macros={}, results={}, on_step_result=seen.append)
        await ctx.run_step({"action": "fake"})
    finally:
        del actions._REGISTRY["fake"]

    assert len(seen) == 1
    assert seen[0].status == "passed"


async def test_failure_screenshot_captured_when_screenshot_dir_set(tmp_path):
    from twrar import actions

    class FakePage:
        async def screenshot(self, path):
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_bytes(b"fake-png")

    async def always_fails(ctx, step):
        raise RuntimeError("boom")

    actions._REGISTRY["always_fails"] = always_fails
    try:
        ctx = ExecutionContext(page=FakePage(), macros={}, results={}, screenshot_dir=str(tmp_path))
        with pytest.raises(RuntimeError):
            await ctx.run_step({"action": "always_fails"})
    finally:
        del actions._REGISTRY["always_fails"]

    result = ctx.step_results[0]
    assert result.screenshot is not None
    assert Path(result.screenshot).exists()


async def test_no_screenshot_attempted_without_screenshot_dir():
    from twrar import actions

    async def always_fails(ctx, step):
        raise RuntimeError("boom")

    actions._REGISTRY["always_fails"] = always_fails
    try:
        ctx = ExecutionContext(page=None, macros={}, results={})
        with pytest.raises(RuntimeError):
            await ctx.run_step({"action": "always_fails"})
    finally:
        del actions._REGISTRY["always_fails"]

    assert ctx.step_results[0].screenshot is None
