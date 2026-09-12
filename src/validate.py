"""Config pre-flight validation: catches unknown actions, missing required
fields, and dangling macro references before a browser is ever launched,
instead of failing mid-run on step 40 of 50.
"""
from __future__ import annotations

from src.actions import available_actions
from src.schema import ACTION_SCHEMA


def _validate_step(step: object, where: str, macro_names: set[str], errors: list[str]) -> None:
    if not isinstance(step, dict):
        errors.append(f"{where}: step must be a mapping, got {type(step).__name__}")
        return

    action_name = step.get("action")
    if not action_name:
        errors.append(f"{where}: step is missing an \"action\" key")
        return

    if action_name not in available_actions():
        errors.append(
            f"{where}: unknown action {action_name!r}. "
            f"Available actions: {', '.join(available_actions())}"
        )
        return

    if action_name == "run_macro":
        macro_name = step.get("name")
        if macro_name and macro_name not in macro_names:
            errors.append(f"{where}: run_macro references unknown macro {macro_name!r}")

    if action_name == "repeat":
        for i, nested in enumerate(step.get("steps", [])):
            _validate_step(nested, f"{where} -> repeat step {i + 1}", macro_names, errors)

    for field in ACTION_SCHEMA.get(action_name, []):
        if field.get("required") and field["name"] not in step:
            errors.append(f"{where}: {action_name!r} is missing required field {field['name']!r}")


def validate_config(config: dict) -> list[str]:
    """Returns a list of human-readable error strings; empty means valid."""
    errors: list[str] = []

    if not isinstance(config, dict):
        return [f"Config must be a mapping, got {type(config).__name__}"]

    macros = config.get("macros") or {}
    if not isinstance(macros, dict):
        errors.append("\"macros\" must be a mapping of name -> step list")
        macros = {}
    macro_names = set(macros)

    for name, steps in macros.items():
        if not isinstance(steps, list):
            errors.append(f"macro {name!r}: must be a list of steps")
            continue
        for i, step in enumerate(steps):
            _validate_step(step, f"macro {name!r} step {i + 1}", macro_names, errors)

    steps = config.get("steps") or []
    if not isinstance(steps, list):
        errors.append("\"steps\" must be a list")
        steps = []
    for i, step in enumerate(steps):
        _validate_step(step, f"step {i + 1}", macro_names, errors)

    return errors
