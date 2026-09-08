import sys

import pytest
import yaml

from automater import runner
from automater.actions import ExecutionContext


async def _make_ctx(monkeypatch, handler):
    from automater import actions

    monkeypatch.setitem(actions._REGISTRY, "fake", handler)
    return ExecutionContext(page=None, macros={}, results={})


async def test_execute_steps_runs_in_order(monkeypatch):
    calls = []

    async def fake_handler(ctx, step):
        calls.append(step.get("marker"))

    ctx = await _make_ctx(monkeypatch, fake_handler)
    steps = [{"action": "fake", "marker": "a"}, {"action": "fake", "marker": "b"}]

    await runner.execute_steps(ctx, steps)

    assert calls == ["a", "b"]


async def test_execute_steps_wraps_failure_with_step_context(monkeypatch):
    async def fake_handler(ctx, step):
        raise RuntimeError("boom")

    ctx = await _make_ctx(monkeypatch, fake_handler)
    steps = [{"action": "fake"}]

    with pytest.raises(RuntimeError, match=r"Step 1 \(fake\) failed: boom"):
        await runner.execute_steps(ctx, steps)


async def test_execute_steps_drains_pause_hotkey(monkeypatch):
    order = []

    async def fake_handler(ctx, step):
        order.append("ran")

    ctx = await _make_ctx(monkeypatch, fake_handler)
    queue: "__import__('asyncio').Queue" = __import__("asyncio").Queue()
    await queue.put({"combo": "f8", "binding": "pause"})
    await queue.put({"combo": "f8", "binding": "pause"})  # resume

    await runner.execute_steps(ctx, [{"action": "fake"}], queue)

    assert order == ["ran"]


async def test_execute_steps_quit_hotkey_stops_early(monkeypatch):
    async def fake_handler(ctx, step):
        pass

    ctx = await _make_ctx(monkeypatch, fake_handler)
    queue = __import__("asyncio").Queue()
    await queue.put({"combo": "f9", "binding": "quit"})

    await runner.execute_steps(ctx, [{"action": "fake"}], queue)

    assert ctx.step_results == []  # never reached the step


async def test_execute_steps_list_binding_runs_immediately(monkeypatch):
    order = []

    async def fake_handler(ctx, step):
        order.append(step.get("marker", "main"))

    ctx = await _make_ctx(monkeypatch, fake_handler)
    queue = __import__("asyncio").Queue()
    await queue.put({"combo": "f10", "binding": [{"action": "fake", "marker": "hotkey"}]})

    await runner.execute_steps(ctx, [{"action": "fake"}], queue)

    assert order == ["hotkey", "main"]


async def test_run_rejects_invalid_config_before_touching_playwright(tmp_path, capsys):
    config_path = tmp_path / "bad.yaml"
    config_path.write_text(yaml.safe_dump({"steps": [{"action": "does_not_exist"}]}), encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        await runner.run(str(config_path))

    assert exc_info.value.code == 1
    assert "unknown action" in capsys.readouterr().out


def test_main_validate_flag_on_valid_config(tmp_path, monkeypatch, capsys):
    config_path = tmp_path / "good.yaml"
    config_path.write_text(yaml.safe_dump({"steps": [{"action": "goto", "url": "https://example.com"}]}), encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["main.py", "--config", str(config_path), "--validate"])
    runner.main()

    assert "is valid" in capsys.readouterr().out


def test_main_validate_flag_on_invalid_config(tmp_path, monkeypatch, capsys):
    config_path = tmp_path / "bad.yaml"
    config_path.write_text(yaml.safe_dump({"steps": [{"action": "nope"}]}), encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["main.py", "--config", str(config_path), "--validate"])
    with pytest.raises(SystemExit) as exc_info:
        runner.main()

    assert exc_info.value.code == 1
    assert "unknown action" in capsys.readouterr().out
