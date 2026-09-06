"""Sanity-checks that configs/example.yaml stays valid as the action registry evolves."""
from pathlib import Path

import yaml

from automator.actions import available_actions

CONFIG_PATH = Path(__file__).resolve().parent.parent / "configs" / "example.yaml"


def _iter_steps(steps, macros):
    for step in steps:
        yield step
        if step.get("action") == "run_macro":
            yield from _iter_steps(macros.get(step["name"], []), macros)


def test_example_config_parses():
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    assert config["start_url"]
    assert "steps" in config


def test_example_config_uses_only_known_actions():
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    macros = config.get("macros", {})
    known = set(available_actions())

    all_steps = list(_iter_steps(config.get("steps", []), macros))
    for macro_steps in macros.values():
        all_steps.extend(macro_steps)

    for step in all_steps:
        assert step["action"] in known, f"Unknown action in example.yaml: {step['action']!r}"


def test_example_config_hotkey_bindings_reference_known_actions():
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    known = set(available_actions())

    for combo, binding in config.get("hotkeys", {}).items():
        if isinstance(binding, list):
            for step in binding:
                assert step["action"] in known, f"Unknown action in hotkey {combo!r}: {step['action']!r}"
        else:
            assert binding in ("pause", "quit"), f"Unrecognized hotkey binding for {combo!r}: {binding!r}"
