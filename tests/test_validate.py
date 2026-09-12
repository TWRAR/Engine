from src.validate import validate_config


def test_valid_config_has_no_errors():
    config = {
        "steps": [
            {"action": "goto", "url": "https://example.com"},
            {"action": "click", "selector": "#go"},
        ],
    }
    assert validate_config(config) == []


def test_unknown_action_is_reported():
    config = {"steps": [{"action": "teleport"}]}
    errors = validate_config(config)
    assert len(errors) == 1
    assert "teleport" in errors[0]
    assert "unknown action" in errors[0]


def test_missing_required_field_is_reported():
    config = {"steps": [{"action": "click"}]}  # missing required "selector"
    errors = validate_config(config)
    assert any("selector" in e for e in errors)


def test_step_missing_action_key_is_reported():
    config = {"steps": [{"selector": "#go"}]}
    errors = validate_config(config)
    assert any("action" in e for e in errors)


def test_run_macro_unknown_reference_is_reported():
    config = {"steps": [{"action": "run_macro", "name": "does_not_exist"}]}
    errors = validate_config(config)
    assert any("does_not_exist" in e for e in errors)


def test_run_macro_known_reference_is_valid():
    config = {
        "macros": {"login": [{"action": "click", "selector": "#login"}]},
        "steps": [{"action": "run_macro", "name": "login"}],
    }
    assert validate_config(config) == []


def test_macro_step_errors_are_reported_with_macro_context():
    config = {"macros": {"broken": [{"action": "nope"}]}, "steps": []}
    errors = validate_config(config)
    assert any("macro 'broken'" in e for e in errors)


def test_repeat_nested_steps_are_validated():
    config = {"steps": [{"action": "repeat", "times": 2, "steps": [{"action": "nope"}]}]}
    errors = validate_config(config)
    assert any("nope" in e for e in errors)


def test_steps_not_a_list_is_reported():
    assert validate_config({"steps": "oops"}) != []


def test_macros_not_a_mapping_is_reported():
    assert validate_config({"macros": ["oops"], "steps": []}) != []
