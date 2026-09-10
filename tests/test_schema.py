from twrar.actions import available_actions
from twrar.schema import ACTION_SCHEMA

VALID_FIELD_TYPES = {"str", "int", "float", "bool", "choice", "text"}


def test_every_registered_action_has_a_schema_entry():
    missing = set(available_actions()) - set(ACTION_SCHEMA)
    assert not missing, f"Actions with no ACTION_SCHEMA entry: {sorted(missing)}"


def test_every_schema_entry_maps_to_a_registered_action():
    extra = set(ACTION_SCHEMA) - set(available_actions())
    assert not extra, f"ACTION_SCHEMA entries for unregistered actions: {sorted(extra)}"


def test_schema_fields_are_well_formed():
    for action_name, fields in ACTION_SCHEMA.items():
        for field in fields:
            assert "name" in field, f"{action_name}: field missing 'name'"
            assert field.get("type") in VALID_FIELD_TYPES, (
                f"{action_name}.{field.get('name')}: invalid type {field.get('type')!r}"
            )
            if field["type"] == "choice":
                assert field.get("choices"), f"{action_name}.{field['name']}: choice field needs 'choices'"
