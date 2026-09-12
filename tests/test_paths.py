import importlib
import sys

from src import paths
from src.paths import APP_ROOT, CONFIGS_DIR, OUTPUT_DIR, PROFILES_DIR, USER_DATA_DIR


def test_user_data_dir_is_named_after_the_project():
    assert USER_DATA_DIR.name == "TWRAR"


def test_macos_uses_application_support(monkeypatch):
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.delenv("APPDATA", raising=False)
    try:
        importlib.reload(paths)
        assert paths.USER_DATA_DIR == paths.Path.home() / "Library" / "Application Support" / "TWRAR"
    finally:
        monkeypatch.undo()
        importlib.reload(paths)  # restore the real platform's USER_DATA_DIR for later tests


def test_configs_dir_is_created_under_user_data_dir():
    assert CONFIGS_DIR.parent == USER_DATA_DIR
    assert CONFIGS_DIR.exists()


def test_profiles_dir_is_created_under_user_data_dir():
    assert PROFILES_DIR.parent == USER_DATA_DIR
    assert PROFILES_DIR.exists()


def test_output_dir_is_created_under_user_data_dir():
    assert OUTPUT_DIR.parent == USER_DATA_DIR
    assert OUTPUT_DIR.exists()


def test_app_root_is_repo_root_when_not_frozen():
    assert (APP_ROOT / "VERSION.md").exists()
    assert (APP_ROOT / "assets" / "logo.png").exists()


def test_app_root_uses_meipass_when_frozen(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    try:
        importlib.reload(paths)
        assert paths.APP_ROOT == tmp_path
    finally:
        monkeypatch.undo()
        importlib.reload(paths)  # restore the real (non-frozen) APP_ROOT for later tests
