import json
import urllib.error

from src import update_check


def test_parse_version_handles_v_prefix():
    assert update_check._parse_version("v3.10.2") == (3, 10, 2)
    assert update_check._parse_version("3.10.2") == (3, 10, 2)


def test_parse_version_non_numeric_segment_becomes_zero():
    assert update_check._parse_version("v3.x.2") == (3, 0, 2)


class _FakeResponse:
    def __init__(self, payload: dict):
        self._body = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return self._body


def test_check_for_update_returns_none_when_already_current(monkeypatch):
    monkeypatch.setattr(
        update_check.urllib.request, "urlopen",
        lambda *a, **k: _FakeResponse({"tag_name": "v3.0.0", "html_url": "https://example.com"}),
    )
    assert update_check.check_for_update("3.0.0") is None


def test_check_for_update_returns_info_when_newer_available(monkeypatch):
    monkeypatch.setattr(
        update_check.urllib.request, "urlopen",
        lambda *a, **k: _FakeResponse({"tag_name": "v3.1.0", "html_url": "https://example.com/release"}),
    )
    result = update_check.check_for_update("3.0.0")
    assert result == {"version": "3.1.0", "url": "https://example.com/release"}


def test_check_for_update_returns_none_on_network_failure(monkeypatch):
    def raise_error(*args, **kwargs):
        raise urllib.error.URLError("no connection")

    monkeypatch.setattr(update_check.urllib.request, "urlopen", raise_error)
    assert update_check.check_for_update("3.0.0") is None


def test_check_for_update_returns_none_on_missing_tag_name(monkeypatch):
    monkeypatch.setattr(
        update_check.urllib.request, "urlopen",
        lambda *a, **k: _FakeResponse({}),
    )
    assert update_check.check_for_update("3.0.0") is None
