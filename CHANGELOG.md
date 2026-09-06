# Changelog

All notable changes to this project are documented here.

## [1.0.0] - 2026-09-07
First stable release - no functional changes since 0.3.0. The action
registry, GUI, config format, and packaging have held steady long enough
to commit to semantic versioning going forward: breaking changes to the
YAML config shape or the action registry's public surface will bump the
major version from here on.

## [0.3.0] - 2026-09-06
### Added
- About tab in the GUI: logo, project name/version, blurb, disclaimer text,
  a link to the repo, and a live `CHANGELOG.md` viewer with a Reload button.
  The existing recorder/editor UI now lives in its own "Automator" tab
  alongside it.
- First-launch disclaimer dialog (`gui/disclaimer.py`), shown before the
  main window until accepted; acceptance is persisted so it only shows once.
- Local GUI settings persistence (`automator/paths.py`, `automator/
  settings.py`): stored at `%APPDATA%\Automater\configs\settings.json`
  (Windows) / `~/.local/share/Automater/configs/settings.json` (Linux),
  deep-merged against defaults so older files backfill new keys. Currently
  persists the disclaimer acknowledgment, default browser channel/headless/
  profile dir, and the last config path used for Load/Save Config.
- `automator/metadata.py`: single source of truth for project name, repo
  URL, and disclaimer text, read by the About tab and disclaimer dialog.
- Packaging (`pyproject.toml`): pip-installable (`pip install -e .`), with
  the version read dynamically from `VERSION.md` so it never drifts from
  the release flow.
- Test suite (`tests/`, pytest + pytest-asyncio): 38 tests covering the
  action registry, `ACTION_SCHEMA`/registry consistency, browser
  default-detection, settings load/save/merge, and the GUI recorder's
  event-to-step mapping.
- GitHub Actions CI (`.github/workflows/ci.yml`), running the test suite on
  `windows-latest` (required by `automator/browser.py`'s use of `winreg`).
- `LICENSE.md`: GNU General Public License v3.0.

## [0.2.0] - 2026-09-06
### Added
- Desktop GUI (`gui_main.py`, PySide6 + qasync): records clicks/form input/
  navigation into steps live, a step editor (reorder, edit, delete, group
  selected steps into a macro), an "Add Action" dialog for step types the
  recorder can't capture, and Play/Pause/Stop playback with a log panel.
  Config load/save is fully interoperable with the CLI's YAML format.
- Browser default-detection (`automator/browser.py`): `browser.channel:
  default` reads the Windows default-browser registration and launches
  Brave/Chrome/Edge/Firefox accordingly; explicit channels and
  `executable_path` still override it.
- Per-step and global delays: `default_delay_ms` config option plus
  per-step `delay_before`/`delay_after` (ms).
- App icon/logo (`assets/icon.ico`, `assets/icon.png`, `assets/logo.png`),
  generated via `scripts/generate_icon.py`; wired into the GUI window icon.

## [0.1.0] - 2026-09-06
### Added
- Initial standalone Python + Playwright automation script for Stux.Group site QA/regression testing and own-data scraping.
- Extensible action registry (`automator/actions.py`): goto/reload/back/forward, click, dblclick, click_coords, hover, drag_and_drop, scroll, fill, type, press, check/uncheck, select_option, upload_file, wait_for_selector/url/load_state, sleep, screenshot, scrape, evaluate, assert (visible/hidden/text/url/count), log, repeat, run_macro.
- Named macros: reusable step groups referenced from `steps`, other macros, or hotkeys.
- Brave browser support via a persistent Playwright context (also works with plain Chrome or any Chromium executable).
- Global system-wide hotkeys (pause/resume, quit, or run an arbitrary list of steps), plus in-page simulated key presses via the `press` action.
- `${env:VAR_NAME}` substitution in config values, so credentials never need to live in the YAML file.
