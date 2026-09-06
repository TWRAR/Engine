import json

import pytest

from automator.actions import (
    ActionError,
    ExecutionContext,
    available_actions,
    resolve_value,
    save_results,
)


def test_resolve_value_substitutes_env_var(monkeypatch):
    monkeypatch.setenv("AUTOMATER_TEST_SECRET", "hunter2")
    assert resolve_value("${env:AUTOMATER_TEST_SECRET}") == "hunter2"


def test_resolve_value_missing_env_var_becomes_empty(monkeypatch):
    monkeypatch.delenv("AUTOMATER_TEST_MISSING", raising=False)
    assert resolve_value("${env:AUTOMATER_TEST_MISSING}") == ""


def test_resolve_value_passes_through_non_strings():
    assert resolve_value(42) == 42
    assert resolve_value(None) is None
    assert resolve_value(True) is True


def test_resolve_value_embedded_in_larger_string(monkeypatch):
    monkeypatch.setenv("AUTOMATER_TEST_USER", "leo")
    assert resolve_value("user=${env:AUTOMATER_TEST_USER}!") == "user=leo!"


async def test_run_step_unknown_action_raises():
    ctx = ExecutionContext(page=None, macros={}, results={})
    with pytest.raises(ActionError, match="Unknown action"):
        await ctx.run_step({"action": "does_not_exist"})


async def test_run_step_resolves_env_vars_before_dispatch(monkeypatch):
    monkeypatch.setenv("AUTOMATER_TEST_VALUE", "resolved")
    seen = {}

    async def fake_handler(ctx, step):
        seen.update(step)

    from automator import actions

    monkeypatch.setitem(actions._REGISTRY, "fake", fake_handler)
    ctx = ExecutionContext(page=None, macros={}, results={})
    await ctx.run_step({"action": "fake", "value": "${env:AUTOMATER_TEST_VALUE}"})

    assert seen == {"value": "resolved"}


async def test_run_macro_unknown_raises():
    ctx = ExecutionContext(page=None, macros={"known": []}, results={})
    with pytest.raises(ActionError, match="Unknown macro"):
        await ctx.run_step({"action": "run_macro", "name": "missing"})


async def test_run_macro_runs_its_steps():
    calls = []

    async def fake_handler(ctx, step):
        calls.append(step["marker"])

    from automator import actions

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

    from automator import actions

    actions._REGISTRY["fake"] = fake_handler
    try:
        ctx = ExecutionContext(page=None, macros={}, results={})
        await ctx.run_step({"action": "repeat", "times": 3, "steps": [{"action": "fake"}]})
    finally:
        del actions._REGISTRY["fake"]

    assert calls == [1, 1, 1]


def test_available_actions_matches_registry():
    from automator import actions

    assert available_actions() == sorted(actions._REGISTRY.keys())
    assert "click" in available_actions()
    assert "run_macro" in available_actions()


def test_save_results_creates_parent_dir_and_writes_json(tmp_path):
    out_path = tmp_path / "nested" / "results.json"
    save_results({"prices": ["1", "2"]}, str(out_path))

    assert out_path.exists()
    assert json.loads(out_path.read_text(encoding="utf-8")) == {"prices": ["1", "2"]}
