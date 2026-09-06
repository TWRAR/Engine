# Changelog

All notable changes to this project are documented here.

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
