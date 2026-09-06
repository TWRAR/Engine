from gui.session import BrowserSession


def test_to_step_click_without_modifiers():
    step = BrowserSession._to_step({"type": "click", "selector": "#go"})
    assert step == {"action": "click", "selector": "#go"}


def test_to_step_click_with_modifiers():
    step = BrowserSession._to_step({"type": "click", "selector": "#go", "modifiers": ["Shift"]})
    assert step == {"action": "click", "selector": "#go", "modifiers": ["Shift"]}


def test_to_step_fill():
    step = BrowserSession._to_step({"type": "fill", "selector": "#name", "value": "leo"})
    assert step == {"action": "fill", "selector": "#name", "value": "leo"}


def test_to_step_check_and_uncheck():
    checked = BrowserSession._to_step({"type": "check", "selector": "#tos", "checked": True})
    unchecked = BrowserSession._to_step({"type": "check", "selector": "#tos", "checked": False})
    assert checked["action"] == "check"
    assert unchecked["action"] == "uncheck"


def test_to_step_unknown_type_returns_none():
    assert BrowserSession._to_step({"type": "unsupported"}) is None
