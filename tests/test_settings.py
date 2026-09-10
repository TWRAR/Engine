import json

from twrar import settings


def test_load_settings_creates_file_with_defaults(tmp_path, monkeypatch):
    path = tmp_path / "settings.json"
    monkeypatch.setattr(settings, "SETTINGS_PATH", path)

    loaded = settings.load_settings()

    assert loaded == settings.DEFAULT_SETTINGS
    assert path.exists()
    assert json.loads(path.read_text(encoding="utf-8")) == settings.DEFAULT_SETTINGS


def test_load_settings_fills_in_missing_keys_from_partial_file(tmp_path, monkeypatch):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"default_headless": True}), encoding="utf-8")
    monkeypatch.setattr(settings, "SETTINGS_PATH", path)

    loaded = settings.load_settings()

    assert loaded["default_headless"] is True
    assert loaded["disclaimer_confirmed"] is False  # backfilled from defaults
    on_disk = json.loads(path.read_text(encoding="utf-8"))
    assert on_disk["disclaimer_confirmed"] is False


def test_load_settings_falls_back_to_defaults_on_corrupt_file(tmp_path, monkeypatch):
    path = tmp_path / "settings.json"
    path.write_text("not valid json{{{", encoding="utf-8")
    monkeypatch.setattr(settings, "SETTINGS_PATH", path)

    assert settings.load_settings() == settings.DEFAULT_SETTINGS


def test_save_settings_writes_exact_dict(tmp_path, monkeypatch):
    path = tmp_path / "settings.json"
    monkeypatch.setattr(settings, "SETTINGS_PATH", path)

    settings.save_settings({"foo": "bar"})

    assert json.loads(path.read_text(encoding="utf-8")) == {"foo": "bar"}


def test_confirm_disclaimer_only_touches_that_key(tmp_path, monkeypatch):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"default_headless": True, "disclaimer_confirmed": False}), encoding="utf-8")
    monkeypatch.setattr(settings, "SETTINGS_PATH", path)

    settings.confirm_disclaimer()

    on_disk = json.loads(path.read_text(encoding="utf-8"))
    assert on_disk == {"default_headless": True, "disclaimer_confirmed": True}
