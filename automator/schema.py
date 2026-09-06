"""Field schema per action, used by the GUI to build editor/add-action forms.

Kept separate from actions.py so the GUI can describe every action without
importing Playwright. Field `type` is one of: str, int, float, bool, choice, text.
"""
from __future__ import annotations

ACTION_SCHEMA: dict[str, list[dict]] = {
    "goto": [
        {"name": "url", "type": "str", "required": True},
        {"name": "wait_until", "type": "choice", "choices": ["load", "domcontentloaded", "networkidle", "commit"]},
    ],
    "reload": [
        {"name": "wait_until", "type": "choice", "choices": ["load", "domcontentloaded", "networkidle", "commit"]},
    ],
    "go_back": [],
    "go_forward": [],
    "click": [
        {"name": "selector", "type": "str", "required": True},
        {"name": "button", "type": "choice", "choices": ["left", "right", "middle"]},
        {"name": "click_count", "type": "int"},
        {"name": "timeout", "type": "int"},
        {"name": "force", "type": "bool"},
    ],
    "dblclick": [
        {"name": "selector", "type": "str", "required": True},
        {"name": "timeout", "type": "int"},
    ],
    "click_coords": [
        {"name": "x", "type": "int", "required": True},
        {"name": "y", "type": "int", "required": True},
        {"name": "button", "type": "choice", "choices": ["left", "right", "middle"]},
    ],
    "hover": [{"name": "selector", "type": "str", "required": True}],
    "drag_and_drop": [
        {"name": "source", "type": "str", "required": True},
        {"name": "target", "type": "str", "required": True},
    ],
    "scroll": [
        {"name": "selector", "type": "str"},
        {"name": "delta_x", "type": "int"},
        {"name": "delta_y", "type": "int"},
    ],
    "fill": [
        {"name": "selector", "type": "str", "required": True},
        {"name": "value", "type": "str", "required": True},
    ],
    "type": [
        {"name": "selector", "type": "str", "required": True},
        {"name": "value", "type": "str", "required": True},
        {"name": "delay", "type": "int"},
    ],
    "press": [
        {"name": "selector", "type": "str"},
        {"name": "keys", "type": "str", "required": True},
    ],
    "check": [{"name": "selector", "type": "str", "required": True}],
    "uncheck": [{"name": "selector", "type": "str", "required": True}],
    "select_option": [
        {"name": "selector", "type": "str", "required": True},
        {"name": "value", "type": "str", "required": True},
    ],
    "upload_file": [
        {"name": "selector", "type": "str", "required": True},
        {"name": "path", "type": "str", "required": True},
    ],
    "wait_for_selector": [
        {"name": "selector", "type": "str", "required": True},
        {"name": "state", "type": "choice", "choices": ["attached", "detached", "visible", "hidden"]},
        {"name": "timeout", "type": "int"},
    ],
    "wait_for_url": [
        {"name": "url", "type": "str", "required": True},
        {"name": "timeout", "type": "int"},
    ],
    "wait_for_load_state": [
        {"name": "state", "type": "choice", "choices": ["load", "domcontentloaded", "networkidle"]},
    ],
    "sleep": [{"name": "seconds", "type": "float", "required": True}],
    "screenshot": [
        {"name": "path", "type": "str", "required": True},
        {"name": "selector", "type": "str"},
        {"name": "full_page", "type": "bool"},
    ],
    "scrape": [
        {"name": "selector", "type": "str", "required": True},
        {"name": "attribute", "type": "str"},
        {"name": "multiple", "type": "bool"},
        {"name": "save_as", "type": "str", "required": True},
    ],
    "evaluate": [
        {"name": "script", "type": "text", "required": True},
        {"name": "save_as", "type": "str"},
    ],
    "assert": [
        {
            "name": "type",
            "type": "choice",
            "choices": ["visible", "hidden", "text_equals", "text_contains", "url_equals", "url_contains", "count_equals"],
            "required": True,
        },
        {"name": "selector", "type": "str"},
        {"name": "value", "type": "str"},
        {"name": "timeout", "type": "int"},
    ],
    "log": [{"name": "message", "type": "str"}],
    "repeat": [{"name": "times", "type": "int", "required": True}],
    "run_macro": [{"name": "name", "type": "str", "required": True}],
}
