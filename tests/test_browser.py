import pytest

from automator import browser


def test_find_first_returns_existing_path(tmp_path):
    exe = tmp_path / "brave.exe"
    exe.write_bytes(b"")
    assert browser._find_first([str(exe)]) == str(exe)


def test_find_first_falls_back_to_which(monkeypatch, tmp_path):
    missing = tmp_path / "does-not-exist.exe"
    monkeypatch.setattr(browser.shutil, "which", lambda name: "/usr/bin/found")
    assert browser._find_first([str(missing)], which_name="brave") == "/usr/bin/found"


def test_find_first_returns_none_when_nothing_found(monkeypatch, tmp_path):
    missing = tmp_path / "does-not-exist.exe"
    monkeypatch.setattr(browser.shutil, "which", lambda name: None)
    assert browser._find_first([str(missing)]) is None


def test_detect_default_browser_falls_back_when_registry_read_fails(monkeypatch):
    def raise_oserror(*args, **kwargs):
        raise OSError("registry key not found")

    monkeypatch.setattr(browser.winreg, "OpenKey", raise_oserror)
    monkeypatch.setattr(browser, "find_brave_executable", lambda: "C:/brave.exe")

    browser_type, path = browser.detect_default_browser()
    assert browser_type == "chromium"
    assert path == "C:/brave.exe"


def test_detect_default_browser_maps_known_progid(monkeypatch):
    class FakeKey:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    monkeypatch.setattr(browser.winreg, "OpenKey", lambda *a, **k: FakeKey())
    monkeypatch.setattr(browser.winreg, "QueryValueEx", lambda key, name: ("FirefoxURL-abc123", None))
    monkeypatch.setattr(browser, "_find_first", lambda paths, which_name=None: "C:/firefox.exe")

    browser_type, path = browser.detect_default_browser()
    assert browser_type == "firefox"
    assert path == "C:/firefox.exe"


def test_detect_default_browser_unrecognized_progid_falls_back_to_brave(monkeypatch):
    class FakeKey:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    monkeypatch.setattr(browser.winreg, "OpenKey", lambda *a, **k: FakeKey())
    monkeypatch.setattr(browser.winreg, "QueryValueEx", lambda key, name: ("OperaStable", None))
    monkeypatch.setattr(browser, "find_brave_executable", lambda: "C:/brave.exe")

    browser_type, path = browser.detect_default_browser()
    assert browser_type == "chromium"
    assert path == "C:/brave.exe"


async def test_launch_context_rejects_unknown_channel():
    with pytest.raises(RuntimeError, match="Unknown browser.channel"):
        await browser.launch_context(playwright=None, browser_cfg={"channel": "bogus"}, user_data_dir="/tmp/x")


async def test_launch_context_raises_when_executable_not_found(monkeypatch):
    monkeypatch.setitem(browser._CHANNEL_RESOLVERS, "brave", lambda: ("chromium", None))
    with pytest.raises(RuntimeError, match="Could not find an executable"):
        await browser.launch_context(playwright=None, browser_cfg={"channel": "brave"}, user_data_dir="/tmp/x")


async def test_launch_context_rejects_load_extension_on_firefox(monkeypatch):
    monkeypatch.setitem(browser._CHANNEL_RESOLVERS, "firefox", lambda: ("firefox", "C:/firefox.exe"))

    class FakeBrowserType:
        async def launch_persistent_context(self, **kwargs):
            raise AssertionError("should not be reached")

    class FakePlaywright:
        firefox = FakeBrowserType()

    with pytest.raises(RuntimeError, match="only supported for Chromium"):
        await browser.launch_context(
            playwright=FakePlaywright(),
            browser_cfg={"channel": "firefox", "load_extension": "C:/ext"},
            user_data_dir="/tmp/x",
        )
