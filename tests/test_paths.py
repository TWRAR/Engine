from automator.paths import CONFIGS_DIR, USER_DATA_DIR


def test_user_data_dir_is_named_after_the_project():
    assert USER_DATA_DIR.name == "Automater"


def test_configs_dir_is_created_under_user_data_dir():
    assert CONFIGS_DIR.parent == USER_DATA_DIR
    assert CONFIGS_DIR.exists()
